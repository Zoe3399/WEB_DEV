import streamlit as st
from sqlalchemy import text
from db_module import engine  # DB 연결

def find_pw_page():
    st.title("비밀번호 찾기")
    user_email = st.text_input("가입한 이메일을 입력하세요")

    # 인증번호 발송 버튼 클릭 시
    if st.button("인증번호 발송"):
        # 1. 이메일 형식 검증
        if not user_email or "@" not in user_email or "." not in user_email:
            st.warning("유효한 이메일을 입력해 주세요.")
        else:
            # 2. DB에 이메일 존재여부 확인
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM users WHERE email = :e AND is_active = TRUE"),
                    {"e": user_email}
                ).scalar()
            if result == 0:
                st.error("등록되지 않은 이메일입니다.")
            else:
                # (실제 서비스라면) 인증번호를 이메일로 전송
                st.session_state["find_pw_email"] = user_email
                st.session_state["find_pw_code"] = "123456"  # 테스트용 코드
                st.success("인증번호가 이메일로 전송되었습니다.")

    # 인증번호 입력란
    code_input = st.text_input("인증번호 입력")

    # 인증번호 확인 버튼 클릭 시
    if st.button("인증번호 확인"):
        if code_input == st.session_state.get("find_pw_code"):
            st.success("이메일 인증이 완료되었습니다.")
            st.session_state["reset_pw_email"] = st.session_state.get("find_pw_email")
            st.session_state["page"] = "reset_pw"
            st.rerun()
        else:
            st.error("인증번호가 일치하지 않습니다.")

if __name__ == "__main__":
    find_pw_page()