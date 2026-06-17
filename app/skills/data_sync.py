from langchain_core.tools import tool

@tool
def data_sync_tool(table_name: str, scope: str) -> str:
    """마스터 데이터 전체 또는 일반 데이터 일부(최근 1달/10% 사이즈)를 선택 이관하는 스킬"""
    return f"'{table_name}' 테이블 데이터를 [{scope}] 조건으로 안전하게 마이그레이션 완료했습니다."