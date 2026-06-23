"""Constants for data and streamlit app."""

DEFAULT_MISSING_COMMENT_VALUE = "kA"

DEFAULT_NAME_COL = "name"
DEFAULT_VOICE_COL = "voice"
DEFAULT_COMMENT_COL = "comment"

COUNT_COL = "count"


# TODO: change to English naming?

VOICES_ORDERED = (
    "Sopran 1",
    "Sopran 2",
    "Alt 1",
    "Alt 2",
    "Tenor 1",
    "Tenor 2",
    "Bass 1",
    "Bass 2",
)

VOICE_GROUPS = ("Sopran", "Alt", "Tenor", "Bass")

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
