'''This file contains code to organise the layout of the dashboard e.g. the sidebar.'''

import streamlit as st


def set_page_config():
    '''This function sets up the necessary page config.'''
    st.set_page_config(page_title="Arelm Court Dashboard", page_icon="🏛", layout="wide",
                       initial_sidebar_state="expanded", menu_items=None)

    st.title("Court Dashboard")


def get_sidebar():
    '''This function programs a streamlit sidebar.'''
    with st.sidebar:
        st.title(":blue[Arelm]")
        st.subheader(":blue[Court Data Dashboard]")
        st.write(
            """This dashboard aims to summarise key insights from the court data we have collected. 
            You can find out more about each case and judge.""")
        st.write("---------")

        st.subheader(":violet[Sources:]")
        st.link_button(
            "All case law files", "https://caselaw.nationalarchives.gov.uk/")
        st.link_button("All judges in the UK",
                       "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/list-of-members-of-the-judiciary/")
        st.write("--------")

        st.subheader(":violet[Meet the team:]")
        st.link_button("Linktree", "https://linktr.ee/C10_Arelm")


if __name__ == "__main__":

    pass
