from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, MetaData, text

metadata = MetaData()

question = Table(
    "question",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("question", Text, nullable=False),
    Column("asker", String(255)),
    Column("created_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True),
    Column("updated_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True, onupdate=text('CURRENT_TIMESTAMP'))
)
