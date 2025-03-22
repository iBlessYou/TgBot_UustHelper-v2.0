import os

import config
from psycopg2 import connect

def connection():
    con = connect(
        host=config.postgresql_config.hostname,
        database=config.postgresql_config.database,
        user=config.postgresql_config.username,
        password=config.postgresql_config.password,
        port=config.postgresql_config.port)

    return con, con.cursor()

def sql_INSERT(table, column_list, *values_list):
    count = ("%s," * len(values_list))[:-1]
    column_string = ",".join(column_list)
    con, cur = connection()
    cur.execute(f'INSERT INTO {table} ({column_string}) VALUES ({count})', (*values_list,))
    con.commit(); con.close()

def sql_SELECT(table, column_key, key_value, column_list):
    column_string = ",".join(column_list)
    con, cur = connection()
    cur.execute(F"SELECT {column_string} FROM {table} WHERE {column_key} = %s", (key_value,))
    data = cur.fetchall()
    con.commit(); con.close()
    return data

def sql_UPDATE(table, column_key, key_value, column_list, *values_list):
    column_string = ",".join([f"{column} = %s" for column in column_list])
    con, cur = connection()
    cur.execute(f"UPDATE {table} SET {column_string} WHERE {column_key} = %s", (*values_list, key_value))
    con.commit(); con.close()