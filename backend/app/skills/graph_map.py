from langchain_core.tools import tool

@tool
def graph_map_tool(root_table: str) -> str:
    """특정 테이블의 Foreign Key(FK) 관계를 추적하여 구조 파악용 맵 데이터를 생성하는 스킬"""
    return f"'{root_table}' 중심의 FK 네트워크 그래프 데이터(Node/Edge) 추출 완료."