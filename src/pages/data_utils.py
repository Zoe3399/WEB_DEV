# src/module/data_utils.py

import pandas as pd
import duckdb

from config import DUCKDB_PATH, DATA_PATH

def read_csv_file(file_path):
    """
    CSV 파일을 읽어서 pandas DataFrame으로 반환
    :param file_path: 읽을 csv 파일의 경로
    :return: pandas DataFrame
    """
    return pd.read_csv(file_path)

def read_excel_file(file_path, sheet_name=0):
    """
    엑셀(xls, xlsx) 파일을 읽어서 pandas DataFrame으로 반환
    :param file_path: 읽을 엑셀 파일의 경로
    :param sheet_name: 읽을 시트명 또는 번호 (기본=0)
    :return: pandas DataFrame
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)

def insert_dataframe_to_duckdb(df, table_name, db_path=DUCKDB_PATH):
    """
    pandas DataFrame을 DuckDB 데이터베이스의 테이블로 저장
    (테이블이 없으면 새로 생성)
    :param df: 저장할 pandas DataFrame
    :param table_name: 저장할 테이블명 (str)
    :param db_path: DuckDB 파일 경로 (기본값 config에서 불러옴)
    """
    con = duckdb.connect(db_path)
    con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
    # 이미 테이블이 있으면 append
    df.to_sql(table_name, con, if_exists='append', index=False)
    con.close()

def fetch_query_from_duckdb(query, db_path=DUCKDB_PATH):
    """
    DuckDB에서 쿼리 실행 결과를 pandas DataFrame으로 반환
    :param query: 실행할 SQL 쿼리 (str)
    :param db_path: DuckDB 파일 경로 (기본값 config에서 불러옴)
    :return: pandas DataFrame
    """
    con = duckdb.connect(db_path)
    df = con.execute(query).df()
    con.close()
    return df

def clean_column_names(df):
    """
    데이터프레임의 컬럼명을 소문자+언더스코어로 통일
    (예: '사고내용' → 'sago_naeyong')
    :param df: pandas DataFrame
    :return: 컬럼명 클린한 DataFrame
    """
    df.columns = (
        df.columns.str.strip()      # 좌우 공백 제거
        .str.lower()                # 소문자
        .str.replace(" ", "_")      # 띄어쓰기 언더스코어
    )
    return df