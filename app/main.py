from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.agents.db_agent import run_db_agent
import json

app = FastAPI(
    title="SyncOps Agent Backend",
    description="DB Schema Analysis & Data Migration AI Agent",
    version="1.0.0"
)

# React 프론트엔드 연동을 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실무 환경에서는 구체적인 프론트 주소로 제한 권장 (e.g., http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
async def health_check():
    """서버 상태 확인용 헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "sync-ops-agent"}

@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    """
    AI 에이전트와 대화하는 엔드포인트
    LangGraph의 실행 과정을 Server-Sent Events(SSE) 스트리밍으로 프론트에 전달합니다.
    """
    try:
        async def event_generator():
            # db_agent에 작성된 비동기 제너레이터 호출
            async for event in run_db_agent(request.message):
                # 프론트엔드가 파싱하기 쉽도록 JSON 구조로 패킹하여 SSE 포맷으로 송신
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 기존 "main.py:app" 대신 모듈 경로 체계인 "app.main:app"으로 변경합니다.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)