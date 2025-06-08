import streamlit as st
import sys
import os

# login.py가 src에 있을 때 import 가능하게 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 첫 페이지 설정: 세션 상태에 page 값이 없으면 로그인 페이지로
if "page" not in st.session_state:
    st.session_state["page"] = "login"

page = st.session_state["page"]

# 각 페이지 모듈에서 함수 import (함수명은 반드시 맞춰서 정의 필요)

if page == "login":
    from login import login_page
    login_page()

elif page == "terms":
    from terms import terms_page
    terms_page()

elif page == "sign_up":
    from sign_up import sign_up_page
    sign_up_page()

elif page == "find_pw":
    from find_pw import find_pw_page
    find_pw_page()

elif page == "reset_pw":
    from reset_pw import reset_pw_page
    reset_pw_page()

elif page == "home":
    from home import show_home
    show_home()

elif page == "download":
    from download import download_page
    download_page()

elif page == "mypage":
    from my_page import my_page
    my_page()
# ... 필요에 따라 페이지 계속 추가