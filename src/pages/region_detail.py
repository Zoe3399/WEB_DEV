

import streamlit as st
import pandas as pd
from db_module import engine
import plotly.express as px

def region_detail_page():
    st.markdown("<h1 style='text-align:center;'>📄 지역별 상세 위험분석</h1>", unsafe_allow_html=True)
    st.write("---")

    # --- 1. 시군구(구) 선택 드롭다운 (DB에서 동적 로드) ---
    sigungu_query = "SELECT DISTINCT sigungu FROM accident_prediction ORDER BY sigungu"
    sigungu_list = pd.read_sql(sigungu_query, engine)["sigungu"].tolist()
    selected_sigungu = st.selectbox("상세 위험도를 확인할 시군구(구)를 선택하세요.", sigungu_list)

    # --- 2. 선택된 구의 최근 사고 통계, 위험도 집계 ---
    detail_query = """
    SELECT accident_type, region_risk, SUM(death_cnt) as death, SUM(severe_cnt) as severe,
    SUM(minor_cnt) as minor, COUNT(*) as total
    FROM accident_prediction
    WHERE sigungu = :s
    GROUP BY accident_type, region_risk
    ORDER BY total DESC
    """
    df = pd.read_sql(detail_query, engine, params={"s": selected_sigungu})

    # --- 3. 상단 카드: 구별 요약 (총 사고/사망/중상/경상) ---
    total_query = """
    SELECT SUM(death_cnt) as total_death, SUM(severe_cnt) as total_severe,
    SUM(minor_cnt) as total_minor, COUNT(*) as total_case
    FROM accident_prediction
    WHERE sigungu = :s
    """
    total = pd.read_sql(total_query, engine, params={"s": selected_sigungu})
    death, severe, minor, case = total.loc[0, "total_death"], total.loc[0, "total_severe"], total.loc[0, "total_minor"], total.loc[0, "total_case"]

    st.info(
        f"**{selected_sigungu} 최근 사고현황**\n\n"
        f"• 총 사고 {case}건   |   사망 {death}명   |   중상 {severe}명   |   경상 {minor}명"
    )
    st.write("")

    # --- 4. 위험도별, 사고유형별 통계 표 ---
    st.subheader("사고 유형별·위험등급별 상세 통계")
    st.dataframe(df, use_container_width=True)

    # --- 5. 시각화: 사고유형별 건수 바 차트 ---
    chart_df = df.groupby("accident_type").agg({"total": "sum"}).reset_index()
    fig = px.bar(chart_df, x="accident_type", y="total", title=f"{selected_sigungu} 사고유형별 발생건수")
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. 위험등급 비율 파이차트 ---
    pie_df = df.groupby("region_risk").agg({"total": "sum"}).reset_index()
    pie_fig = px.pie(pie_df, names="region_risk", values="total", title=f"{selected_sigungu} 위험등급별 비율")
    st.plotly_chart(pie_fig, use_container_width=True)

    # --- 7. (옵션) 최근 3년 추이, 월별 추이 등 더 넣고 싶으면 여기에 추가 가능 ---

    st.write("---")
    st.caption("※ 더 자세한 통계는 데이터 다운로드 메뉴를 이용해 주세요.")

if __name__ == "__main__":
    region_detail_page()