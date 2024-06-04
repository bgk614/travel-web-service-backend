from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, Text, text

metadata = MetaData()

notice = Table(
    "notice",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True),
    Column("updated_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True, onupdate=text('CURRENT_TIMESTAMP'))
)
