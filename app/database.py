import json
from databases import Database  
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


# Load configuration
with open('secrets.json', 'r') as file:
    config = json.load(file)


db_info = config['DATABASE_URL']
DATABASE_URL = f"mysql+pymysql://{db_info['root']}:{db_info['0000']}@{db_info['localhost']}:{db_info['3306']}/{db_info['tours']}"


database = Database(DATABASE_URL)
metadata = MetaData()

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 로컬 정의
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
