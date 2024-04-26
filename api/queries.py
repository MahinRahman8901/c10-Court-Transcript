'''Functions that query the database for information.'''

from dotenv import load_dotenv
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor, RealDictRow
from os import environ as ENV


def get_db_connection(config):
    '''Establishes connection to the database.'''
    conn = connect(user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"],
                   database=config["DB_NAME"],
                   cursor_factory=RealDictCursor)
    return conn


def get_table(conn, table: str) -> list[RealDictRow]:
    '''Returns table information as a list. 
    Only accepts table names: circuit, court_case, judge and judge_type.'''

    if table in ['circuit', 'court_case', 'judge', 'judge_type']:

        with conn.cursor() as cur:

            cur.execute(
                sql.SQL("SELECT * FROM {};").format(sql.Identifier(table)))
            rows = cur.fetchall()

        return rows

    return {'ERROR': f'Table {table} does not exist.'}


if __name__ == '__main__':

    load_dotenv()

    CONN = get_db_connection(ENV)

    result = get_table(CONN, 'court_case')

    print(type(result[0]))
