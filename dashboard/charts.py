'''This file contains charts for the streamlit dashboard.'''

from os import environ as ENV
import streamlit as st
import altair as alt
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
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


def get_filtered_data(data: pd.DataFrame, filters: dict):
    '''Filters a dataframe. Takes in a dictionary with keys type_id, judge_id, 
    circuit_id, gender, and appointed.'''

    for key in filters.keys():
        if filters[key]:
            if key == "circuit_id":
                data = data[data[key].isin(filters[key])]
            elif key == "appointed":
                data = data[data[key].apply(
                    lambda x: x >= filters[key][0] and x <= filters[key][1])]
            else:
                data = data[data[key] == filters[key]]

    if len(data) == 0:
        return "No data for chosen filters."

    return data


def get_judges_appointed(conn: connect) -> pd.DataFrame:
    '''Returns the judge counts grouped by gender and appointment.'''

    query = """
                SELECT appointed, gender, count(judge_id) FROM judge
                GROUP BY appointed, gender;
                """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return pd.DataFrame(rows)


def get_cases(conn: connect) -> pd.DataFrame:
    '''Returns the case number and date.'''

    query = """
                SELECT COUNT(case_no), transcript_date FROM transcript
                GROUP BY transcript_date;
                """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return pd.DataFrame(rows)


def get_gender_donut_chart(data: pd.DataFrame):
    '''Returns a donut chart showing judge genders.'''

    genders = data.value_counts("gender").reset_index()

    chart = alt.Chart(genders).mark_arc(innerRadius=15).encode(
        theta='count:Q',
        color=alt.Color('gender:N').title('Gender')
    ).properties(width=225, height=225)

    return chart


def get_waffle_chart(data: pd.DataFrame):
    '''Returns a waffle chart that shows verdicts which ruled in favour of claimant vs defendant.'''

    claimants = data[data['verdict'].str.lower().str.contains('claimant')]
    defendants = data[data['verdict'].str.lower().str.contains('defendant')]

    waffle_rows = (len(claimants) + len(defendants)) // 50

    if waffle_rows == 0:
        waffle_rows = 1

    fig = plt.figure(
        FigureClass=Waffle,
        rows=waffle_rows,
        figsize=(20, 2),
        values={'Claimant': len(claimants), 'Defendant': len(defendants)},
        colors=['#5e67c7', '#e26571'],
        facecolor='#0F1117',
    )

    return fig


def get_judge_count_line_chart(conn: connect) -> alt.Chart:
    '''Returns the line graph for judge appointment count over time.'''

    data = get_judges_appointed(conn)
    data["appointed"] = pd.to_datetime(data["appointed"])
    judge_count = data.set_index("appointed")

    judge_count = judge_count.groupby(
        ['gender', pd.Grouper(freq='YE')]).count().reset_index()

    # Adding counts for years that don't have values
    for i in range(1999, 2025):

        if not ((judge_count['gender'] == "M") & (judge_count['appointed'] == pd.Timestamp(year=i, month=12, day=31))).any():
            row = pd.DataFrame({"gender": "M", "appointed": pd.Timestamp(
                year=i, month=12, day=31), "count": 0}, index=[0])
            judge_count = pd.concat([judge_count, row], ignore_index=True)

        if not ((judge_count['gender'] == "F") & (judge_count['appointed'] == pd.Timestamp(year=i, month=12, day=31))).any():
            row = pd.DataFrame({"gender": "F", "appointed": pd.Timestamp(
                year=i, month=12, day=31), "count": 0}, index=[0])
            judge_count = pd.concat([judge_count, row], ignore_index=True)

        if not ((judge_count['gender'] == "X") & (judge_count['appointed'] == pd.Timestamp(year=i, month=12, day=31))).any():
            row = pd.DataFrame({"gender": "X", "appointed": pd.Timestamp(
                year=i, month=12, day=31), "count": 0}, index=[0])
            judge_count = pd.concat([judge_count, row], ignore_index=True)

    chart = alt.Chart(judge_count).mark_line().encode(
        x=alt.X("appointed", title="Year of Appointment"),
        y=alt.Y("count", title="Number of Judges"),
        color=alt.Color('gender:N', title='Gender')
    )

    return chart


def get_case_count_line_chart(conn: connect) -> alt.Chart:
    '''Returns the line graph for case count over time.'''

    data = get_cases(conn)

    data["transcript_date"] = pd.to_datetime(data["transcript_date"])
    case_count = data.set_index("transcript_date")

    case_count = case_count.groupby(
        [pd.Grouper(freq='YE')]).count().reset_index()

    chart = alt.Chart(case_count).mark_line().encode(
        x=alt.X("transcript_date", title="Month of Case"),
        y=alt.Y("count", title="Number of Cases"),
    )

    return chart


def generate_word_cloud(summary_texts):
    """Generates the word cloud itself with the 
    correct design."""
    background_color = '#0e1117'
    combined_text = ' '.join(summary_texts)
    word_cloud = WordCloud(width=800, height=400, background_color=background_color,
                           stopwords=STOPWORDS, contour_width=0,
                           max_font_size=80, min_font_size=10,
                           relative_scaling=0.5, random_state=42, max_words=50, colormap='Pastel1').generate(combined_text)
    return word_cloud


def get_summary_texts_from_db(conn, case_no):
    """Gets the summary from the transcripts and 
    adds it to a list."""
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


def standardise_verdicts(verdict: str) -> str:
    '''Standardises a verdict to return either 'Claimant' or 'Defendant.'''

    if 'claimant' in verdict.lower():
        return 'Claimant'

    if 'defendant' in verdict.lower():
        return 'Defendant'

    return None


def get_verdicts_stacked_bar_chart(data):

    data['verdict'] = data['verdict'].apply(standardise_verdicts)

    data = data[data['circuit_id'] != 1]

    chart = alt.Chart(data).mark_bar().encode(
        y=alt.Y('circuit_name:N').title('Location'),
        x=alt.X('count(verdict):Q').title('Number of cases'),
        color=alt.Color('verdict').title('Verdict'))

    return chart


if __name__ == "__main__":

    load_dotenv()

    CONN = get_db_connection(ENV)

    DATA = get_data_from_db(CONN)

    filtered = get_filtered_data(DATA, {'judge_id': None, 'circuit_id': None,
                                        'gender': None, 'appointment_date': None,
                                        'judge_type_id': None})

    result = get_gender_donut_chart(filtered)
