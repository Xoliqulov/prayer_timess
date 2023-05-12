import os
import psycopg2

con = psycopg2.connect(
    user='postgres',
    database='postgres',
    password=os.getenv('DB_PASS'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)

cur = con.cursor()


def create_table():
    query = '''
    CREATE TABLE IF NOT EXISTS users(
        id serial not null,
        user_id varchar(100) unique primary key,
        name varchar(50) not null,
        username varchar(50),
        time timestamp default now()
    )'''

    story_query = '''
    CREATE TABLE IF NOT EXISTS message(
        id serial primary key,
        user_id varchar(100) not null,
        username varchar(255),
        msg text ,
        time timestamp default now()
    )'''
    cur = con.cursor()
    cur.execute(query)
    cur.execute(story_query)
    con.commit()
    cur.close()


def messages():
    cur.execute("SELECT username, msg FROM message")  # noqa
    rows = cur.fetchall()
    return rows


def write_users(id_, name, user):
    query = '''
    INSERT INTO users(user_id, name, username) VALUES (%s, %s, %s);
    '''
    cur.execute(query, (id_, name, user))
    con.commit()


def check_id():
    cur.execute("SELECT user_id FROM users")  # noqa
    rows = cur.fetchall()
    return rows


def write_msg(id_, user, msg):
    query = '''
    INSERT INTO message(user_id, username, msg) VALUES (%s, %s, %s);
    '''
    cur.execute(query, (id_, user, msg))
    con.commit()
