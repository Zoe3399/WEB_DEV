# src/module/model_utils.py

import joblib # type: ignore
import pandas as pd

def load_model(model_path):
    """
    저장된 머신러닝 모델(joblib/pkl) 파일을 불러옴
    :param model_path: 모델 파일 경로
    :return: 모델 객체
    """
    return joblib.load(model_path)

def predict_risk_level(model, X):
    """
    모델과 입력 데이터를 받아 예측 결과(숫자 등급) 반환
    :param model: 학습된 모델 객체
    :param X: 예측용 입력 데이터(pandas DataFrame)
    :return: 예측 위험등급 (예: [0, 1, 2] 등)
    """
    return model.predict(X)

def convert_to_risk_label(y_pred):
    """
    숫자 등급을 '고', '중', '저' 등으로 변환
    :param y_pred: 예측 결과(0/1/2 등)
    :return: ['저', '중', '고'] 등으로 변환된 리스트
    """
    mapping = {0: '저', 1: '중', 2: '고'}
    if isinstance(y_pred, pd.Series) or isinstance(y_pred, list):
        return [mapping.get(i, '알수없음') for i in y_pred]
    else:
        return mapping.get(y_pred, '알수없음')

def model_predict_with_label(model, X):
    """
    예측 → 위험등급 레이블까지 한 번에 반환하는 함수
    :param model: 학습된 모델
    :param X: 입력 데이터(DataFrame)
    :return: 위험등급 문자열 리스트 (예: ['저', '고', ...])
    """
    y_pred = predict_risk_level(model, X)
    return convert_to_risk_label(y_pred)