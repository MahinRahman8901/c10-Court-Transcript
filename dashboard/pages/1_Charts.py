from os import environ as ENV
import streamlit as st
from layout import set_page_config, get_sidebar
from streamlit_app import load_dotenv, get_data_from_db, get_db_connection, get_judge_type_selection, get_circuit_selection, get_gender_selection, get_date_selection, get_judge_selection, compile_inputs_as_dict, get_filtered_data
from charts import (get_db_connection,
                    get_data_from_db,
                    get_filtered_data,
                    get_gender_donut_chart,
                    get_waffle_chart,
                    get_waffle_metrics,
                    get_judge_count_line_chart,
                    get_verdicts_stacked_bar_chart,
                    get_case_count_line_chart)

load_dotenv()
CONN = get_db_connection(ENV)

set_page_config()

get_sidebar()

data = get_data_from_db(CONN)

# controls/filters (may need columns to organize the controls)
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
inputs = compile_inputs_as_dict(CONN, viz_type_selection, viz_circuit_selection,
                                viz_gender_selection, viz_date_selection, viz_judge_selection)
filtered_data = get_filtered_data(data, inputs)

row_1 = st.columns(3, gap="large")
with row_1[0]:
    st.subheader(
        "Verdict Proportions")
    if isinstance(filtered_data, str):
        st.write(filtered_data)
    else:
        st.pyplot(get_waffle_chart(filtered_data))
        claimant_wins, defendant_wins = get_waffle_metrics(filtered_data)
        st.write("In favour of:")
        st.metric("Claimant", claimant_wins)
        st.metric("Defendant", defendant_wins)

with row_1[1]:
    st.subheader("Verdicts By Circuit")
    st.altair_chart(get_verdicts_stacked_bar_chart(data))

with row_1[2]:
    st.subheader("Judge Gender Split")
    if isinstance(filtered_data, str):
        st.write(filtered_data)
    else:
        st.altair_chart(get_gender_donut_chart(filtered_data))

row_2 = st. columns(2)
with row_2[0]:
    st.subheader("Case Count / Time")
    st.altair_chart(get_case_count_line_chart(CONN), use_container_width=True)

with row_2[1]:
    st.subheader("Judge Count / Time")
    st.altair_chart(get_judge_count_line_chart(CONN), use_container_width=True)
