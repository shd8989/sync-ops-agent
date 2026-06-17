# app/agents/db_agent.py
import os
from typing import Annotated, TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# 임시 스킬(Tools) 가져오기 - 추후 실제 skills/*.py 구현체로 교체됩니다.
from app.skills.check_schema import check_schema_tool
from app.skills.data_sync import data_sync_tool
from app.skills.graph_map import graph_map_tool

# 1. 에이전트 상태(State) 정의
class AgentState(TypedDict):
    # add_messages는 새로운 메시지가 올 때 기존 대화 기록에 누적(Append)해주는 헬퍼 함수입니다.
    messages: Annotated[list[BaseMessage], add_messages]

# 2. 에이전트가 사용할 스킬 셋 바인딩
tools = [check_schema_tool, data_sync_tool, graph_map_tool]
tool_node = ToolNode(tools)

# 3. LLM 모델 설정 및 스킬 연결
# 환경 변수에 OPENAI_API_KEY가 세팅되어 있어야 합니다.
llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

# 시스템 프롬프트 로드 (참조 레포의 /prompts 스타일 반영)
def load_system_prompt() -> str:
    # 추후 prompts/ 내 마크다운 파일들을 동적으로 읽어오도록 확장 가능합니다.
    return (
        "당신은 데이터베이스 전문가 'SyncOps Agent'입니다.\n"
        "Oracle, MySQL, PostgreSQL 간의 스키마 비교 및 데이터 이관 작업을 보조합니다.\n"
        "사용자가 요청하면 보유한 스킬(Tools)들을 적절히 활용하여 문제를 해결하고,\n"
        "진행 상황이나 분석 리포트를 명확한 마크다운 테이블이나 구조로 설명하세요."
    )

# 4. 노드 비즈니스 로직 정의
async def call_model(state: AgentState):
    """LLM이 현재 대화 맥락을 보고 다음 행동(스킬 호출 또는 답변)을 결정하는 노드"""
    messages = state['messages']
    
    # 첫 대화라면 시스템 프롬프트를 맨 앞에 주입
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        messages = [HumanMessage(content=load_system_prompt())] + messages
        
    response = await llm.ainvoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    """LLM의 결과물에 스킬 호출(tool_calls)이 포함되어 있는지 판단하는 조건부 라우터"""
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

# 5. LangGraph 워크플로우 그래프 빌드
workflow = StateGraph(AgentState)

# 노드 등록
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# 엣지 연결 (진입점 설정 및 루프 구조 정의)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "__end__": END
    }
)
workflow.add_edge("tools", "agent") # 스킬 수행 후 다시 에이전트의 판단을 받음

# 그래프 컴파일
agent_graph = workflow.compile()

# 6. FastAPI 엔드포인트에서 호출할 비동기 스트리밍 제너레이터 함수
async def run_db_agent(user_message: str):
    """사용자 메시지를 받아 LangGraph의 진행 상태를 실시간 이벤트로 yield 합니다."""
    inputs = {"messages": [HumanMessage(content=user_message)]}
    
    # astream_events 프로토콜을 사용해 에이전트의 생각 및 툴 실행 상태를 낚아챕니다.
    async for event in agent_graph.astream_events(inputs, version="v2"):
        kind = event["event"]
        
        # LLM이 답변 토큰을 실시간으로 뱉을 때 (채팅창 스트리밍용)
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield {"type": "token", "content": content}
                
        # 에이전트가 특정 스킬(Tool)을 실행하기 시작했을 때
        elif kind == "on_tool_start":
            yield {"type": "tool_start", "tool_name": event["name"], "inputs": event["data"].get("input")}
            
        # 스킬 실행이 완료되어 결과 데이터가 나왔을 때
        elif kind == "on_tool_end":
            yield {"type": "tool_end", "tool_name": event["name"], "output": str(event["data"].get("output"))}