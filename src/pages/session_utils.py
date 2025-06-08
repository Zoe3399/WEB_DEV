# src/module/session_utils.py

import streamlit as st

def login_user(user_email):
    """
    로그인 성공 시 사용자 정보를 세션 상태에 저장
    :param user_email: 로그인한 사용자 이메일
    """
    st.session_state["is_logged_in"] = True
    st.session_state["user_email"] = user_email

def logout_user():
    """
    로그아웃 시 세션 상태에서 사용자 정보 제거
    """
    st.session_state["is_logged_in"] = False
    st.session_state["user_email"] = None

def is_user_logged_in():
    """
    사용자가 로그인 상태인지 확인
    :return: True(로그인), False(비로그인)
    """
    return st.session_state.get("is_logged_in", False)

def get_logged_in_user():
    """
    현재 로그인한 사용자의 이메일 반환
    :return: 사용자 이메일 또는 None
    """
    return st.session_state.get("user_email", None)