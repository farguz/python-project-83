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
    correct_length = True if len(url) < 255 else False

    if correct_url is True and correct_length:
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
            id = curs.fetchone()
            if id is None:
                return True
            return id[0]


def get_status_code(url: str) -> int | None:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.HTTPError:
        pass
    except requests.exceptions.ConnectionError:
        pass
    return None


def get_html_tags(url: str) -> tuple | None:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        html_content = response.content
        html_object = bs4.BeautifulSoup(html_content, 'lxml')

        try:
            h1 = html_object.h1.string
        except Exception:
            h1 = ''
        try:
            title = html_object.title.string
        except Exception:
            title = ''
        try:
            description = html_object.find(
                'meta', attrs={'name': 'description'}
                ).get('content')
        except Exception:
            description = ''

        return h1, title, description

    except requests.exceptions.RequestException:
        return None
           
    
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