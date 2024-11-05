import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx

# Setup database connection
conn = sqlite3.connect("tournament_bracket.db")
cursor = conn.cursor()

# Create a table to store match results if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matchups (
        round INTEGER,
        match_id INTEGER,
        team1 TEXT,
        team2 TEXT,
        winner TEXT
    )
''')
conn.commit()

# Function to load matchups from database
def load_matchups():
    cursor.execute("SELECT * FROM matchups")
    return cursor.fetchall()

# Function to add/update a matchup result in the database
def save_matchup(round_num, match_id, team1, team2, winner):
    cursor.execute('''
        INSERT OR REPLACE INTO matchups (round, match_id, team1, team2, winner)
        VALUES (?, ?, ?, ?, ?)
    ''', (round_num, match_id, team1, team2, winner))
    conn.commit()

# UI for entering matchups and selecting the winner
st.title("Dynamic Tournament Bracket")

# Get round and match information
round_num = st.number_input("Round Number", min_value=1, max_value=4, step=1)
match_id = st.number_input("Match ID", min_value=1)
team1 = st.text_input("Team 1")
team2 = st.text_input("Team 2")
winner = st.radio("Select the Winner", [team1, team2])

# Confirm button to save results
if st.button("Confirm Result"):
    save_matchup(round_num, match_id, team1, team2, winner)
    st.success(f"Match result saved: {winner} wins between {team1} and {team2}")

# Load matchups and display them in a bracket-like structure
matchups = load_matchups()

# Function to plot the tournament bracket
def plot_bracket(matchups):
    G = nx.DiGraph()
    positions = {}
    labels = {}

    # Set positions for rounds
    round_positions = {1: -1, 2: 0, 3: 1, 4: 2}

    # Populate graph with nodes and edges based on matchups
    for match in matchups:
        round_num, match_id, team1, team2, winner = match
        G.add_node(team1, pos=(round_positions[round_num], -match_id))
        G.add_node(team2, pos=(round_positions[round_num], -match_id - 0.5))
        
        # Add edges based on winners
        if winner:
            G.add_edge(team1, winner)
            G.add_edge(team2, winner)
        
        # Update labels
        labels[team1] = team1
        labels[team2] = team2

    # Get positions for the graph layout
    pos = nx.get_node_attributes(G, 'pos')
    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=500, node_color="skyblue", font_size=8, font_weight="bold", ax=ax)
    ax.set_title("Tournament Bracket")

    st.pyplot(fig)

# Plot bracket
plot_bracket(matchups)

# Close database connection
conn.close()
