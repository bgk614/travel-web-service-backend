from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

board = Table(
    "board",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255)),
    Column("contents", String(255)),
    Column("created_by", String(50)),
    Column("created_at", String[50])
)