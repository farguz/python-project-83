from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .utils import (
    check_is_not_double,
    connect_database,
    get_html_tags,
    get_status_code,
    normalize_url,
    validate_url,
)

handlers_blueprint = Blueprint('handlers_blueprint', __name__)
get_url_info_link = 'handlers_blueprint.get_url_info'


@handlers_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html',
                           url='')


@handlers_blueprint.route('/urls', methods=['GET'])
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


@handlers_blueprint.route('/urls', methods=['POST'])
def post_url():
    data = request.form.to_dict()
    url = data['url']
    normalized_url = normalize_url(url)
    doubleness = check_is_not_double(normalized_url)
    correctness = validate_url(normalized_url)
    if doubleness is not True:
        flash('Страница уже существует', 'info')
        return redirect(
            url_for(get_url_info_link, id=doubleness)
            )
    if correctness:
        conn = connect_database()
        sql = """INSERT INTO urls (name, created_at) 
                VALUES (%s, %s) RETURNING id;"""
        with conn.cursor() as curs:
            curs.execute(sql, (normalized_url, datetime.now(), ))
            conn.commit()
            id = curs.fetchone()[0]
            conn.close()
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for(get_url_info_link, id=id))
    
    flash('Некорректный URL', 'error')
    return render_template('index.html',
                           url=url), 422


@handlers_blueprint.route('/urls/<int:id>', methods=['GET'])
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


@handlers_blueprint.route('/urls/<int:id>/checks', methods=['POST'])
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
        url = curs.fetchone()[0]
        status_code = get_status_code(url)
        tags = get_html_tags(url)  # (h1, title, description, )

        if status_code is None:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for(get_url_info_link, id=id))
        
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
        flash('Страница успешно проверена', 'success')
    return redirect(url_for(get_url_info_link, id=id))

