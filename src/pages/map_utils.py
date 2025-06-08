import folium
from shapely.geometry import shape, Point

# 위험등급별 색상 맵
RISK_COLOR = {
    0: "#FF4D4D",   # 고위험(빨강)
    1: "#FFB94D",   # 중위험(주황)
    2: "#53C653",   # 저위험(초록)
}

def get_risk_color(level):
    """
    위험등급 정수 → 색상코드(str) 반환
    """
    return RISK_COLOR.get(level, "#DDDDDD")

def style_polygon(feature, df, name_key="SIG_KOR_NM", risk_col="region_risk"):
    """
    폴리곤의 색상을 설정하기 위한 스타일 반환
    """
    region_name = feature['properties'].get(name_key, "").strip()
    row = df[df["region_name"] == region_name]
    if not row.empty:
        risk = int(row.iloc[0][risk_col])
        color = get_risk_color(risk)
    else:
        color = "#EEEEEE"  # 데이터가 없으면 회색
    return {
        "fillColor": color,
        "color": "#CCCCCC",  # 테두리는 연한 회색
        "weight": 1,
        "fillOpacity": 0.5,  # 투명도 설정
    }

def highlight_style():
    """
    폴리곤 클릭 시 강조 스타일
    """
    return {
        "color": "#111111",   # 클릭된 폴리곤 테두리 색
        "weight": 5,           # 테두리 두께
        "fillOpacity": 0.28,   # 테두리 클릭 시 투명도
    }

def get_polygon_tooltip():
    """
    GeoJsonTooltip 반환 (지역명만 표시)
    """
    return folium.GeoJsonTooltip(
        fields=["SIG_KOR_NM"],
        aliases=["지역:"],
        sticky=True,
        style=("background-color: rgba(30,30,30,0.8); color: white; "
"border-radius:6px; padding: 6px; font-size: 1.1em;"),
        localize=True
    )

def find_region_by_coordinate(lat, lon, geojson):
    """
    클릭한 좌표가 포함된 geojson의 지역명을 반환
    """
    point = Point(lon, lat)
    for feature in geojson.get("features", []):
        polygon = shape(feature.get("geometry"))
        if polygon.contains(point):
            return feature["properties"].get("SIG_KOR_NM")
    return None
