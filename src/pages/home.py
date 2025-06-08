import streamlit as st
import pandas as pd
import folium
import json
from streamlit_folium import st_folium
from sidebar import sidebar_menu
from db_module import engine
from map_utils import style_polygon, highlight_style, get_polygon_tooltip, find_region_by_coordinate

def show_home():
    st.set_page_config(page_title="고령자 교통사고 발생 위험도 예측", layout="wide")

    st.markdown("""
    <div style='display:flex;align-items:center;margin-bottom:18px;'>
        <span style='font-size:1.45em;font-weight:700;'>🚦 고령자 교통사고 발생 위험도 예측</span>
    </div>
    """, unsafe_allow_html=True)

    sidebar_menu()

    @st.cache_data
    def load_data():
        query = """
            SELECT r.region_code, r.region_name, r.latitude, r.longitude,
                a.region_risk, a.risk_score, a.death_cnt, a.severe_cnt, a.minor_cnt, a.year
            FROM region_info r
            LEFT JOIN accident_prediction a ON r.region_code = a.law_code
            WHERE a.region_risk IN (0,1,2)
        """
        df = pd.read_sql(query, engine)
        df["region_name"] = df["region_name"].str.strip()
        return df

    @st.cache_data
    def load_geojson():
        with open('./data/법정구역_시군구_simplified.geojson', encoding='utf-8') as f:
            geojson = json.load(f)
        return geojson

    @st.cache_data
    def load_monthly_summary(region_code):
        query = f"""
            SELECT month, SUM(accident_count) as accident_count
            FROM accident_summary
            WHERE region_code='{region_code}'
            GROUP BY month
            ORDER BY month
        """
        return pd.read_sql(query, engine)

    @st.cache_data
    def load_hourly_summary(region_code):
        query = f"""
            SELECT hour, SUM(accident_count) as accident_count
            FROM accident_summary
            WHERE region_code='{region_code}'
            GROUP BY hour
            ORDER BY hour
        """
        return pd.read_sql(query, engine)

    @st.cache_data
    def load_comparison(region_code):
        region_query = f"""
            SELECT SUM(death_cnt) as death, SUM(severe_cnt) as severe, SUM(minor_cnt) as minor
            FROM accident_prediction
            WHERE law_code='{region_code}'
        """
        nation_query = """
            SELECT SUM(death_cnt) as death, SUM(severe_cnt) as severe, SUM(minor_cnt) as minor
            FROM accident_prediction
        """
        region = pd.read_sql(region_query, engine)
        nation = pd.read_sql(nation_query, engine)
        return pd.DataFrame({
            "구분": ["선택지역", "전국"],
            "사망자": [region["death"][0], nation["death"][0]],
            "중상자": [region["severe"][0], nation["severe"][0]],
            "경상자": [region["minor"][0], nation["minor"][0]],
        })

    df = load_data()
    geojson = load_geojson()

    # 상단 영역: 상세/비교(좌) + 지도(우)
    with st.container():
        upper_left, upper_right = st.columns([1.25, 1.75], gap="medium")
        with upper_left:
            region = st.session_state.get("selected_region", None)
            if not region:
                st.markdown("""
                <div style='display:flex;align-items:center;justify-content:center;height:350px;font-size:1.22em;font-weight:600;color:#bbb;'>
                    지역구를 선택해 주세요
                </div>
                """, unsafe_allow_html=True)
            else:
                filtered = df[df["region_name"] == region]
                if filtered.empty:
                    st.warning(f"선택한 지역({region})의 데이터가 없습니다.<br>DB region_name/GeoJSON 이름 일치 확인 필요!", icon="⚠️")
                else:
                    info = filtered.iloc[0]
                    # 카드형 통계
                    st.markdown(f"### {region} 상세정보")
                    st.markdown(f"※ 최근 3년간 ({info['year']-2}~{info['year']}) 통계")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("사고건수", int(info["death_cnt"] + info["severe_cnt"] + info["minor_cnt"]))
                    col2.metric("사망자", int(info["death_cnt"]))
                    col3.metric("중상자", int(info["severe_cnt"]))
                    col4.metric("경상자", int(info["minor_cnt"]))

                    # 기타 정보
                    st.markdown(f"- **행정구역 코드:** {info['region_code']}")
                    st.markdown(f"- **위경도:** {info['latitude']:.5f}, {info['longitude']:.5f}")
                    st.markdown(f"- **위험등급:** {'고위험' if info['region_risk']==0 else ('중위험' if info['region_risk']==1 else '저위험')}")
                    st.markdown(f"- **위험점수:** {info['risk_score']}")

                    # 비교표
                    st.markdown("#### 전국/선택지역 사고 비교")
                    comp_df = load_comparison(info['region_code'])
                    st.dataframe(comp_df, use_container_width=True, hide_index=True)

                    # 다운로드 버튼 (고유 key 필수!)
                    st.download_button(
                        label=f"{region} 통계 데이터 다운로드",
                        data=info.to_csv().encode('utf-8'),
                        file_name=f"{region}_statistics.csv",
                        key=f"download_{region}"
                    )

        with upper_right:
            m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
            folium.GeoJson(
                geojson,
                name="지역 위험도",
                style_function=lambda feature: style_polygon(feature, df),
                highlight_function=lambda feature: highlight_style(),
                tooltip=get_polygon_tooltip()
            ).add_to(m)
            map_ret = st_folium(m, height=350, use_container_width=True, key="risk_map")
            if map_ret and map_ret.get("last_clicked"):
                lat = map_ret["last_clicked"]["lat"]
                lon = map_ret["last_clicked"]["lng"]
                region_name = find_region_by_coordinate(lat, lon, geojson)
                if region_name:
                    st.session_state["selected_region"] = region_name

    # 하단 영역: 월별/시간대별 그래프 좌우
    with st.container():
        lower_left, lower_right = st.columns(2)
        with lower_left:
            if region:
                month_df = load_monthly_summary(filtered.iloc[0]["region_code"])
                st.markdown("#### 월별 사고 분포")
                if month_df.empty:
                    st.info("월별 사고 데이터가 없습니다.")
                else:
                    st.bar_chart(month_df, x="month", y="accident_count")
        with lower_right:
            if region:
                hour_df = load_hourly_summary(filtered.iloc[0]["region_code"])
                st.markdown("#### 시간대별 사고 분포")
                if hour_df.empty:
                    st.info("시간대별 사고 데이터가 없습니다.")
                else:
                    st.bar_chart(hour_df, x="hour", y="accident_count")
