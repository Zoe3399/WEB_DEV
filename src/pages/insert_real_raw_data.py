import os
import pandas as pd
from sqlalchemy import create_engine

DB_URI = "postgresql://streamlit_admin:root1234%40@pg-353kr8.vpc-pub-cdb-kr.ntruss.com:5432/streamlit_db"
engine = create_engine(DB_URI)

# 데이터 파일 경로
file1 = 'preprocessed_data/시도_시군구별_보행자_사고_사고유형_전처리ver.csv'
file2 = 'preprocessed_data/시도_시군구_시간대별_노인교통사고_전처리ver.csv'

try:
    # 파일 존재 체크
    if not (os.path.exists(file1) and os.path.exists(file2)):
        print("❌ 데이터 파일이 존재하지 않습니다. 파일 위치 또는 이름을 확인하세요.")
        exit()

    # 1. 주요 사고/사망/중상자수 정보
    df1 = pd.read_csv(file1)
    # 2. 시간대, 도로형태 등 추가 정보
    df2 = pd.read_csv(file2)

    # 3. 필요시 LEFT JOIN 등으로 병합
    df_merge = pd.merge(
        df1,
        df2,
        left_on=['연도', '시군구명', '법정동코드'],
        right_on=['연도', '시군구명', '법정동코드'],
        how='left'
    )

    # 4. DB 테이블 컬럼에 맞게 가공 (아까 예시 코드 참고)
    df_db = pd.DataFrame()
    df_db["YEAR"] = df_merge["연도"]
    df_db["SIGUNGU"] = df_merge["시군구명"]
    df_db["LAW_CODE"] = df_merge["법정동코드"]
    df_db["ACCIDENT_DESC"] = df_merge.get("사고내용", None)
    df_db["DEATH_CNT"] = df_merge.get("사망자수", None)
    df_db["SEVERE_CNT"] = df_merge.get("중상자수", None)
    df_db["MINOR_CNT"] = df_merge.get("경상자수", None)
    # ... 나머지 컬럼도 동일하게 추출/가공

    df_db.to_sql('accident_raw', engine, if_exists='append', index=False)

    print("✅ 여러 파일 조합으로 ACCIDENT_RAW 적재 완료!")

except Exception as e:
    print(f"❌ 데이터 적재 중 오류 발생: {e}")