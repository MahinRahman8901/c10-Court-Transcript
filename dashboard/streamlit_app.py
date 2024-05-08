from os import environ as ENV
import re
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from psycopg2 import connect
import streamlit as st
from st_pages import Page, show_pages
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
from pywaffle import Waffle

from layout import set_page_config, get_sidebar
from charts import (get_db_connection,
                    get_data_from_db,
                    get_filtered_data,
                    get_gender_donut_chart,
                    get_waffle_chart,
                    get_summary_texts_from_db,
                    generate_word_cloud,
                    get_judge_count_line_chart,
                    get_verdicts_stacked_bar_chart,
                    get_case_count_line_chart)

from case_profiles import (get_case_query,
                           get_case_information_by_name,
                           get_case_information_by_case_number,
                           find_case_query_type)


def extract_id_from_string(string: str) -> int:
    """Returns id in a bracket before string info."""

    if string:
        return int(re.match(r"\((\d+)\)", string).group(1))

    return None


# ========== FUNCTIONS: SELECTIONS ==========
def get_judge_selection(conn: connect, key: str, placeholder: str) -> st.selectbox:
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
                                   placeholder=placeholder,
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
                                     placeholder="circuit(s)",
                                     options=rows,
                                     default=None,
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
                                   placeholder="gender",
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
                                   placeholder="type",
                                   options=rows,
                                   index=None,
                                   label="judge type selection",
                                   label_visibility="hidden")

    return judge_selection


def compile_inputs_as_dict(conn: connect, judge_type: str = None, circuits: str = None,
                           gender: str = None, date: tuple = None, judge: str = None) -> dict:
    """Returns input widget returns as a single dictionary"""

    with conn.cursor() as cur:
        if judge_type:
            query_type = """
                            SELECT judge_type_id
                            FROM judge_type
                            WHERE type_name = %s
                            """
            cur.execute(query_type, [judge_type])
            judge_type = cur.fetchone()["judge_type_id"]

        if circuits:
            placeholders = ', '.join([f"'{circuit}'" for circuit in circuits])
            st.write(placeholders)
            query_circuit = f"""
                            SELECT circuit_id
                            FROM circuit
                            WHERE name IN ({placeholders})
                            """
            cur.execute(query_circuit)
            circuits = cur.fetchall()
            circuits = [circuit["circuit_id"] for circuit in circuits]

    if judge:
        judge = extract_id_from_string(judge)

    inputs = {"judge_id": judge,
              "circuit_id": circuits,
              "gender": gender,
              "appointed": date,
              "type_id": judge_type}

    return inputs


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

    return f"""Name: {judge["name"]}  |  Gender: {judge["gender"]}\n
Judge Type: {judge["type"]}\n
Circuit: {judge["circuit"]}\n
Appointed: {judge["appointed"]}
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

    show_pages(
        [
            Page("streamlit_app.py", "Searches", "🔍"),
            Page("pages/1_Charts.py", "Charts", "📈")
        ]
    )

    data = get_data_from_db(CONN)

    searches = st.columns([.35, .35, .3])

    with searches[0]:
        st.subheader(body="Judge Search", divider="grey")
        judge_profile_selection = get_judge_selection(
            CONN, "judge_profile_selection", "Enter judge name:")
        if judge_profile_selection:
            id = extract_id_from_string(judge_profile_selection)
            judge, cases = get_judge_from_db(CONN, id)
            profile = write_judge_profile(judge)
            st.write(profile)
            if cases:
                st.dataframe(cases, hide_index=True,
                             use_container_width=True)
        else:
            pass
            # st.write("*(no judge selected)*")

    with searches[1]:
        st.subheader(body="Case Search", divider="grey")
        case_search = get_case_query()

        if case_search:
            if find_case_query_type(case_search):
                case_info = get_case_information_by_name(
                    CONN, case_search)
            else:
                case_info = get_case_information_by_case_number(
                    CONN, case_search)

            if case_info is None:
                st.write("Case not found.")
        else:

            case_info = False

        if case_info:
            title = case_info.get("title")
            date = case_info.get("transcript_date")
            judge_name = case_info.get("name")
            summary = case_info.get("summary")
            verdict = case_info.get("verdict")
            st.write(f"Title: {title}")
            st.write(f"DOC: {date}")
            st.write(f"Judge Name: {judge_name}")
            st.write(f"Summary: {summary}")
            st.write(f"Verdict: {verdict}")
        else:
            pass

    with searches[2]:
        st.subheader("Word Cloud", divider="grey")

        case_no = st.text_input(label="judge selection",
                                label_visibility="hidden",
                                placeholder="Enter case number:")
        if case_no:
            summary_texts = get_summary_texts_from_db(CONN, case_no)

            if summary_texts:
                word_cloud = generate_word_cloud(summary_texts)
                background_color = '#0e1117'
                plt.figure(figsize=(20, 10), facecolor=background_color)
                plt.imshow(word_cloud)
                plt.axis("off")
                plt.tight_layout(pad=0)
                st.pyplot()
            else:
                st.warning(
                    "No summary text found in the database for the entered case number.")

    CONN.close()
