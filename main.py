import datetime
import sched
import sqlite3
import time
import requests

def get_opensky_data(icao24, username, password):
    url = f"https://opensky-network.org/api/states/all?icao24={icao24}"
    auth = (username, password)

    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        data = response.json()
        save_to_database(icao24, data)  # Save the data to the database
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching OpenSky data: {e}")
        return None
    except ValueError as e:
        print(f"Error occurred while parsing OpenSky response: {e}")
        return None

def save_to_database(icao24, data):
    # Connect to the database or create it if it doesn't exist
    connection = sqlite3.connect(f"{icao24}.db")
    cursor = connection.cursor()

    # Extract the timestamp and states from the data
    timestamp = data['time']
    states = data['states']

    formatted_timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Create the table if it doesn't exist
        cursor.execute(f"CREATE TABLE IF NOT EXISTS opensky_data (timestamp INTEGER, {create_columns(states)})")

        # Prepare the values to insert into the table
        values = [(formatted_timestamp, *state) for state in states]

        # Insert the data into the table
        cursor.executemany(f"INSERT INTO opensky_data VALUES ({', '.join(['?'] * (len(states[0]) + 1))})", values)

        # Commit the changes and close the connection
        connection.commit()
        print(f"Data saved to the database: {icao24}.db")
    except sqlite3.Error as e:
        print(f"Error occurred while saving data to the database: {e}")

    connection.close()

def create_columns(states):
    columns = []
    for i, state in enumerate(states):
        for j in range(len(state)):
            column_name = f"state{j+1}"
            columns.append(f"{column_name} TEXT")
    return ", ".join(columns)

def fetch_opensky_data():
    icao24 = "ace75a"  # Replace with the actual ICAO24 code
    username = "OPENSKYUSERNAME"  # Replace with your OpenSky username
    password = "OPENSKYPASSWORD"  # Replace with your OpenSky password

    opensky_data = get_opensky_data(icao24, username, password)
    if opensky_data is not None:
        # Data has been saved to the database
        print("OpenSky data retrieved and saved to the database.")
        print(opensky_data)
    else:
        print("Unable to fetch OpenSky data.")

def schedule_opensky_data_fetcher():
    scheduler = sched.scheduler(time.time, time.sleep)
    interval = 120  # Fetch data every 2 minutes

    def fetch_data():
        try:
            fetch_opensky_data()
        except Exception as e:
            print(f"Error occurred while fetching OpenSky data: {e}")

        scheduler.enter(interval, 1, fetch_data)  # Schedule the next fetch

    scheduler.enter(0, 1, fetch_data)  # Schedule the first fetch
    scheduler.run()


schedule_opensky_data_fetcher()
