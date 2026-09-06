import fastf1
import logging
import pandas as pd
import regression
import json
import subprocess


logging.getLogger('fastf1').setLevel(logging.WARNING)
fastf1.Cache.enable_cache('cache')

#year = 2025
#race = 'Abu Dhabi'
#driver = 'VER'
#pit_time_lost = 21.93
#total_laps = 58
#min_stint_length = 5


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

    # session_laps_map = {}

    combined_df = pd.DataFrame()

    for session_name in practice_sessions:

        session = load_session(year, race, session_name)

        if session is None:
            continue

        laps = session.laps.pick_drivers(driver).pick_accurate()

        if laps.empty:
            continue

        # session_laps_map[session_name] = laps

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

    with open("input.json", "w") as file:
        json.dump(input_data, file, indent=2)

    java = r"C:\Program Files\Java\jdk-23\bin\java.exe"

    classpath = (
        r"C:\Users\DELL\IdeaProjects\Formula_1\out\production\Formula_1;"
        r"C:\Users\DELL\IdeaProjects\Formula_1\lib\jackson-annotations-2.21.jar;"
        r"C:\Users\DELL\IdeaProjects\Formula_1\lib\jackson-core-2.21.1.jar;"
        r"C:\Users\DELL\IdeaProjects\Formula_1\lib\jackson-databind-2.21.1.jar"
    )

    result = subprocess.run(
        [java, "-classpath", classpath, "Strategy_Bruteforce"],
        capture_output=True,
        text=True
    )

    if result.stderr:
        print("ERROR:")
        print(result.stderr)

    with open("output.json", "r") as file:
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

print(get_driver_data('VER', "Azerbaijan", 2025))

