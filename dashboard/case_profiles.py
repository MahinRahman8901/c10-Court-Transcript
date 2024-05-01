"""Python script for extracting information for each case from an RDS"""

from os import environ as ENV

import streamlit as st
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
import pandas as pd


def get_db_connection(config) -> connect:
    """Returns db connection."""

    return connect(dbname=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"],
                   cursor_factory=RealDictCursor)


def get_case_query() -> st.text_input:
    """Returns a Streamlit input box that catches a queried case by name or number"""

    return st.text_input(label="Enter a case name/no.")


def get_case_information_by_name(conn, case_name):
    """Returns a dictionary of case details found by case name."""

    with conn.cursor() as cur:
        query = """
                SELECT t.title, t.transcript_date, t.verdict, t.summary, j.name
                FROM transcript AS t
                LEFT JOIN judge AS j
                ON t.judge_id = j.judge_id
                WHERE t.title ILIKE %s
                """
        cur.execute(query, ('%' + case_name + '%',))
        rows = cur.fetchone()

    return rows


def get_case_information_by_case_number(conn, case_number):
    """Returns a dictionary of case details found by case number."""

    with conn.cursor() as cur:
        query = """
                SELECT t.title, t.transcript_date, t.summary, t.verdict, j.name
                FROM transcript AS t
                LEFT JOIN judge AS j
                ON t.judge_id = j.judge_id
                WHERE t.case_no = %s
                """
        cur.execute(query, (case_number,))
        rows = cur.fetchone()

    return rows


def find_case_query_type(case_query):
    """Returns a bool if the case query is name (true) or number (false)"""

    return all(str.isalpha(split) for split in case_query.split())


if __name__ == "__main__":
    pass
