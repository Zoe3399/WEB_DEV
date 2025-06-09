import pandas as pd
from db_module import engine

# -------------------------
# 1. 사고 원본(raw) 데이터 저장
# -------------------------
def insert_accident_raw(df: pd.DataFrame, if_exists="append"):
    """
    ACCIDENT_RAW 테이블에 데이터프레임 저장
    - df: 저장할 데이터프레임 (컬럼명/데이터 타입 반드시 DB와 일치!)
    - if_exists: 'append'는 데이터 추가, 'replace'는 테이블 덮어쓰기
    """
    if df is None or len(df) == 0:
        return
    try:
        # 예: ID는 SERIAL이므로 df에서 빼고 저장해야 오류 없음
        if "ID" in df.columns:
            df = df.drop(columns=["ID"])
        df.to_sql('accident_raw', engine, if_exists=if_exists, index=False)
        print("[ACCIDENT_RAW] 적재 성공")
    except Exception as e:
        print(f"[ACCIDENT_RAW] 적재 오류: {e}")

# -------------------------
# 2. 예측 결과 데이터 저장
# -------------------------
def insert_prediction(df: pd.DataFrame, if_exists="append"):
    """
    ACCIDENT_PREDICTION 테이블에 예측 데이터 저장
    - df: 모델 예측 결과 데이터프레임
    - if_exists: 'append' (기본) 또는 'replace'
    """
    if df is None or len(df) == 0:
        return
    try:
        df.to_sql('accident_prediction', engine, if_exists=if_exists, index=False)
        print("[ACCIDENT_PREDICTION] 적재 성공")
    except Exception as e:
        print(f"[ACCIDENT_PREDICTION] 적재 오류: {e}")

# -------------------------
# 3. 사고 요약 데이터 저장
# -------------------------
def insert_summary(df: pd.DataFrame, if_exists="append"):
    """
    ACCIDENT_SUMMARY 테이블에 요약 데이터 저장
    - df: 월별/시간대별 요약 데이터프레임
    - if_exists: 'append' 또는 'replace'
    """
    if df is None or len(df) == 0:
        return
    try:
        # 예: ID는 SERIAL로 자동생성, df에서 ID 컬럼 있으면 삭제 후 저장
        if "ID" in df.columns:
            df = df.drop(columns=["ID"])
        df.to_sql('accident_summary', engine, if_exists=if_exists, index=False)
        print("[ACCIDENT_SUMMARY] 적재 성공")
    except Exception as e:
        print(f"[ACCIDENT_SUMMARY] 적재 오류: {e}")

# -------------------------
# 4. 필요시 다른 테이블 함수도 추가
# -------------------------
# 예: 사용자 데이터, 지역정보 등 필요시 추가

# -------------------------
# [사용 예시]
# -------------------------
# from insert_db_utils import insert_accident_raw, insert_prediction, insert_summary
# df_raw = pd.read_csv("preprocessed_data/accident_raw.csv")
# insert_accident_raw(df_raw)
# df_pred = ... # 모델 예측 결과 DataFrame
# insert_prediction(df_pred)
# df_sum = ... # 사고 요약 DataFrame
# insert_summary(df_sum)