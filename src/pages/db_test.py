from sqlalchemy import create_engine
import pandas as pd

# 네이버 클라우드 PostgreSQL DB URI (비밀번호 @ → %40 인코딩 주의!)
DB_URI = "postgresql+psycopg2://streamlit_admin:root1234%40@pg-353kr8.vpc-pub-cdb-kr.ntruss.com:5432/streamlit_db"

try:
    # 엔진 생성
    engine = create_engine(DB_URI)

    # 간단한 쿼리 실행 (DB 연결 확인)
    df = pd.read_sql("SELECT 1;", engine)
    print("✅ SQLAlchemy 연결 성공")
    print(df)
except Exception as e:
    print("❌ 연결 실패:", e)