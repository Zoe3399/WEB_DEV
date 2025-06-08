import streamlit as st

def safety_tip_page():
    st.markdown("<h1 style='text-align:center;'>🚧 사고 예방 안내 · 안전 팁</h1>", unsafe_allow_html=True)
    st.write("---")

    # 안전/예방 팁 목록 (필요에 따라 DB, 파일, API 등에서 가져와도 OK)
    tips = [
        {
            "title": "횡단보도에서는 신호를 반드시 확인하세요!",
            "desc": "보행자 신호가 깜빡일 땐 절대 진입하지 않고, 초록불에도 좌우를 꼭 살핀 후 건너세요."
        },
        {
            "title": "야간·우천시 밝은 옷, 반사띠 착용 권장",
            "desc": "어두운 환경에서는 밝은 색 옷과 반사띠가 사고 예방에 큰 도움을 줍니다."
        },
        {
            "title": "도로에서는 항상 지정된 보행로만 이용하세요.",
            "desc": "차도, 갓길, 중앙선 등 위험지역 보행은 사고로 이어질 수 있습니다."
        },
        {
            "title": "어린이·노인 동반시, 반드시 손을 잡아주세요.",
            "desc": "취약계층 보호가 교통사고 예방의 첫걸음입니다."
        },
        {
            "title": "음주, 스마트폰 사용 등 ‘위험 보행’ 금지!",
            "desc": "음주/스마트폰 사용 중 보행은 사고 위험이 2배 이상 높아집니다."
        },
    ]

    # 카드 스타일로 예쁘게 안내
    for tip in tips:
        st.info(f"**{tip['title']}**\n\n{tip['desc']}")
        st.write("")

    st.write("---")
    st.caption("※ 더 많은 안전수칙은 경찰청·교통안전공단 등 공식기관 안내 참고")

if __name__ == "__main__":
    safety_tip_page()