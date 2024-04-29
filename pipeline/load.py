"""This script is responsible for loading data into an RDS database"""

from os import environ as ENV
import logging
import pandas as pd
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


from transform import transform_and_apply_gpt
from extract import extract_cases


def get_db_connection() -> connect:
    """Returns db connection."""

    return connect(dbname=ENV["DB_NAME"],
                   user=ENV["DB_USER"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"],
                   cursor_factory=RealDictCursor)


def get_judge_id(judge_name: str, conn: connect) -> int:
    """Matches the judge name using a LIKE pattern to the names on the courts database"""

    try:
        like_pattern = f'%{judge_name}%'
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT judge_id
                    FROM judge
                    WHERE name ILIKE %s
                    """,
                        (like_pattern,)
                        )
            result = cur.fetchone()
            judge_id = result['judge_id']
        return judge_id
    except TypeError:
        return 1


def add_judge_id_to_dataframe(judge_name: str, cases_df: pd.DataFrame) -> None:
    """Add the judge id for a given judge to the cases dataframe"""

    cases_df["judge_id"] = judge_name


def upload_case_data(conn, cases_df):
    """Insert case data into case table in database."""

    with conn.cursor() as cur:
        query = """
                INSERT INTO transcript
                    (case_no, title, judge_id, verdict, summary, transcript_date)
                VALUES
                    (%s, %s, %s, %s, %s, %s)
                """
        data = list(zip(cases_df['case_no'], cases_df['title'], cases_df['judge_id'],
                    cases_df['verdict'], cases_df['summary'], cases_df['date']))

        cur.executemany(query, data)
    conn.commit()


def load_to_database(cases_df: pd.DataFrame) -> None:
    """Run all functions to load relevant information to courts database"""

    load_dotenv()

    conn = get_db_connection()

    cases_df['judge_id'] = cases_df['judge_name'].apply(
        get_judge_id, args=(conn,))

    upload_case_data(conn, cases_df)

    logging.info("Uploaded case and hearing date data successfully.")

    conn.close()


if __name__ == "__main__":

    cases = extract_cases(1)

    if not cases.empty:

        transformed_cases = transform_and_apply_gpt(cases)

        load_to_database(transformed_cases)
