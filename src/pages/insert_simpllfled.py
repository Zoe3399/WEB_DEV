import json
import pandas as pd
from shapely.geometry import shape
from sqlalchemy import create_engine

# DB 연결
DB_URI = "postgresql://postgres:1234@127.0.0.1:5432/postgres"
engine = create_engine(DB_URI, echo=False)

# GeoJSON 파일 경로
geojson_path = "./data/법정구역_시군구.geojson"

with open(geojson_path, encoding="utf-8") as f:
    gj = json.load(f)

rows = []
for feat in gj["features"]:
    props = feat.get("properties", {})
    region_code = props.get("code")
    region_name = props.get("name")
    parent_code = props.get("parent")
    # properties가 없거나 region_code, region_name이 없으면 건너뜀
    if not region_code or not region_name:
        continue

    # 중심좌표 계산
    geom = shape(feat["geometry"])
    centroid = geom.centroid
    latitude = centroid.y
    longitude = centroid.x

    rows.append({
        "region_code": region_code,
        "region_name": region_name,
        "parent_code": parent_code,
        "latitude": latitude,
        "longitude": longitude,
    })

df = pd.DataFrame(rows)

# DB INSERT
with engine.connect() as conn:
    df.to_sql("region_info", conn, if_exists="append", index=False)
print("DB region_info 테이블에 데이터 입력 완료")
