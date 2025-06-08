import streamlit as st
import re

def check_email_format(email: str) -> bool:
    """
    이메일 형식 검증 (간단 정규식)
    :param email: 입력 이메일 문자열
    :return: 형식에 맞으면 True, 아니면 False
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def check_password_strength(password: str) -> bool:
    """
    비밀번호 강도 체크 (8자 이상, 영문+숫자)
    :param password: 비밀번호 문자열
    :return: 조건 충족 True, 아니면 False
    """
    return (
        len(password) >= 8 and
        re.search(r"[a-zA-Z]", password) and
        re.search(r"\d", password)
    )

def alert_and_stop(msg: str):
    """
    경고 메시지 출력 후 앱 중단
    :param msg: 안내 메시지
    """
    st.error(msg)
    st.stop()

def format_datetime(dt):
    """
    Datetime 객체를 YYYY-MM-DD HH:MM 형식 문자열로 변환
    (None이거나 문자열이면 그대로 반환)
    """
    if not dt:
        return ""
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except AttributeError:
        return str(dt)

# (추후 자주쓰는 유틸 함수 여기서 계속 추가 가능)