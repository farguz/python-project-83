import os

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("no such var in env")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=4,
    timeout=20,
    open=True
)

