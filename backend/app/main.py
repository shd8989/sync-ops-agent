import os

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
    allow_origins=["*"],  # TODO. 실무 환경에서는 구체적인 프론트 주소로 제한 권장 (e.g., http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 메타정보 응답 모델
class DBConnectionInfo(BaseModel):
    key: str      # 예: DB_DEV_MYSQL
    driver: str   # 예: mysql, postgresql, oracle

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

@app.get("/api/schema/databases", response_model=list[DBConnectionInfo])
async def get_available_databases():
    """
    환경변수에서 DB_로 시작하는 설정을 찾아 활성화된 DB 환경 리스트를 반환합니다.
    """
    available_dbs = []
    
    for key, value in os.environ.items():
        if key.startswith("DB_"):
            # 커넥션 스트링 문자열 분석을 통해 대략적인 드라이버 판별
            driver_type = "unknown"
            lower_val = value.lower()
            
            if "mysql" in lower_val or "mariadb" in lower_val:
                driver_type = "mysql"
            elif "postgresql" in lower_val or "postgres" in lower_val:
                driver_type = "postgresql"
            elif "oracle" in lower_val or "thin" in lower_val:
                driver_type = "oracle"
                
            # 프론트엔드 렌더링을 위해 키와 감지된 드라이버 타입 매핑
            available_dbs.append({
                "key": key,
                "driver": driver_type
            })
            
    return available_dbs

# 기존에 연결하려던 스키마 비교 트리거 API 예시
@app.get("/api/schema/compare")
async def compare_schema(driver: str, source: str, target: str):
    # 백엔드 내부적으로 os.environ.get(source), os.environ.get(target) 로 
    # 실제 커넥션 정보를 가져와 안전하게 스킬(check_schema_tool) 등을 호출할 수 있습니다.
    # ... 후속 로직 구현 ...
    return {"status": "success", "detail": f"{source}와 {target} 비교 완료"}

if __name__ == "__main__":
    import uvicorn
    # 기존 "main.py:app" 대신 모듈 경로 체계인 "app.main:app"으로 변경합니다.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)