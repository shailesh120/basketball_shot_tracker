import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle
import sqlite3
from datetime import datetime

# Function to get coordinates based on the shot location
def get_coordinates_from_location(location):
    # Define the mapping of shot locations to (x, y) coordinates based on your court layout
    # Example mapping:
    mapping = {
        'center': (47, 39),
        'left corner': (80, 7),
        'left wing': (70, 31),
        'right corner': (14, 7),
        'right wing': (24, 31),
        'free throw': (47, 27)
        # Add more locations as needed
    }
    return mapping.get(location, (47, 10))  # Default to (0, 0) if location not found

# Function to create a basketball court image and plot shots
def plot_shots_on_court(shots, grouped_shots, date_today):
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 7))

    # Create the basketball court components

    # Create the outer boundary
    outer_boundary = Rectangle((0, 0), 94, 50, linewidth=2, edgecolor='black', fill=None)
    ax.add_patch(outer_boundary)

    # Create the key
    key = Rectangle((41, 5), 12, 19, linewidth=2, edgecolor='black', fill=None)
    ax.add_patch(key)

    # Create the free-throw circle
    free_throw_circle = plt.Circle((47, 24), radius=6, linewidth=2, edgecolor='black', fill=None)
    ax.add_patch(free_throw_circle)

    # Create the three-point line
    three_point_arc = Arc((47, 5), 60, 62, theta1=0, theta2=180, linewidth=2, edgecolor='black', fill=None)
    ax.add_patch(three_point_arc)

    # Plot each shot on the court
    for location, result in shots:
        x, y = get_coordinates_from_location(location)
        ax.add_patch(Circle((x, y), radius=1.6, color='green', alpha=0.7))

    # Add the number of shots made from grouped_shots onto the PNG image
    for location, _, count in grouped_shots:
        x, y = get_coordinates_from_location(location)

        conn = sqlite3.connect('basketball_tracker.db')
        cursor = conn.cursor()

        # Retrieve the counts of made and missed shots
        cursor.execute('SELECT COUNT(*) FROM shots WHERE location=? AND result="made"', (location,))
        made_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM shots WHERE location=? AND result="missed"', (location,))
        missed_count = cursor.fetchone()[0]

        conn.close()

        # Calculate the fraction (avoid division by zero)
        total_shots = made_count + missed_count
        fraction = f'{made_count}/{total_shots}' if total_shots != 0 else '0/0'

        if location == 'free throw':
            ax.text(x, y, made_count, ha='center', va = 'center', fontsize = 8, color = 'black', transform = ax.transData)

        else:
            # Display the fraction at the correct location on the PNG image
            ax.text(x, y, f'{fraction}', ha='center', va='center', fontsize=8, color='black', transform=ax.transData)

    # Set axis limits
    ax.set_xlim(0, 94)
    ax.set_ylim(0, 50)

    # Set aspect ratio to be equal
    ax.set_aspect('equal', adjustable='box')

    # Invert y-axis to flip the court horizontally
    plt.gca().invert_yaxis()

    # Save the plot as an image file
    plt.savefig(f'Shots_made_on_{date_today}.png')

    # Display the plot
    plt.show()

# Example usage:

current_date = datetime.now().strftime('%y-%m-%d')

# Retrieve shot data from the 'shots' table
conn = sqlite3.connect('basketball_tracker.db')
cursor = conn.cursor()
cursor.execute('SELECT location, result FROM shots')
shots = cursor.fetchall()

# Retrieve grouped shot data by location and date from the 'grouped_shots' table
cursor.execute('SELECT location, result, count FROM grouped_shots')
grouped_shots = cursor.fetchall()
conn.close()

# Call the function to plot the basketball court with shots
plot_shots_on_court(shots, grouped_shots, current_date)
