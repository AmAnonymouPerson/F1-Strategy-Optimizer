import streamlit as st
from FastF1Data import run_program
st.title("Formula 1 Strategy Optimizer")

st.header("Race Settings")

driver = st.selectbox(
    "Driver",
    ["VER", "NOR", "PIA", "LEC", "HAM", "RUS", "ALO", "STR",
     "GAS", "COL", "OCO", "BEA", "TSU", "LAW", "HUL", "BOR",
     "SAI", "ALB", "ANT", "HAD"]
)

race = st.selectbox(
    "Race",
    ["Australia", "China", "Japan", "Bahrain", "Saudi Arabia",
     "Miami", "Emilia-Romagna", "Monaco", "Spain", "Canada",
     "Austria", "Great Britain", "Belgium", "Hungary",
     "Netherlands", "Italy", "Azerbaijan", "Singapore",
     "United States", "Mexico", "São Paulo", "Las Vegas",
     "Qatar", "Abu Dhabi"]
)

year = 2025

pit_time_lost = st.number_input(
    "Pit Stop Time Loss (seconds)",
    min_value=0.0,
    value=21.93,
    step=0.1
)

total_laps = st.number_input(
    "Total Race Laps",
    min_value=1,
    value=58,
    step=1
)

min_stint_length = st.number_input(
    "Minimum Stint Length",
    min_value=1,
    value=10,
    step=1
)

if st.button("Optimize Strategy"):

    results = run_program(
        driver,
        race,
        year,
        pit_time_lost,
        total_laps,
        min_stint_length
    )

    if isinstance(results, str):
        st.error(results)

    else:
        st.subheader("Recommended Strategies")

        for result in results:
            st.write(result)