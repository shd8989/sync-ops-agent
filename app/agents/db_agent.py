import os
from typing import Annotated, TypedDict, Literal
# 1. OpenAI 대신 Google GenAI 클래스 임포트
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# 스킬(Tools) 가져오기
from app.skills.check_schema import check_schema_tool
from app.skills.data_sync import data_sync_tool
from app.skills.graph_map import graph_map_tool

# 에이전트 상태(State) 정의
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 에이전트가 사용할 스킬 셋 바인딩
tools = [check_schema_tool, data_sync_tool, graph_map_tool]
tool_node = ToolNode(tools)

# 2. LLM 모델을 Gemini로 변경
# 기본적으로 많이 쓰이는 'gemini-1.5-pro' 또는 속도가 빠른 'gemini-1.5-flash'를 추천합니다.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", 
    temperature=0,
    convert_system_message_to_human=True # 시스템 프롬프트 호환성을 위한 옵션
).bind_tools(tools)

# 시스템 프롬프트 로드
def load_system_prompt() -> str:
    return (
        "당신은 데이터베이스 전문가 'SyncOps Agent'입니다.\n"
        "Oracle, MySQL, PostgreSQL 간의 스키마 비교 및 데이터 이관 작업을 보조합니다.\n"
        "사용자가 요청하면 보유한 스킬(Tools)들을 적절히 활용하여 문제를 해결하고,\n"
        "진행 상황이나 분석 리포트를 명확한 마크다운 테이블이나 구조로 설명하세요."
    )

# 노드 비즈니스 로직 정의
async def call_model(state: AgentState):
    messages = state['messages']
    
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        messages = [HumanMessage(content=load_system_prompt())] + messages
        
    response = await llm.ainvoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

# LangGraph 워크플로우 그래프 빌드
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
workflow.add_edge("tools", "agent")

agent_graph = workflow.compile()

# FastAPI 스트리밍 제너레이터 함수
async def run_db_agent(user_message: str):
    inputs = {"messages": [HumanMessage(content=user_message)]}
    
    async for event in agent_graph.astream_events(inputs, version="v2"):
        kind = event["event"]
        
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield {"type": "token", "content": content}
                
        elif kind == "on_tool_start":
            yield {"type": "tool_start", "tool_name": event["name"], "inputs": event["data"].get("input")}
            
        elif kind == "on_tool_end":
            yield {"type": "tool_end", "tool_name": event["name"], "output": str(event["data"].get("output"))}