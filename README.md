# F1 Strategy Optimizer

A Python and Java application that uses Formula 1 practice-session data to model tire degradation and compare predicted race strategies.

## Overview

This F1 Strategy Optimizer takes Formula 1 practice-session data for a selected driver and race, models tire degradation, and uses the resulting model to compare different pit-stop strategies.

I wanted to better understand F1 strategy and see whether I could use practice-session data to build a model that could give me a more informed idea of what to expect during a race.
Rather than relying only on existing strategy predictions, the program uses practice-session data to estimate how a driver's lap times change as their tires age, then uses those estimates to compare different race strategies.

The project combines **Python for data processing and regression** with **Java for strategy optimization**, with **JSON**  to communicate between the two.

## How It Works

The overall pipeline is:

```text
Streamlit UI
      ↓
Python / FastF1
      ↓
Practice-session data
      ↓
Stint selection + lap filtering
      ↓
Quadratic tire-degradation regression
      ↓
JSON
      ↓
Java brute-force optimizer
      ↓
Strategy ranking
      ↓
JSON
      ↓
Streamlit results
```

### 1. Collecting Practice Data

The Python program uses [FastF1](https://github.com/theOehrly/Fast-F1) to retrieve data from FP1, FP2, and FP3.

For the selected driver, the program:

* Collects laps for the Soft, Medium, and Hard compounds
* Picks accurate laps
* Searches for the longest continuous stint on each compound
* Removes severe lap-time outliers before modeling
* Uses tire age and lap time as the primary variables

### 2. Modeling Tire Degradation

The program uses a second-degree polynomial to approximate the relationship between tire age and lap time.

The model has the form:

```text
Lap Time = a(Tyre Life)^2 + b(Tyre Life) + c
```

A quadratic model was chosen because tire performance does not necessarily degrade at a constant rate.
Tires can have an initial warm-up period with higher lap times and also significantly drop once degradation becomes more significant later in the stint.

The regression produces a set of coefficients for each compound, which are then passed to the Java optimizer.

### 3. Strategy Optimization

The Java portion of the project receives:

* Tire-degradation coefficients
* Total race laps
* Pit-stop time loss
* Any compound excluded because of insufficient stint data

The optimizer evaluates possible strategies of up to three stops.

For each strategy, it:

1. Determines the tire used during each stint.
2. Uses the tire model to estimate lap times.
3. Integrates the model to estimate driving time over each stint.
4. Adds the estimated time lost during pit stops.
5. Calculates the total predicted race time.
6. Sorts the strategies from fastest to slowest.

## Example Output

For example, the optimizer may produce:

| Strategy                             | Stint Lengths | Predicted Time (s) |
| ------------------------------------ | ------------: | -----------------: |
| One stop Medium-Hard                 |         27-31 |            5245.92 |
| Two stop Medium-Hard-Hard            |      20-19-19 |            5246.40 |
| Two stop Medium-Medium-Hard          |      20-20-18 |            5255.92 |
| Three stop Medium-Hard-Hard-Hard     |    1-19-19-19 |            5261.05 |
| Three stop Medium-Medium-Hard-Hard   |    1-20-18-19 |            5270.57 |
| Three stop Medium-Medium-Medium-Hard |    1-20-20-17 |            5280.17 |

The Streamlit interface presents these strategies to the user for comparison.

## Architecture

The project is split into two main components.

### Python

Responsible for:

* User interface through Streamlit
* FastF1 data collection
* Practice-session processing
* Stint detection
* Lap-time filtering
* Regression
* Preparing optimizer inputs
* Communicating with Java through JSON
* Displaying the results

### Java

Responsible for:

* Reading the Python-generated JSON input
* Evaluating possible tire strategies
* Calculating predicted race time
* Accounting for pit-stop time
* Ranking strategies
* Writing the results back to JSON

## Technologies

* **Python 3.13.1**
* **FastF1 3.5.3**
* **NumPy 2.3.0**
* **Pandas 2.3.0**
* **SciPy 1.15.3**
* **Streamlit 1.63.0**
* **Java JDK 25.0.1**
* **Jackson 2.21.x**
* **JSON**
* **Git / GitHub**

## Requirements

Before running the project, make sure you have:

* Python 3.13.1
* Java JDK 25.0.1
* Internet access for retrieving FastF1 data

The Python dependencies are listed in [`requirements.txt`](requirements.txt).

The required Jackson JAR files are already included in the repository under:

```text
Java_calculus optimization/lib/
```

These include:

```text
jackson-annotations-2.21.jar
jackson-core-2.21.1.jar
jackson-databind-2.21.1.jar
```

## Running the Project

### 1. Install Python dependencies

From the root directory of the project, create and activate a Python virtual environment if you have not already done so.

Then install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

### 2. Start the application

Navigate to the Python project directory:

```bash
cd Python_Data_Processing
```

Then run:

```bash
streamlit run app.py
```

Streamlit will start a local web application and provide a URL that can be opened in a browser.

The application allows the user to specify parameters such as:

* Driver
* Race
* Year (Currently set to 2025 by default and not changeable)
* Pit-stop time loss
* Total race laps
* Minimum stint length

The program then retrieves the relevant practice-session data, models tire degradation, runs the Java optimizer, and displays the predicted strategy rankings.

## Limitations

This project is an exploratory model rather than a professional race simulator. There are several factors that are not currently modeled.

### Data and Modeling

* Driver performance can vary significantly within a stint.
* Tire life alone does not completely describe tire degradation.
* The current lap filtering process is not fully robust.
* Regression can overfit when too little stint data is available.
* Errors in the regression model propagate into the final strategy predictions.

### Race Conditions

The current model does not account for factors such as:

* Fuel load
* Track temperature
* Traffic
* Weather
* Safety cars
* Track position
* Driver behavior
* Tire warm-up conditions
* Other race-specific strategic considerations

The optimizer is also currently limited to strategies involving up to three pit stops. This is not a huge limitation since even a three stop is rare realistically.

Because of these limitations, the output should be interpreted as a comparison of strategies based on the available practice-session data and assumptions rather than as a prediction of what will actually happen during a race.

## Future Improvements

Potential improvements include:

* More robust lap filtering
* Better handling of regression outliers
* Modeling fuel load
* Accounting for track and weather conditions
* Incorporating race-session data
* Improving tire degradation models
* Supporting additional strategy types
* Improving the Streamlit interface
* Better handling of invalid or insufficient user input
* More extensive testing of edge cases

## What I Learned

This project started from scratch and that required me learning several new concepts along the way.

### Working With External Libraries

FastF1 was one of my first experiences working extensively with an external library. I had to learn how to navigate its API, retrieve data, and process the specific F1 data I needed.

### Designing a Data Pipeline

A major challenge was designing the Python program around the final goal. I had to work backwards from the desired optimizer and determine how each stage of the pipeline had to be built to accommodate that.

### Regression and Data Modeling

The project introduced me to automating math concepts like regression to turn a lot of data into a mathematical model. 
It also, in a brutal way, showed me how problems in data quality can propagate through an entire system and affect the final results very heavily.

### Cross-Language Communication

Connecting the Python data-processing system to the Java optimizer was another major learning experience. I learned how JSON could be used as a simple interface between programs written in different languages.

### Optimization

I implemented a Java optimizer to evaluate different combinations of tire compounds and stint lengths rather than manually comparing strategies.

### Git and GitHub

The project also gave me practical experience using Git for version control and GitHub for storing and documenting a software project.
