import streamlit as st
from sqlalchemy import text
import bcrypt
import re
import datetime
from db_module import engine  # DB 연결 엔진

def sign_up_page():
    # (A) 회원가입 직후 페이지 이동: 로그인 화면으로 전환
    if st.session_state.get("just_signed_up", False):
        st.success("회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.")
        st.session_state["just_signed_up"] = False
        st.session_state["page"] = "login"
        st.rerun()
        return

    st.markdown("<h1 style='margin-bottom:32px;'>회원가입</h1>", unsafe_allow_html=True)
    st.markdown("※ 이메일 인증은 필수입니다. 이메일을 입력하고 인증번호를 확인해 주세요.")

    # (1) 이메일 입력 + 인증 버튼
    col1, col2 = st.columns([3, 1])
    with col1:
        email = st.text_input("이메일", placeholder="이메일 주소를 입력하세요", key="email_input")
    with col2:
        st.write("")
        email_auth_btn = st.button("이메일 인증", key="email_auth_btn")

    # (2) 인증번호 입력 + 확인 버튼
    col3, col4 = st.columns([3, 1])
    with col3:
        email_code_input = st.text_input("인증번호 입력", placeholder="6자리 숫자", key="email_code_input")
    with col4:
        st.write("")
        email_verify_btn = st.button("인증번호 확인", key="email_verify_btn")

    # 세션 초기화
    if "email_code" not in st.session_state:
        st.session_state["email_code"] = None
    if "email_verified" not in st.session_state:
        st.session_state["email_verified"] = False

    # (3) 비밀번호/추가정보 입력
    col_pw1, col_pw2 = st.columns(2)
    with col_pw1:
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    with col_pw2:
        password2 = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")

    user_type = st.selectbox("사용자 유형", ["학생", "공공기관", "회사", "기타"], key="user_type")
    purpose = st.text_input("사용 목적", placeholder="앱 이용 목적을 입력해 주세요", key="purpose_input")

    # (4) 약관동의 값 세션에서 가져오기
    # 약관동의는 이전 페이지(terms.py)에서 st.session_state["terms_form"]에 dict형태로 저장됨
    terms_form = st.session_state.get("terms_form", None)

    # 약관동의 체크값 보이기(혹은 누락 안내)
    if terms_form is None:
        st.warning("약관동의가 누락되었습니다. 먼저 약관동의 페이지에서 동의 후 진행하세요.")
        return
    else:
        st.success("약관동의가 완료되었습니다.")

    signup_btn = st.button("회원가입", key="signup_btn", use_container_width=True)

    # (1) 이메일 인증 버튼 클릭
    if email_auth_btn:
        if not email:
            st.warning("이메일을 입력해 주세요.")
        elif "@" not in email or "." not in email:
            st.warning("유효한 이메일 형식으로 입력해 주세요.")
        else:
            with engine.begin() as conn:
                duplicate_count = conn.execute(
                    text("SELECT COUNT(*) FROM users WHERE email = :e"),
                    {"e": email}
                ).scalar()
            if duplicate_count > 0:
                st.error("이미 가입된 이메일입니다.")
            else:
                st.session_state["email_code"] = "123456"  # 테스트용 코드
                st.session_state["email_verified"] = False
                st.success("인증번호가 이메일로 발송되었습니다. (테스트용 코드: 123456)")

    # (2) 인증번호 확인 버튼 클릭
    if email_verify_btn:
        if not email_code_input:
            st.warning("인증번호를 입력해 주세요.")
        elif email_code_input == st.session_state["email_code"]:
            st.session_state["email_verified"] = True
            st.success("이메일 인증이 완료되었습니다.")
        else:
            st.error("인증번호가 일치하지 않습니다.")

    # (3) 회원가입 버튼 클릭
    if signup_btn:
        # 필수 입력값 체크
        if not email or not password or not password2 or not purpose:
            st.error("이메일, 비밀번호, 비밀번호 확인, 사용 목적은 모두 필수 입력입니다.")
            return
        if not st.session_state["email_verified"]:
            st.error("이메일 인증을 완료해 주세요.")
            return
        if password != password2:
            st.error("비밀번호가 일치하지 않습니다.")
            return
        if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[a-zA-Z]", password):
            st.error("비밀번호는 8자 이상, 영문자와 숫자를 모두 포함해야 합니다.")
            return

        with engine.begin() as conn:
            existing_count = conn.execute(
                text("SELECT COUNT(*) FROM users WHERE email = :e"),
                {"e": email}
            ).scalar()
            if existing_count > 0:
                st.error("이미 등록된 이메일입니다.")
                return

            # 비밀번호 해시화 (bcrypt)
            password_bytes = password.encode("utf-8")
            hashed_pw = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

            # 약관 동의 및 가입 정보 INSERT
            now = datetime.datetime.now()
            user_data = {
                "email": email,
                "password": hashed_pw,
                "user_type": user_type,
                "purpose": purpose,
                "service_terms_agree": terms_form["service_terms_agree"],
                "service_terms_agree_at": now,
                "privacy_policy_agree": terms_form["privacy_policy_agree"],
                "privacy_policy_agree_at": now,
                "location_info_agree": terms_form["location_info_agree"],
                "location_info_agree_at": now if terms_form["location_info_agree"] else None,
                "unique_id_agree": terms_form["unique_id_agree"],
                "unique_id_agree_at": now if terms_form["unique_id_agree"] else None,
                "marketing_agree": terms_form["marketing_agree"],
                "marketing_agree_at": now if terms_form["marketing_agree"] else None
            }

            try:
                inserted = conn.execute(
                    text("""
                        INSERT INTO users (
                            email, password, user_type, purpose,
                            service_terms_agree, service_terms_agree_at,
                            privacy_policy_agree, privacy_policy_agree_at,
                            location_info_agree, location_info_agree_at,
                            unique_id_agree, unique_id_agree_at,
                            marketing_agree, marketing_agree_at
                        ) VALUES (
                            :email, :password, :user_type, :purpose,
                            :service_terms_agree, :service_terms_agree_at,
                            :privacy_policy_agree, :privacy_policy_agree_at,
                            :location_info_agree, :location_info_agree_at,
                            :unique_id_agree, :unique_id_agree_at,
                            :marketing_agree, :marketing_agree_at
                        )
                        RETURNING email
                    """),
                    user_data
                )
                new_email = inserted.scalar()
            except Exception as e:
                st.error(f"회원가입 중 오류가 발생했습니다: {e}")
                return

        # 가입 성공 처리
        st.session_state["just_signed_up"] = True
        st.session_state["page"] = "login"
        st.rerun()

if __name__ == "__main__":
    sign_up_page()
