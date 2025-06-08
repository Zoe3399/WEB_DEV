import streamlit as st
from sqlalchemy import text
import bcrypt
from db_module import engine
import time

def reset_pw_page():
    if "reset_pw_email" not in st.session_state:
        st.error("비밀번호 찾기 페이지에서 이메일 인증을 먼저 해주세요.")
        st.stop()

    st.markdown("""
        <style>
        .block-container {
            max-width: 600px !important;
            margin: auto;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("비밀번호 재설정")

    new_password = st.text_input("새 비밀번호", type="password")
    confirm_password = st.text_input("새 비밀번호 확인", type="password")

    if st.button("비밀번호 재설정"):
        import re

        st.write("디버그용: 이메일 = ", st.session_state.get("reset_pw_email"))

        if not new_password or not confirm_password:
            st.error("비밀번호와 비밀번호 확인을 모두 입력해주세요.")
            return
        elif new_password != confirm_password:
            st.error("비밀번호가 일치하지 않습니다.")
            return
        elif len(new_password) < 8 or not re.search(r"\d", new_password) or not re.search(r"[a-zA-Z]", new_password):
            st.error("비밀번호는 8자 이상, 영문자와 숫자를 모두 포함해야 합니다.")
            return
        else:
            try:
                with engine.connect() as conn:
                    # 기존 해시값 읽기
                    result = conn.execute(
                        text("SELECT password FROM users WHERE email = :email"),
                        {"email": st.session_state["reset_pw_email"]}
                    ).fetchone()
                    st.write("디버그용: 기존 해시 = ", result)
                    if result and bcrypt.checkpw(new_password.encode('utf-8'), result[0].encode('utf-8')):
                        st.error("이전과 동일한 비밀번호로는 변경할 수 없습니다.")
                        return
                    # bcrypt 해시 생성 (bytes)
                    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    hashed_pw_str = hashed_pw.decode('utf-8')
                    st.write("디버그용: 새 해시 = ", hashed_pw_str)
                    update_stmt = text("UPDATE users SET password = :password WHERE email = :email")
                    # 트랜잭션 블록 없이 바로 실행!
                    conn.execute(update_stmt, {
                        "password": hashed_pw_str,
                        "email": st.session_state["reset_pw_email"]
                    })
                st.success("비밀번호가 성공적으로 재설정되었습니다. 3초 후 로그인 페이지로 이동합니다.")
                del st.session_state["reset_pw_email"]
                time.sleep(3)  # 3초 대기
                st.session_state["page"] = "login"
                st.rerun()
            except Exception as e:
                time.sleep(5)
                st.error(f"비밀번호 재설정 중 오류가 발생했습니다. (상세: {e})")

if __name__ == "__main__":
    reset_pw_page()
