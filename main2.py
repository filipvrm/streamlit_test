import streamlit as st
import pandas as pd
import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('dishes_progress.db')
cursor = conn.cursor()

# Create the dishes table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dishes_progress (
        dish_id INTEGER PRIMARY KEY,
        stage INTEGER DEFAULT 0
    )
''')
conn.commit()

# Initialize the dishes in the database if they haven't been added yet
for dish_id in range(41):
    cursor.execute('INSERT OR IGNORE INTO dishes_progress (dish_id, stage) VALUES (?, ?)', (dish_id, 0))
conn.commit()

# Load data from the database
def load_dishes_progress():
    cursor.execute('SELECT * FROM dishes_progress')
    dishes = cursor.fetchall()
    return {dish_id: stage for dish_id, stage in dishes}

# Update dish stage in the database
def update_dish_stage(dish_id, new_stage):
    cursor.execute('UPDATE dishes_progress SET stage = ? WHERE dish_id = ?', (new_stage, dish_id))
    conn.commit()

# Load current dishes progress
dishes_progress = load_dishes_progress()

# Title
st.title("TaggadThaiTorsdag - Taste Test Tournament")

# Instructions
st.write("Select two dishes to taste test. Pick one as the 'Winner' and one as the 'Loser'.")

# Dish Selection
dish_options = list(dishes_progress.keys())
dish1 = st.selectbox("Choose Dish 1", dish_options, key="dish1")
dish2 = st.selectbox("Choose Dish 2", dish_options, key="dish2")

# Ensure two different dishes are selected
if dish1 == dish2:
    st.warning("Please select two different dishes.")
else:
    # Winner and Loser selection
    winner = st.radio("Select the Winner", [dish1, dish2], key="winner")
    loser = dish1 if winner == dish2 else dish2

    # Confirm button
    if st.button("Confirm"):
        # Advance the winner's position by 1
        new_stage = dishes_progress[winner] + 1
        update_dish_stage(winner, new_stage)
        st.success(f"Dish {winner} advances! Current stage: {new_stage}")
        
        # Reload updated progress
        dishes_progress = load_dishes_progress()

# Display Progression Table
progress_data = pd.DataFrame(list(dishes_progress.items()), columns=["Dish", "Stage"])
progress_data = progress_data.sort_values(by="Stage", ascending=False).reset_index(drop=True)

# Progression Table
st.write("### Dish Progression Table")
st.write("The dish that tasted the best will end up on the far right as the tournament progresses.")
st.table(progress_data)

# Arrow-Like Progress Visualization
st.write("### Progress Visualization")
for dish, stage in sorted(dishes_progress.items(), key=lambda x: x[1], reverse=True):
    st.write("Dish {}: ".format(dish) + "→ " * stage)

# Close database connection when done
conn.close()
