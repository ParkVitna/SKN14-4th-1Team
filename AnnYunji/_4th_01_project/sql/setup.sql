# root계정으로 실행

# 모든 host에서 접근가능한 django계정 생성(비밀번호 django)
create user 'django'@'%' identified by 'django';

# prjdb 생성
create database prjdb character set utf8mb4 collate utf8mb4_unicode_ci;

# django사용자에게 prjdb 권한 부여
grant all privileges on prjdb.* to 'django'@'%';
flush privileges;