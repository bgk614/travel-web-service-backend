from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Text

metadata = MetaData()

plans = Table(
    'plans', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('description', Text, nullable=False),
    Column('region', String(100), nullable=False),
    Column('category', String(100), nullable=False),
    Column('userid', String(100), ForeignKey('users.userid'), nullable=False),
    Column('likes', Integer, default=0),
    Column('images', Text, nullable=True),
    Column('itinerary', Text, nullable=True)
)
