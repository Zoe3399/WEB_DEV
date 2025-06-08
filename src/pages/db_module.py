# db_module.py
from sqlalchemy import create_engine # type: ignore
import duckdb # type: ignore

DB_URI = "postgresql://streamlit_admin:root1234%40@pg-353kr8.vpc-pub-cdb-kr.ntruss.com:5432/streamlit_db"
engine = create_engine(DB_URI, echo=False)

# DuckDB 파일 경로 (config 등에서 import해도 됨)
DUCKDB_PATH = "./data_csv/mydb.duckdb"

# DuckDB 연결 함수
def get_duckdb_conn(db_path=DUCKDB_PATH):
    """
    DuckDB 데이터베이스에 연결해 커넥션 객체 반환
    :param db_path: DuckDB 파일 경로
    :return: duckdb.Connection 객체
    """
    return duckdb.connect(db_path)