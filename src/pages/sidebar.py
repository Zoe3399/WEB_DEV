import streamlit as st

def sidebar_menu():
    st.sidebar.markdown(
        "<h2 style='margin-bottom:20px;'>🚦 메뉴</h2>",
        unsafe_allow_html=True
    )

    # --- 1. 계정 관련 버튼 상단에 배치 ---
    # 로그인 상태일 때
    if st.session_state.get("is_login"):
        user_id = st.session_state.get("user_id", "Unknown")
        st.sidebar.write(f"👤 {user_id}님")
        if st.sidebar.button("로그아웃"):
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()
        # st.sidebar.markdown("---")
    # 비회원(게스트)일 때
    elif st.session_state.get("is_guest"):
        st.sidebar.write("👤 비회원 이용 중")
        if st.sidebar.button("로그인"):
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()
        # st.sidebar.markdown("---")
    # 미로그인(처음 접속 등)
    else:
        if st.sidebar.button("🔑 로그인"):
            st.session_state["page"] = "login"
            st.rerun()
        if st.sidebar.button("✍️ 회원가입"):
            st.session_state["page"] = "sign_up"
            st.rerun()

    # --- 2. 기능 메뉴 버튼 아래에 배치 ---
    menu_list = [("🏠 메인 대시보드", "home")]

    if st.session_state.get("is_login"):
        menu_list += [
            ("⬇️ 데이터 다운로드", "download"),
            ("👤 마이페이지", "mypage"),
        ]
    # 게스트는 추가 메뉴 없음

    for label, page_key in menu_list:
        if st.sidebar.button(label):
            st.session_state["page"] = page_key
            st.rerun()
