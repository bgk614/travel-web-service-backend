import json
import os
from databases import Database  
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Load configuration
with open('secrets.json', 'r') as file:
    config = json.load(file)

db_info = config['DATABASE_URL']
DATABASE_URL = f"mysql+pymysql://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/{db_info['dbname']}"


database = Database(DATABASE_URL)
metadata = MetaData()

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 로컬 정의
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 정의
Base = declarative_base()

# OpenAI API 키 로드
openai_api_key = config.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in the config file")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
