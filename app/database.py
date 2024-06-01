import json
import os
import pymysql
from databases import Database  # 올바른 라이브러리에서 Database 클래스를 임포트
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser


# Load configuration
with open('secrets.json', 'r') as file:
    config = json.load(file)

# configparser 사용하여 설정 파일에서 설정을 읽어옴
config = configparser.ConfigParser()

# 설정 파일 경로를 절대 경로로 변경하여 문제 해결
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
config.read(config_path)

db_user = config.get("database", "user")
db_password = config.get("database", "password")
db_host = config.get("database", "host", fallback="localhost")
db_port = config.getint("database", "port", fallback=3306)
db_name = config.get("database", "name")

# Construct the database URL
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Use pymysql as MySQL driver
pymysql.install_as_MySQLdb()

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
database = Database(DATABASE_URL)
metadata = MetaData()

# OpenAI API 키 로드
# openai_api_key = config.get("OPENAI_API_KEY")
# if not openai_api_key:
#     raise ValueError("OpenAI API key not found in the config file")
