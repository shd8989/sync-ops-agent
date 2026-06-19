import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

DB_CONFIGS = {
    "oracle_11g": {
        "user": os.getenv("ORACLE_11G_USER"),
        "password": os.getenv("ORACLE_11G_PASSWORD"),
        "dsn": os.getenv("ORACLE_11G_DSN", "localhost:1521/orcl11g")
    },
    "oracle_19c": {
        "user": os.getenv("ORACLE_19C_USER", "user19"),
        "password": os.getenv("ORACLE_19C_PASSWORD", "pass19"),
        "dsn": os.getenv("ORACLE_19C_DSN", "localhost:1522/orcl19c")
    },
    "db_postgres14": {
        "user": os.getenv("ORACLE_19C_USER"),
        "password": os.getenv("ORACLE_19C_PASSWORD"),
        "host": os.getenv("ORACLE_19C_PASSWORD"),
        "port": os.getenv("ORACLE_19C_PASSWORD"),
        "database": os.getenv("ORACLE_19C_PASSWORD")
    }
}