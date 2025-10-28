import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        port=3307,
        user='root',
        password='',
        database='habit_tracker',
        cursorclass=pymysql.cursors.DictCursor
    )