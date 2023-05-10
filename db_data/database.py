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
    CREATE TABLE IF NOT EXISTS stores(
        id serial primary key,
        author_id varchar(100) references users(user_id)  on DELETE CASCADE ,
        author_name varchar(100) not null,
        story_title varchar(255) not null,
        story text not null,
        public boolean not null,
        time timestamp default now()
    )'''
    cur = con.cursor()
    cur.execute(query)
    cur.execute(story_query)
    con.commit()
    cur.close()


def get_user(user_id: str):
    query = 'select * from users where user_id = %s'
    cur.execute(query, (user_id,))
    user = cur.fetchone()
    return user


def get_all_stories():
    query = 'select * from stores where public = %s'
    cur.execute(query, (True,))
    stores = cur.fetchall()
    return stores


def get_my_stories(user_id: str):
    query = 'select * from stores where author_id = %s'
    cur.execute(query, (user_id,))
    stores = cur.fetchall()
    return stores
