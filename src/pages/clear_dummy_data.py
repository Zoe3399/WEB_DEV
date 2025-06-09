from sqlalchemy import text
from db_module import engine

def clear_table(table_name):
    """테이블 전체 데이터 삭제"""
    with engine.connect() as conn:
        try:
            conn.execute(text(f"DELETE FROM {table_name};"))
            conn.commit()
            print(f"{table_name}: 데이터 전체 삭제 성공")
        except Exception as e:
            print(f"{table_name}: 데이터 삭제 실패 - {e}")

# 삭제할 테이블명 리스트
target_tables = [
    "accident_raw",
    "accident_prediction",
    "accident_summary",
    "users",
    "user_roles",
    "region_info",
    "user_favorite_region",
    "safety_tip",
    "download_log",
    "report_file",
    "admin_log",
    "user_log",
    "error_log"
]

if __name__ == "__main__":
    for tbl in target_tables:
        clear_table(tbl)
    print("모든 테이블 데이터 삭제 시도 완료!")