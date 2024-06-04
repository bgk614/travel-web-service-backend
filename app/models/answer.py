from sqlalchemy import Table, Column, Integer, Text, text, String, TIMESTAMP, MetaData, ForeignKey
from sqlalchemy.sql import func

metadata = MetaData()

answer = Table(
    "answer",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("question_id", Integer, ForeignKey("question.id", ondelete="CASCADE")),
    Column("answer", Text, nullable=False),
    Column("responder", String(255)),
    Column("created_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True),
    Column("updated_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True, onupdate=text('CURRENT_TIMESTAMP'))
)
