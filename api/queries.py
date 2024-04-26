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


def get_judge_by_id(conn, judge_id: int) -> list[RealDictRow]:
    '''Returns all information about a specific judge.'''

    try:
        with conn.cursor() as cur:

            cur.execute(sql.SQL("""SELECT * FROM judge
                                WHERE judge_id = {};""").format(sql.Identifier(judge_id)))

            judge = cur.fetchone()

        return judge

    except:
        return {'ERROR': f"No judge with ID {judge_id} exists."}


def get_case_by_case_no(conn, case_no: str) -> list[RealDictRow]:
    '''Returns all information about a specific case.'''

    try:
        with conn.cursor() as cur:

            cur.execute(sql.SQL("""SELECT * FROM court_case
                                WHERE case_no_id = {};""").format(sql.Identifier(case_no)))

            case = cur.fetchone()

        return case

    except:
        return {"ERROR": f"No case with case number {case_no}."}


def filter_judges(filter_by: str) -> list[RealDictRow]:
    '''Filters judges by circuit or judge_type.'''
    pass


def filter_cases_by_judge(judge_id: int):
    '''Filters cases by judge id.'''
    pass


if __name__ == '__main__':

    load_dotenv()

    CONN = get_db_connection(ENV)

    result = get_table(CONN, 'court_case')

    print(type(result[0]))
