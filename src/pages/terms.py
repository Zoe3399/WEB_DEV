import streamlit as st
import os
import datetime
from db_module import engine        # DB 연결 import
from sqlalchemy import text                # SQL 실행용

def read_md(file_path):
    # 약관 md 파일 읽기 (파일 없으면 오류 메시지 반환)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, file_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ 파일을 읽을 수 없습니다: {file_path}\n\n에러: {e}"

def terms_page():
    st.markdown(
        "<h1 style='text-align:center;'>회원가입 - 약관동의</h1>"
        "<p style='text-align:center;color:gray;'>서비스 이용을 위해 약관에 동의해 주세요.</p>",
        unsafe_allow_html=True
    )

    terms = [
        ("이용약관 동의 (필수)", "약관동의/service_terms.md", True),
        ("개인정보처리방침 동의 (필수)", "약관동의/privacy_policy.md", True),
        ("위치정보 동의 (선택)", "약관동의/location_info_consent.md", False),
        ("고유식별정보 동의 (선택)", "약관동의/unique_id_consent.md", False),
        ("마케팅 정보 수신 동의 (선택)", "약관동의/marketing_consent.md", False),
    ]

    # --- 상태 초기화 ---
    for label, _, _ in terms:
        if label not in st.session_state:
            st.session_state[label] = False
    if "all_agree" not in st.session_state:
        st.session_state["all_agree"] = False

    # --- 전체동의 체크 UX ---
    all_required_checked = all(st.session_state[label] for label, _, _ in terms)
    all_agree_clicked = st.checkbox(
        "전체 약관에 모두 동의합니다", 
        value=st.session_state["all_agree"],
        key="all_agree_cb", 
        help="모든 약관에 한번에 동의할 수 있습니다."
    )

    # 전체동의 버튼을 눌렀을 때만 전체 값 변경
    if all_agree_clicked != st.session_state["all_agree"]:
        st.session_state["all_agree"] = all_agree_clicked
        for label, _, _ in terms:
            st.session_state[label] = all_agree_clicked

    # 개별 약관 체크박스
    for label, file, required in terms:
        prev = st.session_state[label]
        st.session_state[label] = st.checkbox(label, value=st.session_state[label], key=f"agree_{label}")
        if prev and not st.session_state[label]:
            st.session_state["all_agree"] = False

        with st.expander("자세히 보기"):
            st.markdown(read_md(file))

    # 필수 동의만 확인
    all_required = all(st.session_state[label] for label, _, required in terms if required)

    if all_required and st.button("동의하고 회원가입 계속"):
        st.session_state["terms_form"] = {
            "service_terms_agree": st.session_state["이용약관 동의 (필수)"],
            "privacy_policy_agree": st.session_state["개인정보처리방침 동의 (필수)"],
            "location_info_agree": st.session_state["위치정보 동의 (선택)"],
            "unique_id_agree": st.session_state["고유식별정보 동의 (선택)"],
            "marketing_agree": st.session_state["마케팅 정보 수신 동의 (선택)"],
        }
        st.session_state["page"] = "sign_up"
        st.rerun()

# 페이지 실행
terms_page()
