import random
import pandas as pd

dummy_list = []
지역목록 = ['강남구', '마포구', '용산구', '서초구', '송파구', '노원구', '중구', '은평구', '관악구', '동작구']  # 예시 10개

for i in range(200):
    region = random.choice(지역목록)
    year = random.choice([2021, 2022, 2023])
    # 사망자/중상자/경상자(무작위)
    death = random.randint(0, 5)
    severe = random.randint(1, 12)
    minor = random.randint(3, 35)
    accident_count = death + severe + minor
    risk_score = round(random.uniform(20, 60), 1)
    region_risk = random.choice([0, 1, 2])
    region_code = 11000 + 지역목록.index(region) * 10  # 예시 코드
    lat, lon = round(random.uniform(37.45, 37.70), 5), round(random.uniform(126.80, 127.15), 5)

    dummy_list.append({
        "region": region,
        "year": year,
        "region_code": region_code,
        "accident_count": accident_count,
        "death": death,
        "severe": severe,
        "minor": minor,
        "risk_score": risk_score,
        "region_risk": region_risk,
        "lat": lat,
        "lon": lon,
    })

df = pd.DataFrame(dummy_list)
df.to_csv("더미_사고통계.csv", index=False, encoding="utf-8-sig")
print("생성 완료! (더미_사고통계.csv)")