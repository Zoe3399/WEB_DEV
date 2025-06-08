import streamlit as st
from sqlalchemy import text
from db_module import engine
import pandas as pd

def my_page():
    st.markdown("<h1 style='text-align:center;'>👤 마이페이지</h1>", unsafe_allow_html=True)
    st.write("---")

    # --- 1. 로그인 여부 체크 ---
    if not st.session_state.get("is_login"):
        st.warning("마이페이지는 로그인 후 이용할 수 있습니다.")
        if st.button("로그인 하러가기"):
            st.session_state["page"] = "login"
            st.rerun()
        return

    # --- 2. 내 정보 표시 (DB에서 이메일 기준 조회) ---
    user_email = st.session_state.get("user_id")
    query = """
    SELECT email, user_type, created_at, last_login
    FROM users
    WHERE email = :e
    """
    with engine.connect() as conn:
        user = conn.execute(text(query), {"e": user_email}).fetchone()
    if user:
        st.info(
            f"**이메일:** {user['email']}  \n"
            f"**사용자 유형:** {user['user_type']}  \n"
            f"**가입일:** {user['created_at']}  \n"
            f"**최근 로그인:** {user['last_login']}"
        )
    else:
        st.error("사용자 정보를 불러오지 못했습니다.")
        return

    st.write("")

    # --- 3. 최근 다운로드/액션 로그(선택) ---
    st.subheader("내 다운로드 기록")
    query2 = """
    SELECT downloaded_at, region_code, file_type
    FROM download_log
    WHERE user_id = (SELECT id FROM users WHERE email = :e)
    ORDER BY downloaded_at DESC
    LIMIT 10
    """
    df = pd.read_sql(query2, engine, params={"e": user_email})
    st.dataframe(df, use_container_width=True)

    st.write("")

    # --- 4. 비밀번호 변경(바로가기) ---
    st.subheader("비밀번호 변경")
    st.write("비밀번호를 재설정하고 싶으시면 아래 버튼을 눌러주세요.")
    if st.button("비밀번호 재설정"):
        st.session_state["page"] = "reset_pw"
        st.rerun()

    st.write("---")
    st.caption("문의: traffic-risk@example.com")

if __name__ == "__main__":
    my_page()
