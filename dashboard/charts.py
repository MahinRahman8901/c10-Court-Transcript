'''This file contains charts for the streamlit dashboard.'''

import streamlit as st
import pandas as pd
import altair as alt
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor, RealDictRow
from dotenv import load_dotenv
from os import environ as ENV
import matplotlib.pyplot as plt
from pywaffle import Waffle


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


def get_judge_verdicts(conn: connect, judge_id: str, verdict: str) -> int:
    '''Returns the number of cases with a certain verdict.'''

    with conn.cursor() as cur:
        query = sql.SQL("""
                SELECT transcript_id, verdict FROM transcript
                WHERE verdict ILIKE '%{}%'
                AND judge_id = {}
                """).format(sql.SQL(verdict.lower()), sql.SQL(judge_id))
        cur.execute(query)
        rows = cur.fetchall()

    return len(rows)


def get_judge_appointed(conn: connect):
    query = """
                SELECT appointed, count(judge_id) FROM judge
                GROUP BY appointed;
                """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return pd.DataFrame(rows)


def get_gender_donut_chart(conn: connect):

    data = get_judge_genders(conn)

    chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
        theta='count',
        color=alt.Color('gender').title('Gender')
    )

    return chart


def get_waffle_chart(conn: connect, judge_id):

    claimants = get_judge_verdicts(conn, judge_id, 'claimant')
    defendants = get_judge_verdicts(conn, judge_id, 'defendant')

    fig = plt.figure(
        FigureClass=Waffle,
        rows=5,
        figsize=(20, 5),
        values={'Claimants': claimants, 'Defendants': defendants}
    )

    return fig


def get_judge_count_line_chart(conn: connect, judge_id):


if __name__ == "__main__":

    load_dotenv()

    CONN = get_db_connection(ENV)

    result = get_judge_verdicts(CONN, '3', 'defendant')

    print(result)
