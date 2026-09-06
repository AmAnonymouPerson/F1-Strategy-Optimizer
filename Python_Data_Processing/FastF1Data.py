import fastf1
import logging
import pandas as pd
import regression
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JAVA_DIR = PROJECT_ROOT / "Java_calculus optimization"
JAVA_OUT = JAVA_DIR / "out"
JAVA_LIB = JAVA_DIR / "lib"
RUNTIME_DIR = PROJECT_ROOT


logging.getLogger('fastf1').setLevel(logging.WARNING)
fastf1.Cache.enable_cache('cache')

practice_sessions = ['FP1', 'FP2', 'FP3']
tyres = ['SOFT', 'MEDIUM', 'HARD']

degree = 2

def load_session(year, race, session_name):
    try:
        session = fastf1.get_session(year, race, session_name)
        session.load()
        return session
    except Exception as e:
        print(f"Couldn't load {session_name} for {race}: {e}")
        return None

def get_used_compounds(laps, compounds):
    return {c for c in compounds if not laps[laps['Compound'] == c].empty}

def get_driver_data(driver, race, year):

    used_compounds = set()

    combined_df = pd.DataFrame()

    for session_name in practice_sessions:

        session = load_session(year, race, session_name)

        if session is None:
            continue

        laps = session.laps.pick_drivers(driver).pick_accurate()

        if laps.empty:
            continue

        used_compounds.update(get_used_compounds(laps, tyres))

        for compound in tyres:

            tyre_laps = laps[laps['Compound'] == compound]

            if tyre_laps.empty:
                continue

            session_df = pd.DataFrame({

                'LapNumber': tyre_laps['LapNumber'],
                'TyreLife': tyre_laps['TyreLife'],
                'LapTime': tyre_laps['LapTime'].dt.total_seconds(),
                'Compound': tyre_laps['Compound'],
                'Session': session_name

            })

            combined_df = pd.concat([combined_df, session_df], ignore_index=True)

    if len(used_compounds) > 1:
        print(f"{race} has more than 1 compound")
    else:
        print(f"{race} doesnt have more than 1 compound")

    return combined_df, used_compounds

def longest_stint (dataset):

    longest = []

    for session in practice_sessions:

        temp = []

        session_dataset = dataset[dataset['Session'] == session]
        session_dataset = session_dataset.sort_values('LapNumber')

        if session_dataset.empty:
            continue

        for i in range(len(session_dataset) - 1):

            current_row = session_dataset.iloc[i]
            next_row = session_dataset.iloc[i + 1]

            current_lap = current_row['LapNumber']
            next_lap = next_row['LapNumber']

            temp.append(current_row)

            if current_lap != next_lap - 1:
                if len(temp) > len(longest):
                    longest = temp
                temp = []

        temp.append(session_dataset.iloc[-1])

        if len(temp) > len(longest):
            longest = temp


    return longest

def filter_lap_times(dataset):

    if dataset.empty:
        return dataset

    median = dataset['LapTime'].median()

    mad = ((dataset['LapTime'] - median).abs()).median()

    dataset = dataset[ ( 0.6745 * (dataset['LapTime'] - median) / mad ).abs() < 3.5 ]

    minimum = dataset['LapTime'].min()
    dataset = dataset[dataset['LapTime'] <= minimum * 1.07]

    return dataset

def run_optimizer(constants, pit_time_lost, total_laps, excluded_compound):
    input_data = {
        "constants": constants,
        "pit_time_lost": pit_time_lost,
        "total_laps": total_laps,
        "excluded_compound": excluded_compound
    }

    with open(RUNTIME_DIR / "input.json", "w") as file:
        json.dump(input_data, file, indent=2)

    java = "java"

    classpath = (
            str(JAVA_OUT)
            + ";"
            + str(JAVA_LIB / "jackson-annotations-2.21.jar")
            + ";"
            + str(JAVA_LIB / "jackson-core-2.21.1.jar")
            + ";"
            + str(JAVA_LIB / "jackson-databind-2.21.1.jar")
    )

    compile_result = subprocess.run(
        [
            "javac",
            "-cp", str(JAVA_LIB / "*"),
            str(JAVA_DIR / "src" / "InputData.java"),
            str(JAVA_DIR / "src" / "Strategy_Bruteforce.java"),
            "-d", str(JAVA_OUT)
        ],
        capture_output=True,
        text=True
    )

    if compile_result.returncode != 0:
        raise RuntimeError(f"Java compilation failed:\n{compile_result.stderr}")

    result = subprocess.run(
        [java, "-classpath", classpath, "Strategy_Bruteforce"],
        capture_output=True,
        text=True,
        cwd=RUNTIME_DIR
    )

    if result.stderr:
        print("ERROR:")
        print(result.stderr)

    with open(RUNTIME_DIR / "output.json", "r") as file:
        results = json.load(file)

    return results

def run_program(driver, race, year, pit_time_lost, total_laps, min_stint_length):

    data, compounds = get_driver_data(driver, race, year)

    hard = data[(data['Compound'] == 'HARD')]
    medium = data[(data['Compound'] == 'MEDIUM')]
    soft = data[(data['Compound'] == 'SOFT')]

    longest_hard_stint = filter_lap_times(pd.DataFrame(longest_stint(hard)))
    longest_medium_stint = filter_lap_times(pd.DataFrame(longest_stint(medium)))
    longest_soft_stint = filter_lap_times(pd.DataFrame(longest_stint(soft)))

    insufficient = [len(longest_soft_stint) < min_stint_length, len(longest_medium_stint) < min_stint_length, len(longest_hard_stint) < min_stint_length]

    if sum(insufficient) >= 2:
        return "Not enough stint data"

    if insufficient[0]:
        excluded_compound = 0
    elif insufficient[1]:
        excluded_compound = 1
    elif insufficient[2]:
        excluded_compound = 2
    else:
        excluded_compound = 3

    hard_constants = regression.run_regression(longest_hard_stint, degree)
    medium_constants = regression.run_regression(longest_medium_stint, degree)
    soft_constants = regression.run_regression(longest_soft_stint, degree)

    constants = [soft_constants.tolist(), medium_constants.tolist(), hard_constants.tolist()]

    results = run_optimizer(constants, pit_time_lost, total_laps, excluded_compound)

    return results