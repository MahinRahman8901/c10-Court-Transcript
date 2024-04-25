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


def get_judge_id(conn: connect, judge_name: str) -> int | None:
    """Matches the judge name to the names on the courts database"""

    with conn.cursor() as cur:
        cur.execute("""
                SELECT judge_id
                FROM judges
                WHERE name = %s
                """,
                    (judge_name,)
                    )
    result = cur.fetchone()
    if result:
        return result[0]
    return None


def add_judge_id_to_dataframe(judge_name: str, cases_df: pd.DataFrame) -> None:
    """Add the judge id for a given judge to the cases dataframe"""

    cases_df["judge_id"] = judge_name


def upload_hearing_dates_data(conn: connect, cases_df: pd.DataFrame) -> None:
    """Insert hearing dates data into hearing dates table in database"""

    with conn.cursor() as cur:
        query = """
                        INSERT INTO hearing_dates
                            (date, case_no_id)
                        VALUES
                            (%s, %s)
                        """
        cur.executemany(query,
                        [cases_df["date"], cases_df["case_no_id"]])
    conn.commit()


def upload_cases_data(conn: connect, cases_df: pd.DataFrame) -> None:
    """Insert case data into case table in database."""

    with conn.cursor() as cur:
        query = """
                        INSERT INTO cases
                            (judge_id, verdict, summary)
                        VALUES
                            (%s, %s, %s)
                        """
        cur.executemany(query,
                        [cases_df["judge_id"], cases_df["verdict"], cases_df['summary']])
    conn.commit()


def load_to_database(cases_df: pd.DataFrame) -> None:
    """Run all functions to load relevant information to courts database"""

    load_dotenv()

    conn = get_db_connection()

    cases_df['judge_id'] = cases_df['judge_name'].apply(get_judge_id)

    upload_cases_data(conn, cases_df)

    upload_hearing_dates_data(conn, cases_df)

    logging.info("Uploaded case and hearing date data successfully.")

    conn.close()


if __name__ == "__main__":

    cases = extract_cases(1)

    transform_and_apply_gpt(cases)

    load_to_database(cases)
