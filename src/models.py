from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, DECIMAL, MetaData

metadata = MetaData()

infrastructure_reports = Table(
    "infrastructure_reports",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(20)),
    Column("comment", Text),
    Column("image", Text),
    Column("timestamp", TIMESTAMP),
    Column("latitude", DECIMAL(9, 6)),
    Column("longitude", DECIMAL(9, 6)),
)
