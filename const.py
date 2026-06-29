"""Constants for data and streamlit app."""

import itertools

DEFAULT_MISSING_COMMENT_VALUE = "kA"

DEFAULT_NAME_COL = "name"
DEFAULT_VOICE_COL = "voice"
DEFAULT_COMMENT_COL = "comment"

COUNT_COL = "count"


EN_S = "Soprano"
EN_A = "Alto"
EN_T = "Tenor"
EN_B = "Bass"
EN_UNKNOWN = "Unknown"
DE_S = "Sopran"
DE_A = "Alt"
DE_T = "Tenor"
DE_B = "Bass"
DE_UNKNOWN = "Unbekannt"

VOICE_GROUPS = (EN_S, EN_A, EN_T, EN_B)
SUBGROUP_SUFFICES = (1, 2)

VOICES_ORDERED = tuple(
    f"{group} {num}"
    for group, num in itertools.product(VOICE_GROUPS, SUBGROUP_SUFFICES)
)

DEFAULT_MIN_AVAILABILITY_VALUE = 1
DEFAULT_MAX_AVAILABILITY_VALUE = 4
DEFAULT_DEFAULT_AVAILABILITY_VALUE = 3

DEFAULT_AVAILABILITY_LABELS = {
    1: "Not available",
    2: "Not sure yet",
    3: "Partially available",
    4: "Fully available",
}

SESSION_STATE_MIN_DATES_FIT_CRITERIA = "min_dates_to_fit_criteria"
