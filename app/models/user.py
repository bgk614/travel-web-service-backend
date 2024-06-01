from sqlalchemy import Date, Table, Column, Integer, String, MetaData

metadata = MetaData()

user = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('userid', String(50), nullable=False, unique=True),
    Column('nickname', String(50)),
    Column('password', String(100)),
    Column('name', String(100)),
    Column('phone', String(15)),
    Column('email', String(100), unique=True, index=True),
    Column('birthdate', Date, nullable=False) 
)
