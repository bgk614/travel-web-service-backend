# from sqlalchemy import Table, Column, Integer, String, Text, MetaData, TIMESTAMP, text as sa_text
# from app.database import Base

# metadata = MetaData()

# place = Table(
#     "place", metadata,
#     Column('id', Integer, primary_key=True, index=True),
#     Column('name', String(255), index=True),
#     Column('address', String(255), index=True),
#     Column('description', String(255), index=True),
#     Column('image', String(255), index=True),
#     Column('clicks', Integer, default=0)
# )
# board = Table(
#     "board", metadata,
#     Column('idx', Integer, primary_key=True, autoincrement=True),
#     Column('title', String(255)),
#     Column('contents', String(255)),
#     Column('created_by', String(255)),
#     Column('created_at', TIMESTAMP, server_default=sa_text("CURRENT_TIMESTAMP"))
# )

# chat = Table(
#     'chat', metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True),
#     Column('sender', String(50)),
#     Column('text', Text),
#     Column('timestamp', TIMESTAMP, server_default=sa_text('CURRENT_TIMESTAMP'))
# )

# users = Table(
#     'users', metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True),
#     Column('userid', Integer, primary_key=True),
#     Column('nickname', String(50)),
#     Column('password', String(100)),  # 실제로는 비밀번호 해싱 필요
#     Column('name', String(100)),
#     Column('phone', String(15)),
#     Column('email', String(100), unique=True, index=True),
#     Column('address', String(255))
# )

