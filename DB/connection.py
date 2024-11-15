import sqlite3
from contextlib import closing
import os

# Database filename
database_path = 'DB/skincancer.db'

sql_files = [ # Address to SQL files for tables 
        'DB/model.sql',
        'DB/requests.sql',
        'DB/users.sql',
    ]

# DB connection
def connect():
    """Returns a connection object to the database"""
    return sqlite3.connect(database_path)

def execute_query(query, params=()):
    """Use this for queries without any returns such as Creation, Updating, or Deletion (Handler is responsible for implementing the correct logic of execution)."""
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(query, params)
        connection.commit()

def fetch_one(query, params=()):
    """Fetches only one result of the query (Use this for reading operations that are only looking for one result e.g. SELECT)"""
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()
    
def fetch_all(query, params=()):
    """Fetches all results of the query (Use this for queries that only read data e.g. SELECT * from users WHERE username = 'Bob123')"""
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()
    

# Function to execute an SQL script from a file
def execute_sql_file(filename):
    """This function executes external sql commands from a sql file"""
    with open(filename, 'r') as file:
        sql = file.read()
    execute_query(sql)

def setup_database():
    """This function carries out the responsibility of creating tables in the database."""
    for file in sql_files:
        if os.path.exists(file):
            execute_sql_file(file)
            print(f"Executed {file}")
        else:
            print(f"File {file} not found!")
