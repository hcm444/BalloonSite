from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch airplane data from the database
    data = fetch_airplane_data()

    # Pass the data to the template for rendering
    return render_template('index.html', data=data)

def fetch_airplane_data():
    icao24 = "ace75a"  # Replace with the actual ICAO24 code

    # Connect to the database and fetch all airplane data
    connection = sqlite3.connect(f"{icao24}.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM opensky_data")
    data = cursor.fetchall()
    connection.close()

    return data


if __name__ == '__main__':
    app.run(debug=True)
