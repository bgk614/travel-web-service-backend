from sqlalchemy import create_engine
from models import metadata
import json

# Load database configuration from secrets.json
with open('../secrets.json', 'r') as file:
    secrets = json.load(file)

db_info = secrets['DATABASE_URL']
# Configure the MySQL database URL
DATABASE_URL = f"mysql+pymysql://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/{db_info['dbname']}"

# Create an SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create all tables in the database
metadata.create_all(engine)
print("Tables created successfully")
