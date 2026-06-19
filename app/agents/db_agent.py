import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
#from config import DB_CONFIGS

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

# .env 파일 로드
load_dotenv()

# 에이전트 상태(State) 정의
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 에이전트가 사용할 스킬 셋 바인딩
tools = [check_schema_tool, data_sync_tool, graph_map_tool]
tool_node = ToolNode(tools)

# 2. LLM 모델을 Gemini로 변경
# 기본적으로 많이 쓰이는 'gemini-1.5-pro' 또는 속도가 빠른 'gemini-1.5-flash'를 추천합니다.
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash", 
    temperature=0,
    convert_system_message_to_human=True # 시스템 프롬프트 호환성을 위한 옵션
).bind_tools(tools)

# 시스템 프롬프트 로드
def load_system_prompt() -> str:
    db_connections = ""
    for key, value in os.environ.items():
        if key.startswith("DB_"):
            print(f"[{key}] 연결 시도 중...")
            try:
                # 커넥션 스트링을 그대로 넘겨서 엔진 생성 (타임아웃 3초 설정)
                engine = create_engine(value, connect_args={"connect_timeout": 3} if "postgres" in value or "mysql" in value else {})
                
                with engine.connect() as connection:
                    # 각 DB 공통으로 작동하는 표준 SQL 테스트
                    connection.execute(text("SELECT 1"))
                print(f"[{key}] 연결 성공!")
            except Exception as e:
                print(f"[{key}] 연결 실패: {e}")
            
            db_connections += f"- {key}: {value}\n"

    prompt = ("당신은 데이터베이스 전문가 'SyncOps Agent'입니다.\n"
        "현재 관리 중인 인프라의 DB 접속 정보(Connection String) 리스트는 다음과 같습니다:\n\n"
        f"{db_connections}\n"
        "사용자가 특정 서버나 버전에 대한 스키마, 테이블 조회를 요청하면, "
        "위 접속 정보 중에서 매칭되는 알맞은 connection_string을 찾아 "
        "스킬(check_schema_tool)의 파라미터에 스스로 입력하고 호출하세요.\n"
        "만약 동일한 종류의 DB(예: Oracle 11g, 19c)가 여러 개 있다면, 사용자가 명시한 버전에 맞는 key의 주소를 정확히 매칭해야 합니다."
    )
    return prompt

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