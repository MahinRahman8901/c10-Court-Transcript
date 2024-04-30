'''This file contains charts for the streamlit dashboard.'''

import streamlit as st
import pandas as pd
import altair as alt
from psycopg2 import connect
from psycopg2.extras import RealDictCursor, RealDictRow
from dotenv import load_dotenv
from os import environ as ENV


def get_db_connection(config) -> connect:
    """Returns db connection."""

    return connect(dbname=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"],
                   cursor_factory=RealDictCursor)


def get_judge_genders(conn: connect) -> pd.DataFrame:
    '''Queries the database for judge genders.'''

    with conn.cursor() as cur:
        query = """
                SELECT gender, count(judge_id) FROM judge
                GROUP BY gender;
                """
        cur.execute(query)
        rows = cur.fetchall()

    return pd.DataFrame(rows)


def get_gender_donut_chart(conn: connect):

    data = get_judge_genders(conn)

    chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
        theta='count',
        color='gender:N'
    )

    return chart


if __name__ == "__main__":

    load_dotenv()

    CONN = get_db_connection(ENV)

    result = get_judge_genders(CONN)

    print(result)
