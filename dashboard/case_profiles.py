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

# TODO: if statements for if a number or name is passed
# TODO: ILIKE query for matching name but = for case number


def get_case_information_by_name(conn: connect, case_name) -> st.selectbox:
    """Returns a Streamlit selectbox for individual cases."""

    with conn.cursor() as cur:
        query = """
                SELECT t.title, t.transcript_date, j.judge_name
                FROM transcript AS t
                LEFT JOIN judge AS j
                ON t.judge_id = j.judge_id
                WHERE t.title ILIKE %s
                """,
        (case_name)
        cur.execute(query)
        rows = cur.fetchall()

    rows = [item["judge"] for item in rows]

    judge_selection = st.selectbox(placeholder="select a judge",
                                   options=rows,
                                   index=None,
                                   label="judge selection",
                                   label_visibility="hidden")

    return judge_selection


def get_case_information_by_name(conn, case_name):
    """Returns a Streamlit selectbox for individual cases."""

    with conn.cursor() as cur:
        query = """
                SELECT t.title, t.transcript_date, j.name
                FROM transcript AS t
                LEFT JOIN judge AS j
                ON t.judge_id = j.judge_id
                WHERE t.title ILIKE %s
                """
        cur.execute(query, ('%' + case_name + '%',))
        rows = cur.fetchone()

    return rows


if __name__ == "__main__":
    pass
