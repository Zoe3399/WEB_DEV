import pandas as pd
import random
from sqlalchemy import text
from db_module import engine

sigungu_list = ['강남구', '송파구', '용산구', '마포구', '서초구', '노원구', '은평구', '광진구', '구로구', '동작구']
law_code_list = ['11230', '11040', '11440', '11650', '11350', '11170', '11380', '11215', '11530', '11590']
accident_type_list = ['전체', '중상사고', '경상사고']
acc_type_detail_list = ['차대사람', '차대차', '기타']
road_type_list = ['교차로', '직선도로', '굴다리', '곡선도로']
region_risk_list = [0, 1, 2]
years = [2021, 2022, 2023]

dummy_data = []
for i in range(200):
    idx = i % 10
    year = random.choice(years)
    sigungu = sigungu_list[idx]
    law_code = law_code_list[idx]
    accident_type = random.choice(accident_type_list)
    death_cnt = random.randint(0, 5)
    severe_cnt = random.randint(0, 10)
    minor_cnt = random.randint(0, 20)
    report_cnt = random.randint(0, 5)
    acc_type_detail = random.choice(acc_type_detail_list)
    road_type = random.choice(road_type_list)
    risk_score = round(random.uniform(10, 90), 1)
    region_risk = random.choice(region_risk_list)
    avg_accident = round(random.uniform(5, 30), 2)

    dummy_data.append({
        "year": year,
        "sigungu": sigungu,
        "law_code": law_code,
        "accident_type": accident_type,
        "death_cnt": death_cnt,
        "severe_cnt": severe_cnt,
        "minor_cnt": minor_cnt,
        "report_cnt": report_cnt,
        "acc_type_detail": acc_type_detail,
        "road_type": road_type,
        "risk_score": risk_score,
        "region_risk": region_risk,
        "avg_accident": avg_accident
    })

df = pd.DataFrame(dummy_data)

insert_sql = """
INSERT INTO accident_prediction (
    year, sigungu, law_code, accident_type, death_cnt, severe_cnt, minor_cnt, report_cnt,
    acc_type_detail, road_type, risk_score, region_risk, avg_accident
) VALUES (
    :year, :sigungu, :law_code, :accident_type, :death_cnt, :severe_cnt, :minor_cnt, :report_cnt,
    :acc_type_detail, :road_type, :risk_score, :region_risk, :avg_accident
)
ON CONFLICT (year, law_code, accident_type) DO NOTHING
"""

with engine.begin() as conn:
    for _, row in df.iterrows():
        conn.execute(text(insert_sql), row.to_dict())

print("accident_prediction 테이블에 더미데이터 200개 입력 완료!")