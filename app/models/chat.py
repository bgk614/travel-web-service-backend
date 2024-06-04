from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, text

metadata = MetaData()

chat = Table(
    "chat",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sender", String(50), nullable=False),
    Column("text", String(255), nullable=False),
    Column("created_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
)
