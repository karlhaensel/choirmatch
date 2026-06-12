"""Main entry point for streamlit app 'choirmatch'."""

import pandas as pd
import streamlit as st

st.title(":green[ChoirMatch]")

st.sidebar.header("Input and options")
input_file = st.sidebar.file_uploader(
    "Upload a CSV file containing choir availability feedback.",
    type=["csv"],
    help="CSV file should have three columns for name, voice, and comment "
    "(comment can be empty, others not). "
    "All other columns are considered date columns to chose from later on.",
)
if input_file is None:
    st.info("Please upload a CSV file in the sidebar to the left.")
    st.stop()

df = pd.read_csv(input_file)

st.header("Availability data")
st.dataframe(df)
