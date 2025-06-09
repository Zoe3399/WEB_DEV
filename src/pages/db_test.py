import psycopg2

try:
    conn = psycopg2.connect(
        host="pg-353kr8.vpc-pub-cdb-kr.ntruss.com",
        port=5432,
        dbname="streamlit_db",
        user="streamlit_admin",
        password="root1234@"
    )
    print("✅ 연결 성공")
    conn.close()
except Exception as e:
    print("❌ 연결 실패:", e)