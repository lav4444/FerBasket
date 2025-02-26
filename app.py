import streamlit as st
import json
import os

database_path = "/Users/tomislavmatanovic/Documents/Sunday Brunch/database.json"

# Load JSON Data
@st.cache_data
def load_data():
    with open(database_path) as f:
        return json.load(f)

data = load_data()

# App Title
st.title("Basketball Player Profiles")

# Select Season
season = st.selectbox("Choose a Season", list(data.keys()))

# Select Player
all_players = []
for game in data[season].values():
    for team in game.values():
        all_players.extend(list(team.keys()))

all_players = list(set(all_players))
player = st.selectbox("Choose a Player", sorted(all_players))

# Display Player Stats
player_stats = []
for game in data[season].values():
    for team in game.values():
        if player in team:
            player_stats.append(team[player])

if player_stats:
    st.subheader(f"{player}'s Stats in {season}")
    st.json(player_stats)

    # Calculate Averages
    avg_stats = {k: sum(d[k] for d in player_stats) / len(player_stats) for k in player_stats[0]}
    st.subheader("Averages:")
    st.json(avg_stats)
else:
    st.warning("No data available for this player in the selected season.")





# RUN
# streamlit run /Users/tomislavmatanovic/Documents/Sunday\ Brunch/Python_App/web_basketball_app/app.py

#   Local URL: http://localhost:8501
#  Network URL: http://172.20.10.3:8501