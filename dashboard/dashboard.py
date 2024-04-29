import streamlit as st
from os import environ as ENV
import re
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
import pandas as pd
import altair as alt
from pywaffle import Waffle
from wordcloud import WordCloud, STOPWORDS


def get_db_connection(config) -> connect:
    """Returns db connection."""

    return connect(dbname=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"],
                   cursor_factory=RealDictCursor)


def extract_id_from_string(string: str) -> int:
    """Returns id in a bracket before string info."""
    return int(re.match(r"\((\d+)\)", string).group(1))


def get_judge_selection(conn: connect) -> st.selectbox:
    """Returns a Streamlit selectbox for individual judges."""

    with conn.cursor() as cur:
        query = """
                SELECT FORMAT('(%s) %s', judge_id, name) judge
                FROM judge
                """
        cur.execute(query)
        rows = cur.fetchall()

    rows = [item["judge"] for item in rows]

    judge_selection = st.selectbox(placeholder="select a judge",
                                   options=rows,
                                   index=None,
                                   label="judge selection",
                                   label_visibility="hidden")

    return judge_selection


def get_judge_from_db(conn: connect, id: int) -> tuple[dict, list[dict]]:
    """Returns a tuple of judge info and cases overseen."""

    with conn.cursor() as cur:
        judge_query = """
                        WITH judge_selected AS (
                            SELECT *
                            FROM judge
                            WHERE judge_id = %s
                        )
                        SELECT j.name, j.gender, j.appointed, t.type_name AS type, c.name AS circuit
                        FROM judge_selected AS j
                        JOIN judge_type AS t
                            ON j.judge_type_id = t.judge_type_id
                        JOIN circuit AS c
                            ON j.circuit_id = c.circuit_id
                        """
        cur.execute(judge_query, [id])
        judge = cur.fetchone()

        case_query = """
                        SELECT transcript_id AS id, case_no AS "case no", title
                        FROM transcript
                        WHERE judge_id = %s
                        """
        cur.execute(case_query, [id])
        cases = cur.fetchall()

    return judge, cases


def write_judge_profile(judge: dict) -> str:
    """Returns a formatted string of judge info."""

    return f"""name: {judge["name"]}  |  gender: {judge["gender"]}\n
judge type: {judge["type"]}\n
circuit: {judge["circuit"]}\n
appointed: {judge["appointed"]}
"""


if __name__ == "__main__":

    load_dotenv()
    conn = get_db_connection(ENV)

    st.set_page_config(page_title="Arelm Court Dashboard", page_icon="🏛", layout="wide",
                       initial_sidebar_state="expanded", menu_items=None)

    with st.sidebar:
        st.title("Arelm")
        st.subheader("lorem ipsum something about Arelm and the dashboard")
        st.text("")

    profiles, visualizations = st.columns([.35, .65], gap="medium")
    with profiles:
        # judge profile
        judge_profile_selection = get_judge_selection(conn)
        if judge_profile_selection:
            id = extract_id_from_string(judge_profile_selection)
            judge, cases = get_judge_from_db(conn, id)
            profile = write_judge_profile(judge)
            st.write(profile)
            st.dataframe(cases, hide_index=True,
                         use_container_width=True)
        else:
            st.write("*(no judge selected)*")

        # court case profile
        pass

    with visualizations:
        # controls/filters (may need columns to organise the controls)
        pass

        judge_cols = st.columns([.6, .4])
        with judge_cols[0]:
            # judge count over appointment date line graph
            pass

        with judge_cols[1]:
            # judge gender donut chart
            pass

        case_cols = st. columns([.6, .4])
        with case_cols[0]:
            # case count over doc date line graph
            pass

        with case_cols[1]:
            # summary word cloud
            pass

        verdict_cols = st.columns([.6, .4])
        with verdict_cols[0]:
            # verdict waffle chart
            pass

        with verdict_cols[1]:
            # verdict by circuit bar chart
            pass
