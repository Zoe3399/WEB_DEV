import streamlit as st
import pandas as pd
from db_module import engine  # PostgreSQL용
from download_utils import dataframe_to_csv_bytes, dataframe_to_excel_bytes
from sidebar import sidebar_menu

def download_page():
    st.title("데이터 다운로드")
    sidebar_menu()

    # 권한 체크 (비회원이면 접근 제한)
    if not st.session_state.get("is_login"):
        st.warning("회원만 데이터 다운로드가 가능합니다. 먼저 로그인 해주세요.")
        if st.button("로그인 하러 가기"):
            st.session_state["page"] = "login"
            st.rerun()
        st.stop()

    # DB에서 조회 옵션 불러오기 (예: 구, 사고유형 등)
    sigungu_list = pd.read_sql("SELECT DISTINCT sigungu FROM accident_prediction", engine)["sigungu"].tolist()
    acc_type_list = pd.read_sql("SELECT DISTINCT accident_type FROM accident_prediction", engine)["accident_type"].tolist()
    road_type_list = pd.read_sql("SELECT DISTINCT road_type FROM accident_prediction", engine)["road_type"].tolist()

    # 필터 옵션 선택
    sigungu = st.selectbox("시군구", ["전체"] + sigungu_list)
    acc_type = st.selectbox("사고유형", ["전체"] + acc_type_list)
    road_type = st.selectbox("도로형태", ["전체"] + road_type_list)

    # SQL 쿼리 동적 생성
    query = "SELECT * FROM accident_prediction WHERE 1=1"
    if sigungu != "전체":
        query += f" AND sigungu = '{sigungu}'"
    if acc_type != "전체":
        query += f" AND accident_type = '{acc_type}'"
    if road_type != "전체":
        query += f" AND road_type = '{road_type}'"

    df = pd.read_sql(query, engine)

    st.write(f"총 {len(df)}건의 데이터가 조회되었습니다.")

    # 다운로드 버튼 (CSV/엑셀 선택)
    dl_type = st.radio("파일 형식", ["CSV", "Excel"], horizontal=True)

    if not df.empty:
        if dl_type == "CSV":
            st.download_button(
                "CSV 다운로드",
                data=dataframe_to_csv_bytes(df),
                file_name="download.csv",
                mime="text/csv"
            )
        else:
            st.download_button(
                "Excel 다운로드",
                data=dataframe_to_excel_bytes(df),
                file_name="download.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("다운로드할 데이터가 없습니다.")

# 이거 필요없음! (단독 실행할 일 없으면)
# if __name__ == "__main__":
#     download_page()
