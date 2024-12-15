from sqlalchemy import Table, Column, BigInteger, String, TIMESTAMP, MetaData, text

metadata = MetaData()

board = Table(
    "board",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("contents", String(255), nullable=False),
    Column("created_by", String(255), nullable=False),
    Column("created_at", TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=True),
    Column("click_count", BigInteger, default=0, nullable=False)  # 클릭 수를 저장하는 컬럼 추가
)