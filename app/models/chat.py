from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

chat = Table(
    "chat",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sender", String(50)),
    Column("text", String(255)),
)