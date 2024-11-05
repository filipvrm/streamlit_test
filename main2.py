import streamlit as st
import pandas as pd

# Initialize or load the dishes progress data
if 'dishes' not in st.session_state:
    st.session_state.dishes = {i: 0 for i in range(41)}  # Initialize all dishes at position 0

# Title
st.title("TaggadThaiTorsdag - Taste Test Tournament")

# Instructions
st.write("Select two dishes to taste test. Pick one as the 'Winner' and one as the 'Loser'.")

# Dish Selection
dish_options = list(st.session_state.dishes.keys())
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
        st.session_state.dishes[winner] += 1

        # Update information
        st.success(f"Dish {winner} advances! Current stage: {st.session_state.dishes[winner]}")
        
# Display Progression Table
progress_data = pd.DataFrame(list(st.session_state.dishes.items()), columns=["Dish", "Stage"])
progress_data = progress_data.sort_values(by="Stage", ascending=False).reset_index(drop=True)

# Progression Graph
st.write("### Dish Progression")
st.write("The dish that tasted the best will end up on the far right as the tournament progresses.")
st.table(progress_data)

# Arrow-Like Progress Visualization
st.write("### Progress Visualization")
for dish, stage in sorted(st.session_state.dishes.items(), key=lambda x: x[1], reverse=True):
    st.write("Dish {}: ".format(dish) + "→ " * stage)
