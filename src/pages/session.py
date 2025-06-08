import streamlit as st

def init_session():
    """
    세션 상태에 꼭 필요한 값들을 초기화하는 함수.
    (첫 방문/앱 재시작 시 자동 세팅)
    """
    # 로그인 여부
    if "is_login" not in st.session_state:
        st.session_state["is_login"] = False
    # 비회원(게스트) 여부
    if "is_guest" not in st.session_state:
        st.session_state["is_guest"] = False
    # 현재 로그인한 사용자 이메일(ID)
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    # 현재 페이지 정보 (Multipage에선 생략 가능)
    if "page" not in st.session_state:
        st.session_state["page"] = None
    # 기타 필요 세션 변수(여기서 확장 가능)
    # 예: 이메일 인증, 약관동의 등
    if "terms_agreed" not in st.session_state:
        st.session_state["terms_agreed"] = False
    if "email_verified" not in st.session_state:
        st.session_state["email_verified"] = False
    if "email_code" not in st.session_state:
        st.session_state["email_code"] = None

# 메인, 로그인, 회원가입 등 각 파일에서 아래처럼 호출해서 세션 초기화
if __name__ == "__main__":
    init_session()