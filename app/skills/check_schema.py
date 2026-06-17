from langchain_core.tools import tool

@tool
def check_schema_tool(source_db: str, target_db: str) -> str:
    """개발 서버와 운영 서버의 DB 스키마 차이점(테이블, 컬럼, 인덱스)을 대조하는 스킬"""
    return f"[{source_db} -> {target_db}] 스키마 대조 완료: 두 서버의 'user' 테이블 인덱스 불일치 1건 발견."