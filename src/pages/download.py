import streamlit as st
import pandas as pd
from db_module import engine
from download_utils import dataframe_to_csv_bytes, dataframe_to_excel_bytes
from sidebar import sidebar_menu
from datetime import datetime

def download_page():
    st.title("데이터 다운로드")
    sidebar_menu()

    # 안내 메시지(발표용)
    st.markdown("""
    <span style='color:#333;font-size:1.13em;'>
    ▶️ <b>고령자 교통사고 위험도 예측</b> 서비스의<br>
    <b>최신 3년치 데이터</b>를 자유롭게 다운로드할 수 있습니다.
    <br>분석/연구/행정 등 다양한 목적으로 활용 가능합니다.
    </span>
    """, unsafe_allow_html=True)

    # 로그인 체크
    if not st.session_state.get("is_login"):
        st.warning("회원만 데이터 다운로드가 가능합니다. 먼저 로그인 해주세요.")
        if st.button("로그인 하러 가기"):
            st.session_state["page"] = "login"
            st.rerun()
        st.stop()

    # accident_prediction 테이블에서 selectbox용 값 안전 조회
    try:
        sigungu_list = pd.read_sql("SELECT DISTINCT sigungu FROM accident_prediction", engine)["sigungu"].dropna().tolist()
    except Exception:
        sigungu_list = []
    try:
        acc_type_list = pd.read_sql("SELECT DISTINCT accident_type FROM accident_prediction", engine)["accident_type"].dropna().tolist()
    except Exception:
        acc_type_list = []
    try:
        road_type_list = pd.read_sql("SELECT DISTINCT road_type FROM accident_prediction", engine)["road_type"].dropna().tolist()
    except Exception:
        road_type_list = []

    if not sigungu_list and not acc_type_list and not road_type_list:
        st.info("다운로드 가능한 데이터가 없습니다. 데이터 적재 후 이용해 주세요.")
        return

    sigungu = st.selectbox("시군구(구 선택)", ["전체"] + sigungu_list)
    acc_type = st.selectbox("사고유형", ["전체"] + acc_type_list)
    road_type = st.selectbox("도로형태", ["전체"] + road_type_list)

    # 쿼리(최근 3년만)
    now = datetime.now()
    start_year = now.year - 2
    query = f"SELECT * FROM accident_prediction WHERE year BETWEEN {start_year} AND {now.year}"
    if sigungu != "전체":
        query += f" AND sigungu = '{sigungu}'"
    if acc_type != "전체":
        query += f" AND accident_type = '{acc_type}'"
    if road_type != "전체":
        query += f" AND road_type = '{road_type}'"

    try:
        df = pd.read_sql(query, engine)
    except Exception:
        st.info("데이터를 불러오는 중 오류가 발생했습니다. 데이터베이스 상태를 확인해 주세요.")
        return

    st.write(f"총 <b>{len(df):,}건</b>의 데이터가 조회되었습니다.", unsafe_allow_html=True)

    # 미리보기 표와 다운로드 버튼 아래에도 try-except로 에러 케이스 안내
    if not df.empty:
        try:
            st.dataframe(df.head(30), use_container_width=True, hide_index=True)
            dl_type = st.radio("다운로드 파일 형식", ["CSV", "Excel"], horizontal=True)
            today = datetime.now().strftime("%Y%m%d")
            sigungu_nm = sigungu if sigungu != "전체" else "all"
            fname = f"accident_{sigungu_nm}_{today}.{ 'csv' if dl_type=='CSV' else 'xlsx' }"

            if dl_type == "CSV":
                st.download_button(
                    "CSV 다운로드",
                    data=dataframe_to_csv_bytes(df),
                    file_name=fname,
                    mime="text/csv"
                )
            else:
                st.download_button(
                    "Excel 다운로드",
                    data=dataframe_to_excel_bytes(df),
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.info("※ 상위 30건 미리보기. 전체 데이터는 다운로드 파일에서 확인하세요.")
        except Exception:
            st.info("미리보기 또는 다운로드 준비 중 오류가 발생했습니다. 데이터 내용을 확인해 주세요.")
    else:
        st.info("조회 조건에 맞는 데이터가 없습니다. (필터를 변경해 주세요)")

    # 추가 안내(발표/서비스용)
    st.markdown("""
    <br>
    - 데이터 출처: 한국교통안전공단(TAAS), KOSIS, 공공데이터포털 등
    """, unsafe_allow_html=True)