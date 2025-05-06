import asyncio
from psycopg_pool import ConnectionPool
from app.core.config import get_settings
from langgraph.checkpoint.postgres import PostgresSaver

settings = get_settings()

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

DATABASE_URL = settings.DATABASE_URL

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    max_size=20,
    kwargs=connection_kwargs,
)

checkpointer = PostgresSaver(pool)
    



