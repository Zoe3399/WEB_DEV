from sqlalchemy import create_engine, text

DB_URI = "postgresql://postgres:1234@127.0.0.1:5432/postgres"
engine = create_engine(DB_URI, echo=True)

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))  # text로 감싸기
    print(result.fetchall())
