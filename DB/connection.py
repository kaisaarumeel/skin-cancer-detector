import sqlite3
from contextlib import closing
import os

# Database filename
database_path = 'DB/skincancer.db'

sql_files = [ # Tables 
        'DB/model.sql',
        'DB/requests.sql',
        'DB/users.sql',
    ]

# DB connection
def connect():
    return sqlite3.connect(database_path)

def execute_query(query, params=()):
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(query, params)
        connection.commit()

def fetch_one(query, params=()):
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()
    
def fetch_all(query, params=()):
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()
    

# Function to execute an SQL script from a file
def execute_sql_file(filename):
    with open(filename, 'r') as file:
        sql = file.read()
    execute_query(sql)

def setup_database():
    for file in sql_files:
        if os.path.exists(file):
            execute_sql_file(file)
            print(f"Executed {file}")
        else:
            print(f"File {file} not found!")

if __name__ == '__main__':
    # First, run all the SQL scripts to create the necessary tables
    setup_database()