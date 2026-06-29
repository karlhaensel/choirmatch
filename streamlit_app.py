"""Main entry point for streamlit app 'choirmatch'."""

# TODO: check typing and add more type hints
# TODO: try to modularise more
# TODO: add more documentation

import itertools

import pandas as pd
import streamlit as st

from const import (
    DEFAULT_NAME_COL,
    DEFAULT_VOICE_COL,
    DEFAULT_COMMENT_COL,
    VOICES_ORDERED,
    DEFAULT_MISSING_COMMENT_VALUE,
    SESSION_STATE_MIN_DATES_FIT_CRITERIA,
    VOICE_GROUPS,
    COUNT_COL,
    DEFAULT_MIN_AVAILABILITY_VALUE,
    DEFAULT_MAX_AVAILABILITY_VALUE,
    DEFAULT_DEFAULT_AVAILABILITY_VALUE,
    DEFAULT_AVAILABILITY_LABELS,
    DE_S,
    EN_S,
    EN_A,
    DE_A,
    EN_T,
    DE_T,
    EN_B,
    DE_B,
    EN_UNKNOWN,
    DE_UNKNOWN,
    SUBGROUP_SUFFICES,
)
from utils import colour_availability

# Basic setup
st.title(":green[ChoirMatch]")

# Start sidebar
with st.sidebar:
    st.sidebar.header("Input and options")
    side_tab1, side_tab2 = st.tabs(["Input and Column choice", "Mapping"])

    with side_tab1:
        # Organise CSV input:
        st.subheader("CSV input")
        input_file = st.file_uploader(
            "Upload a CSV file containing choir availability feedback.",
            type=["csv"],
            help="CSV file should have three columns for name, voice, and comment "
            "(comment can be empty, others not). "
            "All other columns are considered date columns to chose from later on.",
        )

        csv_separator = st.selectbox(
            "CSV seperator character", options=[",", ";"], index=0
        )
    if input_file is None:
        st.info("Please upload a CSV file!")
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
    with side_tab1:
        st.subheader("Data columns")
    column_choice = list(df.columns)

    name_idx = (
        column_choice.index(DEFAULT_NAME_COL)
        if DEFAULT_NAME_COL in column_choice
        else None
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

    with side_tab1:
        col_name = st.selectbox(
            "Column for singers' names:", column_choice, index=name_idx
        )
        col_voice = st.selectbox(
            "Column for singers' voices:", column_choice, index=voice_idx
        )
        col_comment = st.selectbox(
            "Column for singers' comments:", column_choice, index=comment_idx
        )
        cols_date = st.multiselect(
            "Columns of possible dates:",
            column_choice,
            default=[
                col
                for col in column_choice
                if col not in [col_name, col_voice, col_comment]
            ],
        )

    with side_tab2:
        st.subheader("Voice names")
        translate_voices = st.checkbox("Custom voice group names", value=False)
        v_unknown: str
        voice_groups: tuple[str, ...]
        voices_ordered: tuple[str, ...]
        if translate_voices:
            v_soprano = str(st.text_input(f"{EN_S}:", value=DE_S)).strip()
            v_alto = str(st.text_input(f"{EN_A}:", value=DE_A)).strip()
            v_tenor = str(st.text_input(f"{EN_T}:", value=DE_T)).strip()
            v_bass = str(st.text_input(f"{EN_B}:", value=DE_B)).strip()
            v_unknown = str(st.text_input(f"{EN_UNKNOWN}:", value=DE_UNKNOWN)).strip()
            voice_groups = tuple([v_soprano, v_alto, v_tenor, v_bass, v_unknown])
            voices_ordered = tuple(
                [
                    *(
                        f"{group} {num}"
                        for group, num in itertools.product(
                            voice_groups[:-1], SUBGROUP_SUFFICES
                        )
                    ),
                    v_unknown,
                ]
            )
        else:
            v_unknown = EN_UNKNOWN
            voice_groups = VOICE_GROUPS
            voices_ordered = tuple([*VOICES_ORDERED, v_unknown])

for col in (col_name, col_voice, col_comment):
    if col in cols_date:
        st.warning(
            f"Column {col} cannot be a special column (name/voice/comment) "
            f"AND a date column. Chose only one!"
        )
        st.stop()

if col_name is None:
    st.warning("You must chose a name column to continue!")
    st.stop()
if col_voice is None:
    st.warning("You must chose a voice column to continue!")
    st.stop()

basic_cols = (
    [col_name, col_voice, col_comment]
    if col_comment is not None
    else [col_name, col_voice]
)
if len(list(set(basic_cols))) != len(basic_cols):
    st.warning(
        "Special columns (name/voice/comment) must be different from each other. "
        "Use every column only once!"
    )
    st.stop()

# TODO: add dymanisation of availability codes/labels

# Preprocess data:
# TODO: check names and comments are strings/able
try:
    df[cols_date] = df[cols_date].astype(int)
except ValueError:
    st.warning(
        "Could not read in availabilites as integer values. "
        "Check source and/or choice of date columns!"
    )
    st.stop()

if (df[cols_date] > DEFAULT_MAX_AVAILABILITY_VALUE).any().any() or (
    df[cols_date] < DEFAULT_MIN_AVAILABILITY_VALUE
).any().any():
    st.error(
        f"Availability values must be between {DEFAULT_MIN_AVAILABILITY_VALUE} "
        f"and {DEFAULT_MAX_AVAILABILITY_VALUE} (both inclusive). "
        f"Please prepare CSV data accordingly!"
    )
    st.stop()

df[col_voice] = pd.Categorical(
    df[col_voice],
    categories=voices_ordered,
    ordered=True,
)
df[col_voice] = df[col_voice].fillna(v_unknown)  # Set NA to unknown.
if df[col_voice].isna().all():
    st.error(
        "No voice could be categorised. "
        'Check input file and/or adjust voice mapping in sidebar tab "Mapping".'
    )
    st.stop()
if (df[col_voice] == v_unknown).mean() > 0.5:
    st.warning(
        "Half of voice values were categorised as unknown. "
        'Check input file and/or adjust voice mapping in sidebar tab "Mapping".'
    )

cols_to_use = [*basic_cols, *cols_date]
df = df[cols_to_use].reset_index(drop=True).set_index(col_name)
df = df.sort_values([col_voice, df.index.name])
comments: pd.Series | None = df[col_comment] if col_comment is not None else None

# Main page:
st.header("Choose filters")
min_availability_required = st.slider(
    "Minimum availability required",
    min_value=DEFAULT_MIN_AVAILABILITY_VALUE,
    max_value=DEFAULT_MAX_AVAILABILITY_VALUE,
    value=DEFAULT_DEFAULT_AVAILABILITY_VALUE,
    help=f"Possible values: "
    f"{', '.join(f'{k}: {v}' for k, v in DEFAULT_AVAILABILITY_LABELS.items())}",
)
date_selection = st.multiselect("Filter for dates", cols_date, default=cols_date)
date_selection = [date for date in cols_date if date in date_selection]

if SESSION_STATE_MIN_DATES_FIT_CRITERIA not in st.session_state:
    setattr(st.session_state, SESSION_STATE_MIN_DATES_FIT_CRITERIA, 1)
setattr(
    st.session_state,
    SESSION_STATE_MIN_DATES_FIT_CRITERIA,
    min(
        getattr(st.session_state, SESSION_STATE_MIN_DATES_FIT_CRITERIA),
        len(date_selection),
    ),
)
min_dates_to_fit_criteria = 1
if len(date_selection) > 0:
    min_dates_to_fit_criteria = st.slider(
        "Minimum of selected dates that must meet given availability criteria",
        min_value=0,
        max_value=len(date_selection),
        key=SESSION_STATE_MIN_DATES_FIT_CRITERIA,
    )
filter_voices = st.multiselect(
    "Filter for voice groups", options=voices_ordered, default=voices_ordered
)

# Start displaying data:
st.header("Availability data")
# Display options:
with st.container(border=True):
    opt_col1, opt_col2, opt_col3 = st.columns(3)
    with opt_col1:
        colourise = st.checkbox(
            "Colourise availabilities",
            value=True,
        )
    with opt_col2:
        hide_unselected = st.checkbox(
            "Only show chosen dates",
            value=True,
        )
    with opt_col3:
        # FIXME: Too specific, make dynamic (special criterium AND date(s) to apply to).
        # FIXME: If dates selected in wrong order -> this breaks!
        force_performance_date = st.checkbox(
            "Filter for last selected date (=performance) with availability >= 3",
            value=False,
        )

# Filter data:
dates_to_show = cols_date
if hide_unselected and date_selection:
    dates_to_show = date_selection

display_df = df[[col_voice, *dates_to_show]].copy()

if filter_voices:
    display_df = display_df[display_df[col_voice].isin(filter_voices)]

sum_of_dates_meeting_criteria_in_selection = (
    display_df[date_selection].ge(min_availability_required).sum(axis=1)
)
display_df = display_df[
    sum_of_dates_meeting_criteria_in_selection >= min_dates_to_fit_criteria
]

if force_performance_date and len(date_selection) > 0:
    display_df = display_df[display_df[date_selection[-1]].ge(3)]

# Colourise if option selected and finally display:
if colourise:
    styled_df = display_df.style.map(
        colour_availability,
        subset=dates_to_show,
    )
    st.dataframe(styled_df)
else:
    st.dataframe(display_df)

st.write(
    f"**TOTAL (filtered):** {len(display_df)} ({len(display_df) / len(df):.1%}) singers"
)

# Download button current choir configuration summary according to filters
if len(date_selection) > 0:
    text = [
        f"Total singers that left date feedback: {len(df)}",
        f"Minimum availability required: {min_availability_required}",
        f"Selected dates: {', '.join(date_selection)}",
        f"Minimum selected dates to fit criteria: {min_dates_to_fit_criteria}",
    ]
    if force_performance_date:
        text.append(
            "Special: Force availability of >= 3 for last selected date (=performance)."
        )

    text.extend(
        [
            "",
            f"TOTAL for set filters: {len(display_df)} "
            f"({len(display_df) / len(df):.1%})",
            "\n",
        ]
    )

    for voice in voices_ordered:
        names = display_df[display_df[col_voice] == voice].index.tolist()
        text.append(f"{voice} ({len(names)}):")
        if names:
            text.extend(names)
        else:
            text.append("-")
        text.append("")

    st.download_button(
        label="Download current choir match",
        data="\n".join(text),
        file_name="choir_match.txt",
        mime="text/plain",
    )

# Display voice statistics for filtered data
st.header("Summary per voice groups")
detail_counts = (
    display_df[col_voice].value_counts().reindex(voices_ordered).fillna(0).astype(int)
)

summary = {}

for group in [*voice_groups, v_unknown]:
    summary[group] = display_df[col_voice].str.startswith(group).sum()

sum_col1, sum_col2 = st.columns(2)

summary_ser = pd.Series(summary, name=COUNT_COL)
summary_ser.index.name = col_voice

with sum_col1:
    st.subheader("Voices")
    st.table(detail_counts)

with sum_col2:
    st.subheader("Voice groups")
    st.table(summary_ser)

# TODO: add date-grouped stats

# Display availability comments (if existing):
if col_comment is not None:
    st.header("Availability comments")
    display_comments = comments[comments != DEFAULT_MISSING_COMMENT_VALUE].copy()  # type: ignore[index]
    display_comments = display_comments[display_comments.index.isin(display_df.index)]
    st.dataframe(display_comments)
