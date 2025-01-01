import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer.pitch import Pitch

# Streamlit Page Setup
st.set_page_config(page_title="AI Football Match Analysis", layout="wide")
st.title("AI Football Match Analysis")
st.write("Analyze football matches with advanced AI-driven insights in real-time.")

# API Setup (Replace with your own API key)
API_KEY = "your_api_key_here"  # Replace this with your API key
API_URL = "https://api-football-v1.p.rapidapi.com/v3/matches"

# Function to fetch live match data from the API
def fetch_live_match_data():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    params = {
        "live": "true"  # Fetch live matches
    }
    
    response = requests.get(API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        matches = data['response']
        match_data = []
        
        for match in matches:
            match_info = {
                "match_name": f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}",
                "team_1": match['teams']['home']['name'],
                "team_2": match['teams']['away']['name'],
                "score": f"{match['goals']['home']} - {match['goals']['away']}",
                "status": match['fixture']['status']['long'],
                "event": match['goals']['home'] > match['goals']['away'] and "Goal" or "Shot"
            }
            match_data.append(match_info)
        return pd.DataFrame(match_data)
    else:
        st.error(f"Error fetching data from API: {response.status_code}")
        return pd.DataFrame()

# Helper Functions for Match Analysis
def plot_xg():
    pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    # Simulated shot data (X, Y, Outcome, xG value)
    shots = pd.DataFrame({
        "X": [50, 60, 70],
        "Y": [40, 50, 60],
        "shot_outcome": ["Goal", "Miss", "Goal"],
        "shot_statsbomb_xg": [0.8, 0.2, 0.9]
    })
    goals = shots[shots['shot_outcome'] == 'Goal']
    no_goals = shots[shots['shot_outcome'] != 'Goal']
    pitch.scatter(goals["X"], goals["Y"], s=goals["shot_statsbomb_xg"] * 500,
                  c="green", edgecolors="black", label="Goals", ax=ax)
    pitch.scatter(no_goals["X"], no_goals["Y"], s=no_goals["shot_statsbomb_xg"] * 500,
                  c="red", edgecolors="black", label="Missed Shots", ax=ax)
    plt.legend(loc="upper right")
    return fig

def heatmap_xg():
    # Simulate xG heatmap
    heatmap_data = np.random.rand(8, 12)
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax)
    ax.set_title("xG Heatmap")
    return fig

def player_insights():
    # Simulate player insights
    return "Player A (Team A)", "Player B (Team B)"

# Streamlit Interactive Elements
data = fetch_live_match_data()

# Check if there are live matches
if data.empty:
    st.write("No live matches found.")
else:
    # Sidebar Match Selection
    match_options = data["match_name"].unique()
    selected_match = st.sidebar.selectbox("Select a Match", match_options)

    # Get data for selected match
    match_data = data[data["match_name"] == selected_match]

    # Display selected match details
    st.subheader(f"Match: {selected_match}")
    st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
    st.write(f"Score: {match_data['score'].values[0]}")
    st.write(f"Status: {match_data['status'].values[0]}")

    # Simulate live match data updates for selected match
    st.write("Simulating live event data...")
    event_data = match_data['event'].values[0]

    if event_data == "Goal":
        st.success("Goal Scored!")
    elif event_data == "Shot":
        st.warning("Shot Attempted!")

    # Display Match Analysis
    if st.button("Generate Match Analysis"):
        # Display xG plot
        st.subheader("Expected Goals (xG) Visualization")
        st.pyplot(plot_xg())

        # Display xG heatmap
        st.subheader("xG Heatmap")
        st.pyplot(heatmap_xg())

        # Display player insights
        st.subheader("Player Insights")
        xg_leader, goals_leader = player_insights()
        st.write(f"xG Leader: {xg_leader}")
        st.write(f"Goals Leader: {goals_leader}")
    
