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

