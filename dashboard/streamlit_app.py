import streamlit as st
import matplotlib.pyplot as plt
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
from charts import get_db_connection, get_data_from_db, get_filtered_data, get_gender_donut_chart, get_waffle_chart
from case_profiles import (get_case_query,
                           get_case_information_by_name,
                           get_case_information_by_case_number,
                           find_case_query_type)



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


def generate_word_cloud(summary_texts):
    combined_text = ' '.join(summary_texts)
    word_cloud = WordCloud(width=800, height=400, background_color='white',
                           stopwords=STOPWORDS).generate(combined_text)
    return word_cloud


def get_summary_texts_from_db(conn, case_no):
    summary_texts = []
    try:
        with conn.cursor() as cur:
            query = """
                    SELECT summary FROM transcript WHERE case_no = %s
                    """
            cur.execute(query, (case_no,))
            rows = cur.fetchall()
            for row in rows:
                summary_text = row.get('summary')
                if summary_text:
                    summary_texts.append(summary_text)
            return summary_texts

    except Exception as e:
        st.error(f"Error fetching summary texts from database: {e}")
        return summary_texts


if __name__ == "__main__":

    load_dotenv()
    CONN = get_db_connection(ENV)

    set_page_config()

    get_sidebar()

    data = get_data_from_db(CONN)
    filtered_data = get_filtered_data(data, {})

    st.altair_chart(get_gender_donut_chart(filtered_data))
    st.pyplot(get_waffle_chart(filtered_data))


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

        st.subheader(body="Case Search", divider="grey")
        case_search = get_case_query()

        if case_search:
            if find_case_query_type(case_search):
                case_info = get_case_information_by_name(
                    CONN, case_search)
            else:
                case_info = get_case_information_by_case_number(
                    CONN, case_search)
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
            st.write("Case not found.")

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
            pass

        with judge_cols[1]:
            # judge gender donut chart
            pass

        case_cols = st. columns([.6, .4])
        with case_cols[0]:
            # case count over doc date line graph
            pass

        with case_cols[1]:
            st.title("Word Cloud Generator")

            case_no = st.text_input("Enter Case Number:")
            if case_no:
                summary_texts = get_summary_texts_from_db(CONN, case_no)

                if summary_texts:
                    st.subheader("Word Cloud")
                    word_cloud = generate_word_cloud(summary_texts)
                    word_cloud = generate_word_cloud(summary_texts)
                    plt.figure(figsize=(10, 5))
                    plt.imshow(word_cloud, interpolation='bilinear')
                    plt.axis('off')
                    st.pyplot()
                else:
                    st.warning(
                        "No summary text found in the database for the entered case number.")
        verdict_cols = st.columns([.6, .4])
        with verdict_cols[0]:
            # verdict waffle chart
            pass

        with verdict_cols[1]:
            # verdict by circuit bar chart
            pass
