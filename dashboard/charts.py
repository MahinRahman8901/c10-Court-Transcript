'''This file contains charts for the streamlit dashboard.'''

from os import environ as ENV

import altair as alt
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from pywaffle import Waffle


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
    '''Filters a dataframe. Takes in a dictionary with keys judge_id, 
    circuit_id, gender, appointment_date and judge_type_id.'''

    for key in filters.keys():
        if filters[key]:
            data = data[data[key] == filters[key]]

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

    chart = alt.Chart(genders, title='Genders').mark_arc(innerRadius=50).encode(
        theta='count:Q',
        color=alt.Color('gender:N').title('Gender')
    ).properties(
        title='Judge Gender Split')

    return chart


def get_waffle_chart(data: pd.DataFrame):
    '''Returns a waffle chart that shows verdicts which ruled in favour of claimant vs defendant.'''

    claimants = data[data['verdict'].str.lower().str.contains('claimant')]
    defendants = data[data['verdict'].str.lower().str.contains('defendant')]

    waffle_rows = (len(claimants) + len(defendants)) // 100

    if waffle_rows == 0:
        waffle_rows = 1

    fig = plt.figure(
        FigureClass=Waffle,
        rows=waffle_rows,
        figsize=(20, 2),
        values={'Claimant': len(claimants), 'Defendant': len(defendants)},
        colors=['#5e67c7', '#e26571'],
        facecolor='#0F1117',
        title={
            'label': 'Cases ruled in favour of the claimant vs the defendant',
            'loc': 'left',
            'fontdict': {
                'fontsize': 20,
                'color': '#FFFFFF'
            }
        }
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

    chart = alt.Chart(judge_count, title="Judge Appointment Date / Time").mark_line().encode(
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

    chart = alt.Chart(case_count, title="Case Count / Time").mark_line().encode(
        x=alt.X("transcript_date", title="Month of Case"),
        y=alt.Y("count", title="Number of Cases"),
    )

    return chart


if __name__ == "__main__":

    load_dotenv()

    CONN = get_db_connection(ENV)

    DATA = get_data_from_db(CONN)

    filtered = get_filtered_data(DATA, {'judge_id': None, 'circuit_id': None,
                                        'gender': None, 'appointment_date': None,
                                        'judge_type_id': None})

    result = get_gender_donut_chart(filtered)
