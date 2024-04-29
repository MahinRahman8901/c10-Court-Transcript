import streamlit as st
from os import environ as ENV
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


if __name__ == "__main__":

    load_dotenv()
    conn = get_db_connection(ENV)

    with st.sidebar:
        st.title("Arelm")
        st.subheader("")

    profiles, visualizations = st.columns([.4, .6], gap="medium")
    with profiles:
        # judge profile
        pass

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
