-- 1) PUBLIC 스키마 삭제(전체 초기화, 신중히 실행)
DROP SCHEMA PUBLIC CASCADE;

-- 2) PUBLIC 스키마 재생성
CREATE SCHEMA PUBLIC;

-- 1. 사용자(회원) 테이블 (이메일 PK)
CREATE TABLE USERS (
    EMAIL VARCHAR(100) PRIMARY KEY,                  -- 이메일(=ID, 로그인 및 인증용)
    PASSWORD VARCHAR(256) NOT NULL,                  -- 암호화 비밀번호
    IS_ACTIVE BOOLEAN DEFAULT TRUE,                  -- 계정 활성화 여부
    CREATED_AT TIMESTAMP DEFAULT NOW()               -- 회원 가입 일시
);

-- 2. 사용자 역할/권한 관리
CREATE TABLE USER_ROLES (
    ID SERIAL PRIMARY KEY,                           -- 역할 고유번호
    USER_EMAIL VARCHAR(100) REFERENCES USERS(EMAIL), -- 대상 사용자(이메일 FK)
    ROLE VARCHAR(30),                                -- 역할명(예: ADMIN, MEMBER)
    ASSIGNED_AT TIMESTAMP DEFAULT NOW()              -- 역할 부여 일시
);

-- 3. 구/지역 정보
CREATE TABLE REGION_INFO (
    REGION_CODE VARCHAR(16) PRIMARY KEY,             -- 구(시군구) 코드
    REGION_NAME VARCHAR(40),                         -- 구 이름(예: 강남구)
    PARENT_CODE VARCHAR(16),                         -- 상위 행정구역(예: 서울시 코드)
    LATITUDE FLOAT,                                  -- 중심 위도
    LONGITUDE FLOAT                                  -- 중심 경도
);

-- 4. 사고 예측 결과 (구 단위, 모델 결과)
CREATE TABLE ACCIDENT_PREDICTION (
    YEAR INT,                                        -- 연도
    SIGUNGU VARCHAR(50),                             -- 시군구명
    LAW_CODE VARCHAR(20),                            -- 법정동코드(구)
    ACCIDENT_TYPE VARCHAR(20),                       -- 사고내용(중상사고 등)
    DEATH_CNT INT NOT NULL,                          -- 사망자 수
    SEVERE_CNT INT NOT NULL,                         -- 중상자 수
    MINOR_CNT INT NOT NULL,                          -- 경상자 수
    REPORT_CNT INT,                                  -- 부상신고자 수
    ACC_TYPE_DETAIL VARCHAR(50),                     -- 사고유형(차대사람 등)
    ROAD_TYPE VARCHAR(50),                           -- 도로형태(교차로 등)
    RISK_SCORE FLOAT NOT NULL,                       -- 예측 위험점수(실수)
    REGION_RISK INT NOT NULL,                        -- 위험등급(0~4 등급)
    AVG_ACCIDENT FLOAT,                              -- 시군구 평균 사고 건수
    PRIMARY KEY (YEAR, LAW_CODE, ACCIDENT_TYPE)
);

-- 복합 유니크(중복 방지)
ALTER TABLE ACCIDENT_PREDICTION
    ADD CONSTRAINT UQ_PREDICTION UNIQUE(YEAR, LAW_CODE, ACCIDENT_TYPE);

-- 5. 사고 통계 요약 (구/월/시간별)
CREATE TABLE ACCIDENT_SUMMARY (
    ID SERIAL PRIMARY KEY,                           -- 고유번호
    REGION_CODE VARCHAR(16) REFERENCES REGION_INFO(REGION_CODE), -- 구 코드
    YEAR INT,                                        -- 연도
    MONTH INT,                                       -- 월
    HOUR INT CHECK (HOUR BETWEEN 0 AND 23),          -- 시간대 (0~23)
    ACCIDENT_COUNT INT                               -- 사고 건수
);

-- 6. 즐겨찾기/관심 구역
CREATE TABLE USER_FAVORITE_REGION (
    ID SERIAL PRIMARY KEY,                           -- 즐겨찾기 고유번호
    USER_EMAIL VARCHAR(100) REFERENCES USERS(EMAIL) ON DELETE CASCADE, -- 사용자(이메일)
    REGION_CODE VARCHAR(16) REFERENCES REGION_INFO(REGION_CODE), -- 구 코드
    CREATED_AT TIMESTAMP DEFAULT NOW()               -- 등록 일시
);

-- 7. 사고 예방 안내/팁
CREATE TABLE SAFETY_TIP (
    ID SERIAL PRIMARY KEY,                           -- 팁 고유번호
    REGION_CODE VARCHAR(16) REFERENCES REGION_INFO(REGION_CODE), -- 구 코드
    ACCIDENT_TYPE VARCHAR(50),                       -- 사고유형별 팁(공통은 NULL)
    TIP TEXT,                                        -- 안내문/팁 내용
    CREATED_AT TIMESTAMP DEFAULT NOW()               -- 등록 일시
);

-- 8. 다운로드 기록
CREATE TABLE DOWNLOAD_LOG (
    ID SERIAL PRIMARY KEY,                           -- 기록 고유번호
    USER_EMAIL VARCHAR(100) REFERENCES USERS(EMAIL), -- 사용자(이메일)
    REGION_CODE VARCHAR(20),                         -- 다운로드 지역 코드
    DOWNLOADED_AT TIMESTAMP DEFAULT NOW(),           -- 다운로드 일시
    FILE_TYPE VARCHAR(20)                            -- 파일 형식(CSV/XLSX 등)
);

-- 9. 리포트 파일 관리
CREATE TABLE REPORT_FILE (
    ID SERIAL PRIMARY KEY,                           -- 고유번호
    REGION_CODE VARCHAR(20),                         -- 구 코드
    FILE_PATH VARCHAR(255),                          -- 파일 경로/이름
    CREATED_AT TIMESTAMP DEFAULT NOW()               -- 파일 생성 일시
);

-- 10. 관리자 행위 로그
CREATE TABLE ADMIN_LOG (
    ID SERIAL PRIMARY KEY,                           -- 로그 고유번호
    ADMIN_EMAIL VARCHAR(100) REFERENCES USERS(EMAIL),-- 관리자(이메일)
    ACTION VARCHAR(100),                             -- 수행 행위(예: 삭제, 수정 등)
    TARGET_TABLE VARCHAR(50),                        -- 대상 테이블명
    LOG_DETAIL JSONB,                                -- 상세 내용(JSON 형식)
    CREATED_AT TIMESTAMP DEFAULT NOW()               -- 로그 일시
);

-- 11. 사용자 행위 로그
CREATE TABLE USER_LOG (
    LOG_ID SERIAL PRIMARY KEY,                       -- 로그 고유번호
    USER_EMAIL VARCHAR(100) REFERENCES USERS(EMAIL), -- 사용자(이메일)
    ACTION VARCHAR(100),                             -- 행위(예: 다운로드, 조회 등)
    TARGET VARCHAR(100),                             -- 대상(구 등)
    DETAIL TEXT,                                     -- 세부 내용
    IP_ADDRESS VARCHAR(50),                          -- 접속 IP
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 로그 일시
);

-- 12. 에러/예외 로그
CREATE TABLE ERROR_LOG (
    ERROR_ID SERIAL PRIMARY KEY,                     -- 에러 고유번호
    USER_EMAIL VARCHAR(100) REFERENCES USERS(EMAIL), -- 사용자(이메일)
    ERROR_TYPE VARCHAR(100),                         -- 에러 유형(예: DB에러 등)
    MESSAGE TEXT,                                    -- 에러 메시지
    STACK_TRACE TEXT,                                -- 스택 트레이스(상세)
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 에러 발생 일시
);

-- 13. 원본 RAW 데이터 저장 테이블
CREATE TABLE ACCIDENT_RAW (
    ID SERIAL PRIMARY KEY,                           -- 고유번호
    YEAR INT,                                        -- 연도
    SIGUNGU VARCHAR(50),                             -- 시군구명
    LAW_CODE VARCHAR(20),                            -- 법정동코드(구)
    ACCIDENT_DESC VARCHAR(20),                       -- 사고내용
    DEATH_CNT INT,                                   -- 사망자 수
    SEVERE_CNT INT,                                  -- 중상자 수
    MINOR_CNT INT,                                   -- 경상자 수
    REPORT_CNT INT,                                  -- 부상신고자 수
    ACC_TYPE VARCHAR(50),                            -- 사고유형
    ROAD_TYPE VARCHAR(50),                           -- 도로형태
    VICTIM_STATUS VARCHAR(10),                       -- 피해자 상태
    VICTIM_SCORE FLOAT,                              -- 피해자 가중점수
    ACC_TYPE_SCORE FLOAT,                            -- 사고유형 가중점수
    ROAD_SCORE FLOAT,                                -- 도로형태 가중점수
    RISK_SCORE FLOAT,                                -- 위험점수
    ACC_TYPE_ROAD_AGG VARCHAR(100),                  -- 사고도로조합
    AVG_ACCIDENT FLOAT,                              -- 평균 사고건수
    REGION_RISK INT,                                 -- 위험등급(예측전이면 NULL)
    CREATED_AT TIMESTAMP DEFAULT NOW()               -- 저장 일시
);

-- CREATED_AT 자동 입력 보강
ALTER TABLE ACCIDENT_RAW
    ALTER COLUMN CREATED_AT SET DEFAULT NOW();

-- (마지막) 정상 생성됐는지 확인
SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PUBLIC';

-- users table check
select * from users
-- users table 테이블 추가
ALTER TABLE users ADD COLUMN user_type VARCHAR(50);
ALTER TABLE users ADD COLUMN purpose TEXT;

-- 약관 동의 여부 테이블
ALTER TABLE users
ADD COLUMN service_terms_agree BOOLEAN,
ADD COLUMN service_terms_agree_at TIMESTAMP,
ADD COLUMN privacy_policy_agree BOOLEAN,
ADD COLUMN privacy_policy_agree_at TIMESTAMP,
ADD COLUMN location_info_agree BOOLEAN,
ADD COLUMN location_info_agree_at TIMESTAMP,
ADD COLUMN unique_id_agree BOOLEAN,
ADD COLUMN unique_id_agree_at TIMESTAMP,
ADD COLUMN marketing_agree BOOLEAN,
ADD COLUMN marketing_agree_at TIMESTAMP;

-- accident_prediction에 테스트 위험도 값 넣기 (연도/코드/위험등급 직접 세팅)
INSERT INTO accident_prediction (
    year, sigungu, law_code, accident_type,
    death_cnt, severe_cnt, minor_cnt,
    report_cnt, acc_type_detail, road_type,
    risk_score, region_risk, avg_accident
)
VALUES
(2024, '강동구', '11230', '전체', 0, 0, 0, 0, NULL, NULL, 50.0, 0, 1.0),  -- 고위험(빨강)
(2024, '마포구', '11440', '전체', 0, 0, 0, 0, NULL, NULL, 30.0, 1, 1.0),  -- 중위험(주황)
(2024, '서초구', '11650', '전체', 0, 0, 0, 0, NULL, NULL, 10.0, 2, 1.0); -- 저위험(초록

INSERT INTO accident_prediction (year, sigungu, law_code, accident_type, death_cnt, severe_cnt, minor_cnt, report_cnt, risk_score, region_risk, avg_accident)
VALUES
(2023, '강동구', '11230', '전체', 2, 3, 7, 2, 53, 0, 3),
(2023, '마포구', '11440', '전체', 0, 1, 3, 0, 30, 1, 2);


-- accident_prediction table check
select * from accident_prediction ap 

-- accident_prediction table data delete
DELETE FROM accident_prediction;


 -- 테스트용 임시 데이터 추가
INSERT INTO ACCIDENT_RAW (YEAR, SIGUNGU, LAW_CODE, ACCIDENT_DESC, DEATH_CNT, SEVERE_CNT, MINOR_CNT, REPORT_CNT, ACC_TYPE, ROAD_TYPE, VICTIM_STATUS, VICTIM_SCORE, ACC_TYPE_SCORE, ROAD_SCORE, RISK_SCORE, ACC_TYPE_ROAD_AGG, AVG_ACCIDENT, REGION_RISK)
VALUES
(2024, '강남구', '11230', '교차로 사고', 0, 1, 5, 0, '차대사람', '교차로', '중상', 0.10, 0.15, 0.12, 50, '차대사람 - 교차로', 3, 0),
(2024, '마포구', '11440', '직선도로 사고', 0, 0, 2, 1, '차대사람', '직선로', '경상', 0.05, 0.09, 0.10, 30, '차대사람 - 직선로', 1, 1),
(2024, '서초구', '11650', '교차로 사고', 0, 1, 4, 0, '차대차', '교차로', '중상', 0.07, 0.12, 0.13, 40, '차대차 - 교차로', 2, 2),
(2024, '송파구', '11320', '교차로 사고', 1, 2, 3, 1, '차대사람', '교차로', '사망', 0.20, 0.18, 0.14, 60, '차대사람 - 교차로', 4, 0),
(2024, '용산구', '11380', '직선도로 사고', 0, 0, 2, 0, '차대사람', '직선로', '경상', 0.05, 0.07, 0.09, 28, '차대사람 - 직선로', 1, 1),
(2024, '광진구', '11215', '교차로 사고', 0, 0, 1, 0, '차대사람', '교차로', '경상', 0.04, 0.08, 0.10, 35, '차대사람 - 교차로', 1, 1),
(2024, '중구', '11140', '직선도로 사고', 0, 2, 5, 2, '차대차', '직선로', '중상', 0.12, 0.13, 0.14, 45, '차대차 - 직선로', 3, 0),
(2024, '동작구', '11530', '교차로 사고', 0, 1, 3, 1, '차대사람', '교차로', '중상', 0.09, 0.11, 0.12, 38, '차대사람 - 교차로', 2, 1),
(2024, '강서구', '11590', '직선도로 사고', 0, 1, 4, 0, '차대사람', '직선로', '중상', 0.08, 0.10, 0.12, 50, '차대사람 - 직선로', 1, 2),
(2024, '노원구', '11350', '교차로 사고', 0, 0, 2, 0, '차대차', '교차로', '경상', 0.06, 0.09, 0.11, 33, '차대차 - 교차로', 2, 0);

-- 테스트용 임시 데이터 추가
INSERT INTO accident_prediction (YEAR, SIGUNGU, LAW_CODE, ACCIDENT_TYPE, DEATH_CNT, SEVERE_CNT, MINOR_CNT, REPORT_CNT, RISK_SCORE, REGION_RISK, AVG_ACCIDENT)
VALUES
(2024, '강남구', '11230', '전체', 0, 1, 5, 0, 50, 0, 3),
(2024, '마포구', '11440', '전체', 0, 0, 2, 1, 30, 1, 2),
(2024, '서초구', '11650', '전체', 0, 1, 4, 0, 40, 2, 3),
(2024, '송파구', '11320', '전체', 1, 2, 3, 1, 60, 0, 4),
(2024, '용산구', '11380', '전체', 0, 0, 2, 0, 28, 0, 2),
(2024, '광진구', '11215', '전체', 0, 0, 1, 0, 35, 0, 1),
(2024, '중구', '11140', '전체', 0, 2, 5, 2, 45, 0, 3),
(2024, '동작구', '11530', '전체', 0, 1, 3, 1, 38, 1, 2),
(2024, '강서구', '11590', '전체', 0, 1, 4, 0, 50, 0, 3),
(2024, '노원구', '11350', '전체', 0, 0, 2, 0, 33, 0, 2);

INSERT INTO region_info (region_code, region_name, parent_code, latitude, longitude) VALUES
('11230', '강남구', '11', 37.517236, 127.047325),
('11440', '마포구', '11', 37.566324, 126.901451),
('11650', '서초구', '11', 37.483712, 127.032411),
('11710', '송파구', '11', 37.514575, 127.105399),
('11170', '용산구', '11', 37.532492, 126.990388),
('11215', '광진구', '11', 37.538484, 127.082294),
('11140', '중구', '11', 37.563843, 126.997602),
('11590', '동작구', '11', 37.512409, 126.939252),
('11500', '강서구', '11', 37.550978, 126.849538),
('11350', '노원구', '11', 37.654258, 127.056162);


select * from region_info;

-- 임시 더미 데이터 추가
-- accident_prediction (law_code, year 등 region_info와 연결, 임의 accident_type/연도/위험등급)
INSERT INTO accident_prediction (
  YEAR, SIGUNGU, LAW_CODE, ACCIDENT_TYPE, DEATH_CNT, SEVERE_CNT, MINOR_CNT, REPORT_CNT, 
  ACC_TYPE_DETAIL, ROAD_TYPE, RISK_SCORE, REGION_RISK, AVG_ACCIDENT
) VALUES
(2023, '강남구', '11230', '차대차', 1, 2, 6, 2, '차대차', '교차로', 52.1, 1, 5.1),
(2023, '마포구', '11440', '차대사람', 0, 1, 2, 1, '차대사람', '직선로', 33.2, 2, 3.2),
(2023, '서초구', '11650', '차대차', 1, 1, 3, 0, '차대차', '교차로', 44.7, 0, 4.7),
(2023, '송파구', '11320', '차대사람', 2, 1, 4, 0, '차대사람', '직선로', 65.0, 1, 6.2),
(2023, '용산구', '11380', '차대사람', 0, 0, 3, 2, '차대사람', '교차로', 27.8, 1, 2.8),
(2023, '광진구', '11215', '차대차', 1, 0, 2, 1, '차대차', '교차로', 39.0, 2, 3.9),
(2023, '중구', '11140', '차대사람', 0, 3, 5, 1, '차대사람', '직선로', 48.5, 0, 4.1),
(2023, '동작구', '11590', '차대차', 0, 2, 4, 0, '차대차', '교차로', 41.6, 2, 4.6),
(2023, '강서구', '11500', '차대사람', 1, 2, 3, 1, '차대사람', '교차로', 54.2, 1, 5.4),
(2023, '노원구', '11350', '차대차', 0, 1, 2, 0, '차대차', '직선로', 36.9, 2, 3.6);

-- accident_summary (region_code, year, month, hour, accident_count)
select * from accident_summary as2 ;

INSERT INTO accident_summary (region_code, year, month, hour, accident_count) VALUES
('11230', 2024, 1, 8, 3),
('11440', 2024, 2, 12, 5),
('11650', 2024, 3, 17, 7),
('11710', 2024, 4, 10, 4),
('11170', 2024, 5, 20, 6),
('11215', 2024, 6, 14, 2),
('11140', 2024, 7, 19, 5),
('11590', 2024, 8, 11, 3),
('11500', 2024, 9, 16, 7),
('11350', 2024, 10, 15, 6);

-- 데이터 추가
INSERT INTO accident_summary (region_code, year, month, hour, accident_count) VALUES
('11230', 2024, 1, 8, 3),
('11230', 2024, 2, 9, 5),
('11230', 2024, 3, 10, 2),
('11230', 2024, 1, 9, 4),
('11230', 2024, 2, 10, 1),
('11230', 2024, 3, 11, 6),
('11230', 2024, 1, 10, 5),
('11230', 2024, 2, 11, 2),
('11230', 2024, 3, 12, 3);


-- 
SELECT * FROM region_info WHERE region_code = '11230';
SELECT * FROM accident_prediction WHERE law_code = '11230' ORDER BY year;
SELECT * FROM accident_raw WHERE law_code = '11230' ORDER BY year;
SELECT * FROM accident_summary WHERE region_code = '11230' ORDER BY year;

-- 추가 데이터 삽입
INSERT INTO accident_prediction (year, sigungu, law_code, accident_type, death_cnt, severe_cnt, minor_cnt, report_cnt, acc_type_detail, road_type, risk_score, region_risk, avg_accident)
VALUES
(2022, '강남구', '11230', '전체', 1, 2, 4, 1, NULL, NULL, 48.0, 0, 2.3);


INSERT INTO accident_prediction (
    year, sigungu, law_code, accident_type,
    death_cnt, severe_cnt, minor_cnt, report_cnt,
    acc_type_detail, road_type,
    risk_score, region_risk, avg_accident
) VALUES
-- 2022년
--(2022, '강남구', '11230', '전체', 1, 2, 4, 1, NULL, NULL, 48.0, 0, 2.3),
(2022, '강남구', '11230', '차대사람', 1, 1, 2, 1, '차대사람', '교차로', 49.0, 0, 2.3),
(2022, '강남구', '11230', '차대차', 0, 1, 2, 0, '차대차', '직선로', 47.0, 1, 2.3),

-- 2023년
(2023, '강남구', '11230', '전체', 1, 2, 6, 2, NULL, NULL, 50.0, 1, 5.1),
(2023, '강남구', '11230', '차대사람', 1, 2, 3, 1, '차대사람', '교차로', 51.2, 1, 5.1),
--(2023, '강남구', '11230', '차대차', 0, 1, 3, 1, '차대차', '교차로', 52.1, 1, 5.1),

-- 2024년
--(2024, '강남구', '11230', '전체', 0, 1, 5, 0, NULL, NULL, 50.0, 0, 3.0),
(2024, '강남구', '11230', '차대사람', 0, 1, 3, 0, '차대사람', '교차로', 50.8, 0, 3.0),
(2024, '강남구', '11230', '차대차', 0, 0, 2, 0, '차대차', '직선로', 49.5, 1, 3.0);


-- 강남구 2022~2024년 사고 합계
SELECT
  SUM(death_cnt) as 사망자,
  SUM(severe_cnt) as 중상자,
  SUM(minor_cnt) as 경상자,
  SUM(death_cnt + severe_cnt + minor_cnt) as 사고건수
FROM accident_prediction
WHERE law_code = '11230'
  AND year BETWEEN 2022 AND 2024;

-- 전국 2022~2024년 사고 합계
SELECT
  SUM(death_cnt) as 사망자,
  SUM(severe_cnt) as 중상자,
  SUM(minor_cnt) as 경상자,
  SUM(death_cnt + severe_cnt + minor_cnt) as 사고건수
FROM accident_prediction
WHERE year BETWEEN 2022 AND 2024;


SELECT
  SUM(death_cnt), SUM(severe_cnt), SUM(minor_cnt), SUM(death_cnt + severe_cnt + minor_cnt)
FROM accident_prediction
WHERE law_code='11230' AND year BETWEEN 2022 AND 2024

