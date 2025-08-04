-- pip install mysqlclient

-- https://clice.tistory.com/entry/Mac-M1-M2-%EB%A7%A5%EB%B6%81%EC%97%90%EC%84%9C-%EA%B0%84%EB%8B%A8%ED%95%98%EA%B2%8C-MySQL-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0#google_vignette

-- # root 계정으로 접속

-- # 사용자 nutriwisedb/django 생성

create user 'django'@'%' identified by 'django';

-- # nutriwisedb 데이터베이스 생성
-- # - 인코딩 utf8mb4 (다국어/이모지 텍스트 지원 ver)
-- # - 정렬방식 utf8mb4_unicode_ci (대소문자 구분없음)
create database nutriwisedb character set utf8mb4 collate utf8mb4_unicode_ci;

-- # django 계정 권한 부여
grant all privileges on nutriwisedb.* to 'django'@'%';

flush privileges;