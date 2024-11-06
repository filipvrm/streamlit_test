import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database setup
conn = sqlite3.connect("tournament_bracket.db")
cursor = conn.cursor()

# Create the matchups table if it doesn't exist, with an added timestamp column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matchups (
        round INTEGER,
        winner INTEGER,
        loser INTEGER,
        timestamp TEXT
    )
''')
conn.commit()

# Function to add a matchup to the database, with current timestamp
def add_matchup(round_num, winner, loser):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
    try:
        cursor.execute("INSERT INTO matchups (round, winner, loser, timestamp) VALUES (?, ?, ?, ?)", (round_num, winner, loser, timestamp))
        conn.commit()
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to load matchups from the database
def load_matchups():
    cursor.execute("SELECT round, winner, loser, timestamp FROM matchups ORDER BY round")
    return cursor.fetchall()

# Function to remove the last entry from the matchups table
def remove_last_matchup():
    cursor.execute("DELETE FROM matchups WHERE timestamp = (SELECT MAX(timestamp) FROM matchups)")
    conn.commit()

# Function to get the status of each dish (winner, loser, or neutral)
def get_dish_status():
    cursor.execute("SELECT winner, loser FROM matchups")
    matchups = cursor.fetchall()
    
    dish_status = {i: "neutral" for i in range(1, 32)}  # Initialize all dishes as neutral
    
    for winner, loser in matchups:
        dish_status[loser] = "loser"
        dish_status[winner] = "winner"  # If a dish wins later, it overrides "loser" status
    
    return dish_status

# Function to display dish status at the top
def display_dish_status(dish_status_container):
    dish_status = get_dish_status()  # Load the latest status
    with dish_status_container:
        st.write("### Dish Status")
        
        cols = st.columns(10)  # Create 10 columns for better spacing
        
        for i in range(1, 32):
            status = dish_status[i]
            color = "green" if status == "winner" else "red" if status == "loser" else "white"
            cols[(i - 1) % 10].markdown(f"<span style='color:{color}; font-size:20px;'>{i}</span>", unsafe_allow_html=True)

# Function to create the matchups table display
def create_table():
    matchups = load_matchups()
    
    if not matchups:
        st.write("No matchups available yet.")
        return
    
    # Determine the number of rounds by finding the max round number
    rounds = max(match[0] for match in matchups) + 1
    
    # Initialize a dictionary to store table data
    table_data = {f"Round {i+1}": [] for i in range(rounds)}
    
    # Create the rounds and add matchups
    for r in range(rounds):
        round_matchups = [m for m in matchups if m[0] == r]
        
        if r != 1:  # First round (Winner and Loser)
            for i in range(2**(r)-1):
                table_data[f"Round {r+1}"].append("")  # Blank row
        
        # For each round, make sure the number of entries is consistent
        for match in round_matchups:
            if r == 1:  # First round (Winner and Loser)
                table_data[f"Round {r}"].append(match[1])  # Winner
                table_data[f"Round {r}"].append("")  # Blank row
                table_data[f"Round {r}"].append(match[2])  # Loser
                table_data[f"Round {r}"].append("")  # Blank row

                table_data[f"Round {r+1}"].append("")  # Blank row
                table_data[f"Round {r+1}"].append(match[1])  # winner
                table_data[f"Round {r+1}"].append("")  # Blank row
                table_data[f"Round {r+1}"].append("")  # Blank row

            else:  # For subsequent rounds, show only the winner
                table_data[f"Round {r+1}"].append(match[1])  # Winner

                for i in range(2**(r+1)-1):
                    table_data[f"Round {r+1}"].append("")  # Blank row
    
    # Ensure all columns are of the same length by padding with empty strings
    max_length = max(len(col) for col in table_data.values())
    for round_col in table_data:
        while len(table_data[round_col]) < max_length:
            table_data[round_col].append("")  # Append empty strings to pad shorter columns
    
    # Convert to DataFrame for display
    df = pd.DataFrame(table_data)
    st.table(df)

# Streamlit input for winner, loser, and round
st.title("TTT Turnering")

# Display welcome text at the beginning
st.markdown("### Välkommen till TTTs (TaggadThaiTorsdag) officiella hemsida.")

# Display additional text with clickable phone number
st.markdown("##### För att beställa, ring [073-537 83 52](tel:+46735378352).")


# Create a placeholder for dish status
st.markdown("### Maträtter med status")
dish_status_container = st.empty()
display_dish_status(dish_status_container)  # Initial display of dish status


st.markdown("### Ange dagens resultat")
# Input form for entering match results
with st.form("input_form"):
    round_num = st.number_input("Enter the Round (1+):", min_value=1, max_value=31, step=1)
    
    # Dropdowns for winner and loser
    dish_options = list(range(1, 32))
    winner = st.selectbox("Select the Winner", options=dish_options)
    loser = st.selectbox("Select the Loser", options=dish_options)
    
    submitted = st.form_submit_button("Add Result")
    
    if submitted:
        if winner != loser:
            add_matchup(round_num, winner, loser)
            st.success(f"Match result added: Winner = {winner}, Loser = {loser}, Round = {round_num}")
            # Update dish status display after adding a result
            display_dish_status(dish_status_container)  # Refresh only the placeholder
        else:
            st.error("Winner and Loser cannot be the same.")

# Button to remove the last entry
if st.button("Remove Last Entry"):
    remove_last_matchup()
    st.success("Last entry removed.")
    # Update views
    display_dish_status(dish_status_container)  # Refresh the dish status display

# Create and display the table with match results
st.markdown("### Maträtters turneringsresultat")
create_table()

# Close database connection when done
conn.close()
