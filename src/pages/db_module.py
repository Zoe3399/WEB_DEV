from sqlalchemy import create_engine  # type: ignore
import duckdb  # type: ignore

DB_URI = "postgresql://streamlit_admin:root1234%40@pg-353kr8.vpc-pub-cdb-kr.ntruss.com:5432/streamlit_db"
DUCKDB_PATH = "./data_csv/mydb.duckdb"

# DuckDB 연결 함수
def get_duckdb_conn(db_path=DUCKDB_PATH):
    return duckdb.connect(db_path)

# PostgreSQL 엔진 객체 (모든 코드에서 바로 import 가능)
engine = create_engine(DB_URI)