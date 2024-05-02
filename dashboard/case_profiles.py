"""Python script for extracting information for each case from an RDS"""

from os import environ as ENV

import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


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

    return st.text_input(label="case search",
                         label_visibility="hidden",
                         placeholder="Enter a case name/no.")


def get_case_information_by_name(conn, case_name):
    """Returns a dictionary of case details found by case name."""

    try:
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
    except Exception as e:
        st.error(f"Error fetching case information from database: {e}")


def get_case_information_by_case_number(conn, case_number):
    """Returns a dictionary of case details found by case number."""

    try:
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
    except Exception as e:
        st.error(f"Error fetching case information from database: {e}")


def find_case_query_type(case_query):
    """Returns a bool if the case query is name (true) or number (false)"""

    return all(str.isalpha(split) for split in case_query.split())


if __name__ == "__main__":
    pass
