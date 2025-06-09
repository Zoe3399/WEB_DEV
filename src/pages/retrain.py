import streamlit as st
import pandas as pd
from insert_db_utils import insert_accident_raw  # 필요 시 모듈 import

st.title("데이터 업로드 및 모델 재학습")
st.write("새로운 사고 데이터를 업로드하고, 모델을 재학습하세요.")

uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head(10))
    if st.button("DB에 적재"):
        try:
            insert_accident_raw(df)
            st.success("DB 적재 성공!")
        except Exception as e:
            st.error(f"DB 적재 실패: {e}")

if st.button("모델 재학습 실행"):
    # 여기서 실제로는 subprocess로 python model_train.py 같은 파일 실행
    st.info("(여기서 모델 재학습 스크립트 실행)")

st.info("업로드/재학습 완료 시, 결과를 새로고침 후 확인할 수 있습니다.")