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

    if not isinstance(judge_id, int):
        raise TypeError("Judge id must be an integer.")

    with conn.cursor() as cur:

        cur.execute(f"""SELECT * FROM judge
                            WHERE judge_id = {judge_id};""")

        judge = cur.fetchone()

    if not judge:
        return {'ERROR': f"No judge with ID {judge_id} exists."}

    return judge


def get_case_by_case_no(conn, case_no: str) -> list[RealDictRow]:
    '''Returns all information about a specific case.'''

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM court_case WHERE case_no_id = %s;""", (case_no,))
            case = cur.fetchone()

        return case

    except Exception as e:
        print("Error:", e)
        return None


def filter_judges(conn, filter_by: str, id: str) -> list[RealDictRow]:
    '''Filters judges by circuit or judge_type.'''

    if filter_by not in ['circuit_id', 'judge_type']:
        raise ValueError(f"Cannot filter by {filter_by}")

    with conn.cursor() as cur:

        cur.execute(sql.SQL("""SELECT * from judge WHERE {} = {}""").format(
            sql.Identifier(filter_by), sql.SQL(f'{id}')))

        judges = cur.fetchall()

    return judges


def filter_cases_by_judge(conn, judge_id: int) -> list[RealDictRow]:
    '''Filters cases by judge id.'''
    pass


def search_cases(conn, search: str) -> list[RealDictRow]:
    '''Returns cases whose titles contain a particular substring.'''
    pass


if __name__ == '__main__':

    load_dotenv()

    CONN = get_db_connection(ENV)

    result = filter_judges(CONN, 'circuit_id', 5)

    print(len(result))
