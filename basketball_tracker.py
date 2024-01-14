import sqlite3
from datetime import datetime
from prettytable import PrettyTable


def date_has_changed(current_date):
    conn = sqlite3.connect('basketball_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM shots')
    latest_date = cursor.fetchone()[0]
    conn.close()
    return latest_date != current_date


def create_tables():
    # Connect to SQLite database (or create a new one if it doesn't exist)
    conn = sqlite3.connect('basketball_tracker.db')

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result TEXT NOT NULL,
        location TEXT,
        date DATE DEFAULT CURRENT_DATE
        )
    ''')

    # Create a table to store grouped shot data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grouped_shots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            date DATE,
            result TEXT,
            count INTEGER
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to insert shot data into the database
def insert_shot(location, result, date, count):
    conn = sqlite3.connect('basketball_tracker.db')
    cursor = conn.cursor()

    # Insert shot data into the 'shots' table
    cursor.executemany('INSERT INTO shots (result, location, date) VALUES (?, ?, ?)',
                       [(result, location, date) for _ in range(count)])
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to retrieve shot data grouped by location and date
def get_shots_grouped_by_location_and_date():
    conn = sqlite3.connect('basketball_tracker.db')
    cursor = conn.cursor()

    # Retrieve shot data grouped by location and date
    cursor.execute('''
        SELECT MIN(id) as id, location, date, result, COUNT(*) as count
        FROM shots
        GROUP BY location, date, result
    ''')

    # Fetch all the grouped results
    grouped_shots = cursor.fetchall()

    # Close the connection
    conn.close()

    return grouped_shots

# Function to insert grouped results into the database
def insert_grouped_results_into_db(grouped_shots):
    conn = sqlite3.connect('basketball_tracker.db')
    cursor = conn.cursor()

    # Clear existing data in the 'grouped_shots' table
    cursor.execute('DELETE FROM grouped_shots')

    # Reset the auto-increment counter for 'grouped_shots'
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='grouped_shots'")

    for _, location, date, result, count in grouped_shots:
        if result == 'made':
            # Insert grouped results into the 'grouped_shots' table
            cursor.execute('INSERT INTO grouped_shots (location, date, result, count) VALUES (?, ?, ?, ?)',
                        (location, date, result, count))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to display grouped results in a table
def display_grouped_results(grouped_shots):
    table = PrettyTable(['ID', 'Location', 'Date', 'Result', 'Count'])

    for row in grouped_shots:
        table.add_row(row)

    print(table)

#----------------------------------------------------------------------------------------------------------------#

# main

current_date = datetime.now().strftime('%Y-%m-%d')

if date_has_changed(current_date):
    create_tables()

# Get user input for location
location = input("Enter the location: ")

if location == 'free throw':
    num_makes = int(input("How many makes in a row? \n"))
    num_misses = 0
else:
    # Get user input for the number of makes and misses
    num_makes = int(input("How many makes? \n:"))
    num_misses = int(input("How many misses? \n:"))

# Insert makes into the database
insert_shot(location, 'made', datetime.now().strftime('%Y-%m-%d'), num_makes)

# Insert misses into the database
insert_shot(location, 'missed', datetime.now().strftime('%Y-%m-%d'), num_misses)

# Retrieve grouped shot data by location and date
grouped_shots = get_shots_grouped_by_location_and_date()

# Display the grouped results in a table
display_grouped_results(grouped_shots)

# Insert grouped results into the 'grouped_shots' table
insert_grouped_results_into_db(grouped_shots)