'''Functions that query the database for information.'''

from os import environ as ENV

from dotenv import load_dotenv
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor, RealDictRow


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
    Only accepts table names: circuit, transcript, judge and judge_type.'''

    if table in ['circuit', 'transcript', 'judge', 'judge_type']:

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
                """SELECT * FROM transcript WHERE case_no_id = %s;""", (case_no,))
            case = cur.fetchone()

        return case

    except Exception as e:
        print("Error:", e)
        return None


def filter_judges(conn, filter_by: dict) -> list[RealDictRow]:
    '''Filters judges by circuit and/or judge_type.'''

    if not all([f in ['circuit_id', 'judge_type'] for f in filter_by]):
        raise ValueError(f"Invalid filter.")

    with conn.cursor() as cur:

        if len(filter_by) == 1 and len(id) == 1:

            cur.execute(sql.SQL("""SELECT * FROM judge WHERE {} = {}""").format(
                sql.Identifier(filter_by[0]), sql.SQL(f'{id[0]}')))

            judges = cur.fetchall()

    return judges


def filter_cases_by_judge(conn, judge_id: int) -> list[RealDictRow]:
    '''Filters cases by judge id.'''

    if not isinstance(judge_id, int):
        raise TypeError("Judge id must be an integer.")

    with conn.cursor() as cur:

        cur.execute(
            sql.SQL(f"""SELECT * FROM transcript WHERE judge_id = {judge_id} """))

        cases = cur.fetchall()

    return cases


def search_cases(conn, search: str) -> list[RealDictRow]:
    '''Returns cases whose titles contain a particular substring.'''

    with conn.cursor() as cur:

        cur.execute(sql.SQL(
            "SELECT * FROM transcript WHERE title ILIKE '%{}%'").format(sql.SQL(search)))

        cases = cur.fetchall()

    return cases


if __name__ == '__main__':

    load_dotenv()

    CONN = get_db_connection(ENV)

    result = search_cases(CONN, "Palmer")

    print(result)
