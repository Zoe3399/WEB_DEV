# src/module/download_utils.py

import pandas as pd
import io

def dataframe_to_csv_bytes(df):
    """
    pandas DataFrame을 CSV 바이너리(bytes) 형태로 변환 (Streamlit 다운로드 등에서 사용)
    :param df: pandas DataFrame
    :return: CSV 데이터(bytes)
    """
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    # StringIO → bytes로 변환 (Streamlit st.download_button에 바로 사용 가능)
    return output.getvalue().encode('utf-8-sig')

def dataframe_to_excel_bytes(df, sheet_name='Sheet1'):
    """
    pandas DataFrame을 엑셀(xlsx) 바이너리(bytes)로 변환 (Streamlit 다운로드 등에서 사용)
    :param df: pandas DataFrame
    :param sheet_name: 시트 이름
    :return: 엑셀 파일 데이터(bytes)
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()