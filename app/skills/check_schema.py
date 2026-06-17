from langchain_core.tools import tool
from sqlalchemy import create_engine, inspect
import json

@tool
def check_schema_tool(db_type: str, connection_string: str) -> str:
    """
    지정된 데이터베이스의 테이블 및 컬럼 스키마 정보를 추출하는 스킬.
    - db_type: 'mysql', 'postgresql', 'oracle' 중 하나
    - connection_string: DB 접속 정보 URL (e.g., 'mysql+pymysql://user:pwd@localhost:3306/db')
    """
    try:
        # 1. DB 연결 커넥션 생성
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        schema_summary = {}
        
        # 2. 모든 테이블명 가져오기
        table_names = inspector.get_table_names()
        
        for table in table_names:
            schema_summary[table] = []
            # 3. 각 테이블의 컬럼 정보(이름, 타입, Null 여부) 추출
            columns = inspector.get_columns(table)
            for col in columns:
                schema_summary[table].append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                })
        
        # 4. 분석된 결과를 JSON 문자열로 반환 (에이전트가 이 맥락을 읽고 대조 보고서를 작성함)
        return json.dumps(schema_summary, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"DB 스키마 추출 중 오류 발생: {str(e)}"