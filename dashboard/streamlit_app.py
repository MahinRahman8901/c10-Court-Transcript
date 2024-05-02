import streamlit as st
from os import environ as ENV
import re
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from psycopg2 import connect
import pandas as pd
import altair as alt
from pywaffle import Waffle
from wordcloud import WordCloud, STOPWORDS

from layout import set_page_config, get_sidebar
from charts import get_db_connection, get_gender_donut_chart, get_waffle_chart, get_judge_count_line_chart


def extract_id_from_string(string: str) -> int:
    """Returns id in a bracket before string info."""
    return int(re.match(r"\((\d+)\)", string).group(1))


# ========== FUNCTIONS: SELECTIONS ==========
def get_judge_selection(conn: connect, key: str) -> st.selectbox:
    """Returns a Streamlit selectbox for individual judges."""

    with conn.cursor() as cur:
        query = """
                SELECT FORMAT('(%s) %s', judge_id, name) judge
                FROM judge
                """
        cur.execute(query)
        rows = cur.fetchall()

    rows = [item["judge"] for item in rows]

    judge_selection = st.selectbox(key=key,
                                   placeholder="Select a judge",
                                   options=rows,
                                   index=None,
                                   label="judge selection",
                                   label_visibility="hidden")

    return judge_selection


def get_circuit_selection(conn: connect, key: str) -> st.multiselect:
    """Returns a Streamlit multiselect for circuits."""

    with conn.cursor() as cur:
        query = """
                SELECT name AS circuit
                FROM circuit
                """
        cur.execute(query)
        rows = cur.fetchall()

    rows = [item["circuit"] for item in rows]

    judge_selection = st.multiselect(key=key,
                                     placeholder="select circuit(s)",
                                     options=rows,
                                     label="judge selection",
                                     label_visibility="hidden",)

    return judge_selection


def get_gender_selection(conn: connect, key: str) -> st.selectbox:
    """Returns a Streamlit selectbox for genders."""

    with conn.cursor() as cur:
        query = """
                SELECT DISTINCT gender
                FROM judge
                """
        cur.execute(query)
        rows = cur.fetchall()

    rows = [item["gender"] for item in rows]

    judge_selection = st.selectbox(key=key,
                                   placeholder="Select a gender",
                                   options=rows,
                                   index=None,
                                   label="gender selection",
                                   label_visibility="hidden")

    return judge_selection


def get_date_selection(key: str) -> st.date_input:
    """Returns a Streamlit date input for judge appointment."""

    return st.date_input(key=key,
                         value=(),
                         min_value=None, max_value=None,
                         format="YYYY/MM/DD",
                         label="date selection",
                         label_visibility="hidden")


def get_judge_type_selection(conn: connect, key: str) -> st.selectbox:
    """Returns a Streamlit selectbox for judge types."""

    with conn.cursor() as cur:
        query = """
                SELECT type_name
                FROM judge_type
                """
        cur.execute(query)
        rows = cur.fetchall()

    rows = [item["type_name"] for item in rows]

    judge_selection = st.selectbox(key=key,
                                   placeholder="Select a judge type",
                                   options=rows,
                                   index=None,
                                   label="judge type selection",
                                   label_visibility="hidden")

    return judge_selection


# ========== FUNCTIONS: DATABASE ===========
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


def get_data_from_db(conn: connect) -> pd.DataFrame:
    """Returns all data from the database as a pd.DF."""

    with conn.cursor() as cur:
        query = """
                SELECT t.transcript_id, t.case_no, t.transcript_date, t.title, t.summary, t.verdict,
                    j.judge_id, j.name AS judge, j.appointed, j.gender,
                    jt.judge_type_id AS type_id, jt.type_name,
                    c.circuit_id, c.name AS circuit_name
                FROM transcript AS t
                JOIN judge AS j
                    ON t.judge_id = j.judge_id
                JOIN judge_type AS jt
                    ON j.judge_type_id = jt.judge_type_id
                JOIN circuit AS c
                    ON j.circuit_id = c.circuit_id
                """
        cur.execute(query)
        rows = cur.fetchall()

    df = pd.DataFrame(rows)

    return df


if __name__ == "__main__":

    load_dotenv()
    CONN = get_db_connection(ENV)

    set_page_config()

    get_sidebar()

    st.altair_chart(get_gender_donut_chart(CONN))

    st.pyplot(get_waffle_chart(CONN, '593'))

    profiles, visualizations = st.columns([.3, .7], gap="medium")
    with profiles:
        # judge profile
        judge_profile_selection = get_judge_selection(
            CONN, "judge_profile_selection")
        if judge_profile_selection:
            id = extract_id_from_string(judge_profile_selection)
            judge, cases = get_judge_from_db(CONN, id)
            profile = write_judge_profile(judge)
            st.write(profile)
            st.dataframe(cases, hide_index=True,
                         use_container_width=True)
        else:
            st.write("*(no judge selected)*")

        # court case profile
        pass

    with visualizations:
        data = get_data_from_db(CONN)

        # controls/filters (may need columns to organise the controls)
        controls = st.columns(5)
        with controls[0]:
            viz_type_selection = get_judge_type_selection(
                CONN, "viz_type_selection")
        with controls[1]:
            viz_circuit_selection = get_circuit_selection(
                CONN, "viz_circuit_selection")
        with controls[2]:
            viz_gender_selection = get_gender_selection(
                CONN, "viz_gender_selection")
        with controls[3]:
            viz_date_selection = get_date_selection(
                "viz_date_selection")
        with controls[4]:
            viz_judge_selection = get_judge_selection(
                CONN, "viz_judge_selectbox")

        judge_cols = st.columns([.6, .4])
        with judge_cols[0]:
            # judge count over appointment date line graph
            st.altair_chart(get_judge_count_line_chart(CONN))

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
