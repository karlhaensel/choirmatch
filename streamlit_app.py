"""Main entry point for streamlit app 'choirmatch'."""

import pandas as pd
import streamlit as st

from const import (
    DEFAULT_NAME_COL,
    DEFAULT_VOICE_COL,
    DEFAULT_COMMENT_COL,
    VOICES_ORDERED,
    DEFAULT_MISSING_COMMENT_VALUE,
)
from utils import colour_availability

# Basic setup
st.title(":green[ChoirMatch]")

# Start sidebar
st.sidebar.header("Input and options")

# Organise CSV input:
st.sidebar.subheader("CSV input")
input_file = st.sidebar.file_uploader(
    "Upload a CSV file containing choir availability feedback.",
    type=["csv"],
    help="CSV file should have three columns for name, voice, and comment "
    "(comment can be empty, others not). "
    "All other columns are considered date columns to chose from later on.",
)

csv_separator = st.sidebar.selectbox(
    "CSV seperator character", options=[",", ";"], index=0
)
if input_file is None:
    st.info("Please upload a CSV file in the sidebar to the left.")
    st.stop()

# Import CSV:
try:
    df: pd.DataFrame = pd.read_csv(input_file, sep=csv_separator)
except pd.errors.ParserError:
    st.warning(
        f"Could not load data from file with separator '{csv_separator}'. "
        "Choose another seperator character or CSV file source."
    )
    st.stop()

# Data columns options:
st.sidebar.subheader("Data columns")
column_choice = list(df.columns)

name_idx = (
    column_choice.index(DEFAULT_NAME_COL) if DEFAULT_NAME_COL in column_choice else None
)
voice_idx = (
    column_choice.index(DEFAULT_VOICE_COL)
    if DEFAULT_VOICE_COL in column_choice
    else None
)
comment_idx = (
    column_choice.index(DEFAULT_COMMENT_COL)
    if DEFAULT_COMMENT_COL in column_choice
    else None
)

col_name = st.sidebar.selectbox(
    "Column for singers' names:", column_choice, index=name_idx
)
col_voice = st.sidebar.selectbox(
    "Column for singers' voices:", column_choice, index=voice_idx
)
col_comment = st.sidebar.selectbox(
    "Column for singers' comments:", column_choice, index=comment_idx
)
cols_date = st.sidebar.multiselect(
    "Columns of possible dates:",
    column_choice,
    default=[
        col for col in column_choice if col not in [col_name, col_voice, col_comment]
    ],
)

for col in (col_name, col_voice, col_comment):
    if col in cols_date:
        st.warning(
            f"Column {col} cannot be a special column (name/voice/comment) AND a date column. Chose only one!"
        )
        st.stop()

if col_name is None:
    st.warning("You must chose a name column to continue!")
    st.stop()
if col_voice is None:
    st.warning("You must chose a voice column to continue!")
    st.stop()

# TODO: add dymanisation of possible voices, and availability codes/labels

# Preprocess data:
df[col_voice] = pd.Categorical(
    df["voice"],
    categories=VOICES_ORDERED,
    ordered=True,
)

cols_to_use = (
    [col_name, col_voice, *cols_date, col_comment]
    if col_comment is not None
    else [col_name, col_voice, *cols_date]
)
df = df[cols_to_use].reset_index(drop=True).set_index(col_name)
df = df.sort_values([col_voice, df.index.name])
comments: pd.Series | None = df[col_comment] if col_comment is not None else None

# Main page:
st.header("Choose filters")
# TODO: add minimum availability requirement
date_selection = st.multiselect("Filter for dates", cols_date, default=cols_date)
# TODO: add minimum number of chosen dates that must meet the criteria
# TODO: add voice filter

# Start displaying data:
st.header("Availability data")
# Display options:
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        colourise = st.checkbox(
            "Colourise availabilities",
            value=True,
        )
    with col2:
        hide_unselected = st.checkbox(
            "Only show chosen dates.",
            value=True,
        )

# Filter data:
dates_to_show = cols_date
if hide_unselected and date_selection:
    dates_to_show = date_selection

display_df = df[[col_voice, *dates_to_show]].copy()

# Colourise if option selected and finally display:
if colourise:
    styled_df = display_df.style.map(
        colour_availability,
        subset=dates_to_show,
    )
    st.dataframe(styled_df)
else:
    st.dataframe(display_df)

# TODO: add voice-grouped stats

# Display availability comments (if existing):
if col_comment is not None:
    st.header("Availability comments")
    st.dataframe(comments[comments != DEFAULT_MISSING_COMMENT_VALUE])  # type: ignore[index]
