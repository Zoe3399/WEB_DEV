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
    
    # 상단 서비스 소개
    st.markdown("""
    <div style='margin-bottom:18px;'>
        <span style='font-size:1.7em;font-weight:700;'>🚦 데이터로 보는 고령자 교통사고 위험도</span><br>
        <span style='font-size:1.13em;color:#666;'>지역별 고위험 구간, 유형별 사고통계, AI 예측까지 한눈에!</span>
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
        base_path = os.path.dirname(os.path.abspath(__file__))  # 현재 home.py 기준
        file_path = os.path.join(base_path, 'data', '법정구역_시군구_simplified.geojson')

        with open(file_path, encoding='utf-8') as f:
            geojson = json.load(f)
    
        return geojson
    @st.cache_data
    def load_accident_sum(region_code=None):
        # 3년간 합계
        base = "WHERE year BETWEEN EXTRACT(YEAR FROM CURRENT_DATE)-2 AND EXTRACT(YEAR FROM CURRENT_DATE)"
        region_filter = f"AND law_code='{region_code}'" if region_code else ""
        query = f"""
            SELECT SUM(death_cnt) as death, SUM(severe_cnt) as severe, SUM(minor_cnt) as minor
            FROM accident_prediction
            {base} {region_filter}
        """
        return pd.read_sql(query, engine)

    @st.cache_data
    def load_monthly_summary(region_code):
        # 최근 3년 데이터 집계
        query = f"""
            SELECT month, SUM(accident_count) as accident_count
            FROM accident_summary
            WHERE region_code='{region_code}'
            AND year BETWEEN EXTRACT(YEAR FROM CURRENT_DATE)-2 AND EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY month ORDER BY month
        """
        return pd.read_sql(query, engine)

    @st.cache_data
    def load_hourly_summary(region_code):
        query = f"""
            SELECT hour, SUM(accident_count) as accident_count
            FROM accident_summary
            WHERE region_code='{region_code}'
            AND year BETWEEN EXTRACT(YEAR FROM CURRENT_DATE)-2 AND EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY hour ORDER BY hour
        """
        return pd.read_sql(query, engine)

    df = load_data()
    geojson = load_geojson()

    # 메인 레이아웃 (지도+상세/비교)
    upper_left, upper_right = st.columns([1.25, 1.75], gap="medium")
    with upper_left:
        region = st.session_state.get("selected_region", None)
        if not region:
            st.markdown("""
            <div style='display:flex;align-items:center;justify-content:center;height:320px;font-size:1.15em;font-weight:600;color:#bbb;'>
                지역구를 선택해 주세요
            </div>
            """, unsafe_allow_html=True)
        else:
            filtered = df[df["region_name"] == region]
            if filtered.empty:
                st.warning(f"선택한 지역({region})의 데이터가 없습니다.<br>DB region_name/GeoJSON 이름 일치 확인 필요!", icon="⚠️")
            else:
                info = filtered.iloc[0]
                # 3년간 합계
                summary = load_accident_sum(info['region_code'])
                accident_total = int(summary["death"][0] + summary["severe"][0] + summary["minor"][0])
                st.markdown(f"### {region} 상세정보")
                st.markdown("※ 최근 3년간 사고 통계")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("사고건수", accident_total)
                col2.metric("사망자", int(summary["death"][0]))
                col3.metric("중상자", int(summary["severe"][0]))
                col4.metric("경상자", int(summary["minor"][0]))

                # 기타 정보
                st.markdown(f"- **행정구역 코드:** {info['region_code']}")
                st.markdown(f"- **위경도:** {info['latitude']:.5f}, {info['longitude']:.5f}")
                st.markdown(f"- **위험등급:** {'고위험' if info['region_risk']==0 else ('중위험' if info['region_risk']==1 else '저위험')}")
                st.markdown(f"- **위험점수:** {info['risk_score']}")

                # 전국/선택지역 비교
                nation_sum = load_accident_sum()
                comp_df = pd.DataFrame({
                    "구분": ["선택지역", "전국"],
                    "사망자": [summary["death"][0], nation_sum["death"][0]],
                    "중상자": [summary["severe"][0], nation_sum["severe"][0]],
                    "경상자": [summary["minor"][0], nation_sum["minor"][0]],
                })
                st.markdown("#### 전국/선택지역 사고 비교")
                st.dataframe(comp_df, use_container_width=True, hide_index=True)

                # 다운로드 버튼
                st.download_button(
                    label=f"{region} 통계 데이터 다운로드",
                    data=filtered.to_csv(index=False).encode('utf-8'),
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

    # 하단: 그래프 영역(탭)
    if region:
        st.markdown("### 지역별 상세 사고 분석")
        tab1, tab2 = st.tabs(["월별 분포", "시간대별 분포"])
        with tab1:
            month_df = load_monthly_summary(info['region_code'])
            if month_df.empty:
                st.info("월별 사고 데이터가 없습니다.")
            else:
                st.bar_chart(month_df, x="month", y="accident_count")
        with tab2:
            hour_df = load_hourly_summary(info['region_code'])
            if hour_df.empty:
                st.info("시간대별 사고 데이터가 없습니다.")
            else:
                st.bar_chart(hour_df, x="hour", y="accident_count")

    # 하단: 데이터 다운로드/안내
    st.markdown("""
    ---
    #### 데이터/분석 결과 다운로드
    - [전국 전체 데이터 다운로드 (CSV)](링크)
    - [보고서 PDF 다운로드](링크)
    """, unsafe_allow_html=True)
    st.info("이 서비스는 데이터 기반 정책·연구, 언론, 공공기관 모두 자유롭게 활용 가능합니다.")