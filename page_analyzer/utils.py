import os
from urllib.parse import urlparse

import bs4
import requests
import validators
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("no such var in env")

pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=10,
    timeout=10,
)


def validate_url(url: str) -> bool:
    correct_url = validators.url(url)
    correct_length = len(url) < 255

    if correct_url and correct_length:
        return True
    return False


def normalize_url(url: str) -> str:
    lowercase_url = url.lower()
    normalized_url = urlparse(lowercase_url)
    return f'{normalized_url.scheme}://{normalized_url.netloc}'


def check_is_not_double(url: str) -> bool | int:
    sql = "SELECT id FROM urls WHERE name = (%s);"

    with pool.connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql, (url, ))
            row = curs.fetchone()
            if row is None:
                return True
            return row[0]


def get_html_data(url: str) -> tuple | None:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        html_content = response.content
        html_object = bs4.BeautifulSoup(html_content, 'lxml')
        
        h1 = html_object.h1.string if html_object.h1 else ''
        title = html_object.title.string if html_object.title else ''
        description = html_object.find(
                'meta', attrs={'name': 'description'}
                ).get('content') 
        description = description if description else ''
        status_code = response.status_code

    except Exception as e:
        print(f"Logging error: {e}")
        return None

    return h1[:255], title[:255], description[:255], status_code
           
    
def create_table():
    sql_url = '''
    CREATE TABLE IF NOT EXISTS urls (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(255) NOT NULL UNIQUE,
        created_at TIMESTAMP NOT NULL
    );'''

    sql_checks = '''
    CREATE TABLE IF NOT EXISTS url_checks  (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        url_id BIGINT REFERENCES urls (id) NOT NULL,
        status_code INT,
        h1 VARCHAR(255),
        title VARCHAR(255),
        description VARCHAR(255),
        created_at TIMESTAMP NOT NULL
    );'''

    with pool.connection() as conn:
        with conn.cursor() as curs:
            curs.execute(sql_url)
            curs.execute(sql_checks)
        conn.commit()