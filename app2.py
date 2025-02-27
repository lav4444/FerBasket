import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
from PIL import Image
# from streamlit_javascript import st_javascript
# from user_agents import parse


# Configure Streamlit Page
st.set_page_config(page_title="Basketball League App", layout="wide")



# ua_string = st_javascript("""window.navigator.userAgent;""")

# if ua_string and isinstance(ua_string, str):
#     try:
#         user_agent = parse(ua_string)
#         st.session_state.is_session_pc = user_agent.is_pc
#         #st.info(f"Is this a PC session? {st.session_state.is_session_pc}")
#     except Exception as e:
#         st.error(f"Error parsing user agent: {e}")
# else:
#     #st.warning("User agent string is not available or invalid.")
#     st.session_state.is_session_pc = False
# user_agent.is_pc returns True if the session runs on a PC







##### LOAD DATA #####
#database_path = "/Users/tomislavmatanovic/Documents/Sunday Brunch/Python_App/web_basketball_app/database.json"
database_path = "database.json"
#data_rounds_path = "/Users/tomislavmatanovic/Documents/Sunday Brunch/Python_App/web_basketball_app/data_round.json"
data_rounds_path = "data_round.json"

# Load JSON Data
@st.cache_data
def load_data():
    with open(database_path) as f:
        return json.load(f)

data = load_data()

@st.cache_data
def load_data():
    with open(data_rounds_path) as f:
        return json.load(f)

data_rounds = load_data()

####################




##### HELPER FUNCTIONS #####
MAIN_STATS = ["SEC", "PTS", "TREB", "AS", "STL", "BLK", "TOV"]
SHORT_NAME = {"?": "?", "SUN": "Sunday Brunch", "MEJ": "Meja Milkers", "ŠIB": "SKK Šibenik", "HCK": "Hackleri", "PMF": "PMF Tropics", "NEK": "Neks Media/E2GO",
              "IND": "Indukcija", "JSK": "JSK", "RUB": "Rubber Duckies", "MIL": "Meja Milkers", "BRI": "Brick City", "DIA": "Diablosi", "PRK": "Project K", "BRK": "Brick City",
              "S": "SKK Šibenik"}

def get_all_players(season):
    all_players = []
    for game in data[season].values():
        for team in game.values():
            all_players.extend(list(team.keys()))
    return list(set(all_players))

def get_player_team(season, player):
    # Iterate over all the games for the given season
    for game in data[season].values():
        for team_name, players in game.items():
            if player in players:  # Check if the player is in the team's player list
                return team_name  # Return the team name
    return "/"

# Calculate Average Stats for a Player
def calculate_total_stats(player_stats):
    return {k: sum(d[k] for d in player_stats) for k in player_stats[0]}, len(player_stats)

# main_stats
def calculate_basic_stats(player_stats):
    tot_stats, games_played = calculate_total_stats(player_stats)
    
    # Extract and convert required stats
    sec = tot_stats["SEC"]
    sec = sec // games_played
    time_min = sec // 60
    time_sec = sec % 60
    time_formatted = f"{int(time_min)}:{int(time_sec):02d}"
    
    basic_stats = {
        "GAMES": int(games_played),
        "PTS": round(tot_stats["PTS"] / games_played, 2),
        "REB": round(tot_stats["TREB"] / games_played, 2),
        "AST": round(tot_stats["AS"] / games_played, 2),
        "TIME": time_formatted,
        "STL": round(tot_stats["STL"] / games_played, 2),
        "BLK": round(tot_stats["BLK"] / games_played, 2),
        "TOV": round(tot_stats["TOV"] / games_played, 2)
    }
    
    return basic_stats

# advanced_stats
def calculate_advanced_stats(player_stats):
    tot_stats, games_played = calculate_total_stats(player_stats)    
    advanced_stats = {}

    for stat, value in tot_stats.items():
        if stat not in MAIN_STATS:
            if stat == "FG%":
                fgp = 0
                if tot_stats["FGA"] != 0:
                    fgp = tot_stats["FGM"] /  tot_stats["FGA"]
                advanced_stats[stat] = round(fgp*100, 2)
            elif stat == "2P%":
                tpp = 0
                if tot_stats["2PA"] != 0:
                    tpp = tot_stats["2PM"] /  tot_stats["2PA"]
                advanced_stats[stat] = round(tpp*100, 2)
            elif stat == "3P%":
                thpp = 0
                if tot_stats["3PA"] != 0:
                    thpp = tot_stats["3PM"] /  tot_stats["3PA"]
                advanced_stats[stat] = round(thpp*100, 2)
            elif stat == "FT%":
                ftp = 0
                if tot_stats["FTA"] != 0:
                    ftp = tot_stats["FTM"] /  tot_stats["FTA"]
                advanced_stats[stat] = round(ftp*100, 2)
            elif stat == "EFF":
                avg_eff = 0
                if tot_stats["SEC"] != 0:
                    avg_eff = tot_stats["PIR"] /  tot_stats["SEC"]
                    avg_eff = avg_eff * 60
                advanced_stats[stat] = round(avg_eff, 2)
            elif stat == "+/-":
                finall = value / tot_stats["SEC"]
                finall = finall * 60
                advanced_stats["+/- per MIN"] = round(finall, 2)
            else:
                if games_played==0:
                    advanced_stats[stat] = round(0, 2)
                else:
                    advanced_stats[stat] = round(value / games_played, 2)
    
    return advanced_stats

def per40_basic(player_stats):
    avg_basic = calculate_basic_stats(player_stats)
    avg_time = avg_basic["TIME"]
    minutes, seconds = map(int, avg_time.split(":"))
    avg_time = minutes * 60 + seconds
    avg_basic.pop("TIME", None)
    avg_basic.pop("GAMES", None)
    factor = (40*60) / avg_time

    for k, v in avg_basic.items():
        avg_basic[k] = round(v * factor, 2)
    
    return avg_basic


####################




###### PAGE LOGIC #############

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Teams", "Players"]) #selectbox->drop down menu // radio

# Home Page
if page == "Home":
    st.title("🏀 Basketball League Home Page")
    
    # Display League Logo
    st.image("images/ferb_logo.png", use_container_width=True)

    # Count total teams and players
    total_teams = set()
    total_players = set()

    for season_data in data.values():
        for game in season_data.values():
            for team, players in game.items():
                total_teams.add(team)
                total_players.update(players.keys())

    st.metric(label="Total Teams", value=len(total_teams))
    st.metric(label="Total Players", value=len(total_players))

# Teams Page (Placeholder)
elif page == "Teams":
    st.title("🏀 Teams Page")
    st.info("Currently working on this functionality...")

    # if st.session_state.is_session_pc:
    #     st.write("You are on a desktop")
    # else:
    #     st.write("You are on a mobile device")
        

# Players Page
elif page == "Players":
    st.title("🏀 Players Page")

    # Sidebar for Season and Player Selection
    st.sidebar.subheader("Select Season and Player")
    season = st.sidebar.selectbox("Choose a Season", list(data.keys()))
    player = st.sidebar.selectbox("Choose a Player", sorted(get_all_players(season)))

    if player:
        st.subheader(f"Player Profile: {player}")
        st.write(f"Player Team: {get_player_team(season, player)}")
        
        # Display Player Image
        image_path = f"images/{player.replace(' ', '_')}.png"
        if os.path.exists(image_path):
            st.image(Image.open(image_path), width=200)
        else:
            st.image(Image.open("images/player_placeholder.png"), width=200)
        
        # Collect All Stats for Selected Player
        player_stats = []
        round_stats = []
        opp_stats = []
        for game_key, game in data[season].items():
            #print("->", game_key)
            #print("---", data_rounds[season][game_key])
            team1 = (data_rounds[season][game_key])[1]
            team1 = SHORT_NAME[team1.upper()]
            team2 = (data_rounds[season][game_key])[2]
            team2 = SHORT_NAME[team2.upper()]
            curr_round = data_rounds[season][game_key][0]
            
            for team in game.values():
                if player in team:
                    opp_team = (team2 if team1 == team else team1)
                    player_stats.append(team[player])
                    round_stats.append(curr_round)
                    opp_stats.append(opp_team)

        if player_stats:
            # Calculate and Display Average Stats
            avg_stats = calculate_basic_stats(player_stats)

            # if st.session_state.is_session_pc == False:
            #     # Mobile layout
            #     st.subheader("Stats (Average)")
            #     cols = st.columns(2) #st.columns(2)
            #     for i, (stat, value) in enumerate(avg_stats.items()):
            #         cols[i % 2].metric(label=stat, value=value)
            # else:
            # Desktop layout
            st.subheader("Stats (Average)")
            cols = st.columns(4)
            for i, (stat, value) in enumerate(avg_stats.items()):
                cols[i % 4].metric(label=stat, value=value)


            ### Advanced Stats
            with st.expander("Advanced Stats (Average)"):
                st.subheader("Advanced Stats (Average)")
                advanced_stats = calculate_advanced_stats(player_stats)

                # Display Advanced Stats in Columns
                cols_adv = st.columns(4)
                for i, (stat, value) in enumerate(advanced_stats.items()):
                    cols_adv[i % 4].metric(label=stat, value=value)
            
            ### Per 40 min Stats
            with st.expander("Per 40 min Stats"):
                st.subheader("Per 40 min Stats")
                basic40_stats = per40_basic(player_stats)

                # Display Advanced Stats in Columns
                cols_adv = st.columns(8)
                for i, (stat, value) in enumerate(basic40_stats.items()):
                    cols_adv[i % 8].metric(label=stat, value=value)


            # Option to Show All Games
            with st.expander("Show All Games"):
                #st.write(player_stats)
                extend_stats_df = pd.DataFrame(player_stats)
                extend_stats_df.insert(0, "Round", round_stats) 
                extend_stats_df.insert(1, "Opponent", opp_stats)
                extend_stats_df = extend_stats_df.sort_values(by="Round", ascending=True).reset_index(drop=True)
                st.dataframe(extend_stats_df)

                # Provide option to download as CSV
                st.download_button(
                    label="Download stats as CSV",
                    data=extend_stats_df.to_csv(index=False),
                    file_name=f"{player}_stats.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No data available for this player in the selected season.")
