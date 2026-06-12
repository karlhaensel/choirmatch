"""Utils and helpers for streamlit app."""


def colour_availability(val: int):
    """CSS mapping for availability values in table."""
    return {
        4: "background-color: #4CAF50; color: white;",  # green
        3: "background-color: #2196F3; color: white;",  # blue
        2: "background-color: #FF9800; color: black;",  # orange
        1: "background-color: #F44336; color: white;",  # red
    }.get(val, "")
