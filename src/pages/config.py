# DB 연결 정보 (PostgreSQL)
DB_URI = "postgresql://postgres:1234@localhost:5432/postgres"

# DuckDB 파일 경로 (로컬 개발 시)
DUCKDB_PATH = "./data_csv/mydb.duckdb"

# 위험도 색상 매핑 (고중저 3단계)
RISK_LEVEL_COLOR = {
    "저": "#4caf50",      # 초록 (Low)
    "중": "#ffc107",      # 주황 (Medium)
    "고": "#f44336",      # 빨강 (High)
}

# 위험도 라벨 매핑 (영문 병기)
RISK_LEVEL_LABEL = {
    "저": "Low",
    "중": "Medium",
    "고": "High",
}

# 데이터 파일 기본 경로
DATA_PATH = "./data_csv/"

# 엑셀/CSV 업로드 허용 확장자
ALLOWED_EXTENSIONS = ["csv", "xlsx", "xls"]