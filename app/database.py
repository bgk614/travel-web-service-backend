# database.py
import json
from databases import Database  # 올바른 라이브러리에서 Database 클래스를 임포트
from sqlalchemy import create_engine, MetaData

# JSON 파일에서 설정 불러오기
with open('secrets.json', 'r') as file:
    secrets = json.load(file)

db_info = secrets['DATABASE_URL']
DATABASE_URL = f"mysql://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/{db_info['dbname']}"

# Database 인스턴스 생성
database = Database(DATABASE_URL)

# database = Database(DATABASE_URL)
metadata = MetaData()

