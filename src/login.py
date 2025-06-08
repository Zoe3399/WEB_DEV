import streamlit as st
from sqlalchemy import text
from pages.db_module import engine  # PostgreSQL용
import bcrypt

def login_page():
    # 비회원 여부를 세션 상태로 저장 (최초 접속 시 False로 초기화)
    if "is_guest" not in st.session_state:
        st.session_state["is_guest"] = False

    # 로그인 페이지 타이틀과 안내문 (가운데 정렬, 마크다운 사용)
    st.markdown("<h1 style='text-align: center;'>🚦 로그인</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>서비스 이용을 위해 로그인하세요</p>", unsafe_allow_html=True)
    st.write("")

    # 이메일, 비밀번호 입력창
    user_id = st.text_input("이메일", placeholder="이메일을 입력하세요")
    user_pw = st.text_input("PW", type="password", placeholder="비밀번호를 입력하세요")

    # 로그인 버튼 클릭 시 동작
    if st.button("로그인", key="login_btn", use_container_width=True):
        # DB에서 해당 이메일로 사용자 비밀번호 조회 (탈퇴/비활성화 회원 제외)
        print("로그인 버튼 눌림")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT password FROM users WHERE email = :e AND is_active = TRUE"),
                {"e": user_id}
            ).fetchone()
        # 입력된 비밀번호와 DB의 해시된 비밀번호 비교
        if result and bcrypt.checkpw(user_pw.encode('utf-8'), result[0].encode('utf-8')):
            st.success(f"{user_id}님 환영합니다!")
            st.session_state["is_login"] = True      # 로그인 상태 저장
            st.session_state["user_id"] = user_id    # 로그인 사용자 이메일 저장
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error("이메일 또는 비밀번호가 올바르지 않습니다.")

    # 비회원 진입 버튼
    if st.button("비회원으로 이용하기", key="guest_btn", use_container_width=True):
        print("비회원으로 접속합니다.")
        st.session_state["is_guest"] = True         # 비회원 플래그 ON
        st.session_state["page"] = "home"
        st.rerun()

    # 회원가입/비밀번호 찾기 버튼 (아래 2열로 배치)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("회원가입", key="signup_btn", use_container_width=True):
            print("회원가입 페이지로 이동")
            st.session_state["page"] = "terms"  # 회원가입 약관 동의 페이지로 이동
            st.rerun()
    with col2:
        if st.button("비밀번호 찾기", key="findpw_btn", use_container_width=True):
            print("비밀번호 찾기 페이지로 이동")
            st.session_state["page"] = "find_pw" # 비밀번호 찾기 페이지로 이동
            st.rerun()

if __name__ == "__main__":
    login_page()