import os
from datetime import datetime
from urllib.parse import urlparse

import bs4
import psycopg2
import requests
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def connect_database():
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def validate_url(url: str) -> bool:
    correct_url = validators.url(url)
    correct_length = True if len(url) < 255 else False
    # correct_length = validators.length(url, 0, 255) ПОЧЕМУ НЕ РАБОТАЕТ???
    if correct_url is True and correct_length:
        return True
    return False


def normalize_url(url: str) -> str:
    lowercase_url = url.lower()
    normalized_url = urlparse(lowercase_url)
    return f'{normalized_url.scheme}://{normalized_url.netloc}'


def check_is_not_double(url: str) -> bool | int:
    conn = connect_database()
    sql = "SELECT * FROM urls WHERE name = (%s);"
    with conn.cursor() as curs:
        curs.execute(sql, (url, ))
        conn.commit()
        id = curs.fetchone()
        conn.close()
        if id is None:
            return True
        return id[0]


def save_to_db(website):
    pass


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',
                           url='')


@app.route('/urls', methods=['GET'])
def urls_list():
    sql_table_checks = '''SELECT
                            urls.id,
                            urls.name,
                            MAX(url_checks.created_at),
                            url_checks.status_code
                            FROM urls
                            LEFT JOIN url_checks
                            ON urls.id = url_checks.url_id
                            GROUP BY urls.id, url_checks.status_code
                            ORDER BY urls.id DESC;'''
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql_table_checks)
        data = curs.fetchall()
        conn.commit()
        conn.close()
    return render_template('urls.html',
                           urls=data)


@app.route('/', methods=['POST'])
def post_url():
    data = request.form.to_dict()
    url = data['url']
    normalized_url = normalize_url(url)
    doubleness = check_is_not_double(normalized_url)
    correctness = validate_url(normalized_url)
    if doubleness is not True:
        flash("Страница уже существует", "info")
        return redirect(url_for("get_url_info", id=doubleness))
    if correctness:
        conn = connect_database()
        sql = """INSERT INTO urls (name, created_at) 
                VALUES (%s, %s) RETURNING id;"""
        with conn.cursor() as curs:
            curs.execute(sql, (normalized_url, datetime.now(), ))
            conn.commit()
            id = curs.fetchone()[0]
            conn.close()
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("get_url_info", id=id))
    
    flash("Некорректный URL", "error")
    return render_template('index.html',
                           url=url), 422


@app.route('/urls/<int:id>', methods=['GET'])
def get_url_info(id):
    sql_url = """SELECT id, name, created_at
                    FROM urls
                    WHERE urls.id = (%s);"""
    sql_select = """SELECT id, created_at, status_code, h1, title, description
                        FROM url_checks
                        WHERE url_id = (%s) ORDER BY id DESC;"""
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql_url, (id, ))
        conn.commit()
        data_url = curs.fetchall()
        curs.execute(sql_select, (id, ))
        conn.commit()
        data_checks = curs.fetchall()
        conn.close()
    return render_template('url_id.html',
                           data_url=data_url,
                           data_checks=data_checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def post_url_check(id):
    sql_select = """SELECT name FROM urls WHERE id = (%s);"""
    sql_insert = """INSERT INTO url_checks (
                        url_id,
                        created_at,
                        status_code,
                        h1,
                        title,
                        description
                        )
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING (url_id);"""
    
    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql_select, (id, ))
        conn.commit()
        url = curs.fetchone()[0]
        status_code = get_status_code(url)
        tags = get_html_tags(url)  # (h1, title, description, )

        if status_code is None:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for("get_url_info", id=id))
        
        curs.execute(sql_insert,
                     (
                        id,
                        datetime.now(),
                        status_code,
                        tags[0],
                        tags[1],
                        tags[2],
                        )
                    )
        conn.commit()
        id = curs.fetchone()[0]
        conn.close()
        flash("Страница успешно проверена", "success")
    return redirect(url_for("get_url_info", id=id))


def get_status_code(url: str) -> int | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.HTTPError:
        pass
    except requests.exceptions.ConnectionError:
        pass
    # flash('Произошла ошибка при проверке', 'error')
    return None
    # return redirect(url_for("get_url_info", id=id))


def get_html_tags(url: str) -> tuple:
    try:
        response = requests.get(url)
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
        # flash('Произошла ошибка при проверке', 'error')
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

    conn = connect_database()
    with conn.cursor() as curs:
        curs.execute(sql_url)
        conn.commit()
        curs.execute(sql_checks)
        conn.commit()
        conn.close()
