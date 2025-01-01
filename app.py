import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer.pitch import Pitch
import numpy as np  # Needed for heatmap

# Streamlit Page Setup
st.set_page_config(page_title="AI Football Match Analysis", layout="wide")
st.title("AI Football Match Analysis")
st.title("DEV • ALVEXD")
st.write("Analyze football matches with advanced AI-driven insights in real-time or from historical data.")

# API Setup
API_KEY = "a2d5140b518d4c9db46decce1aacdb82"  # Your provided API key
API_URL_LIVE = "https://api.football-data.org/v4/matches"
API_URL_OLD = "https://api.football-data.org/v4/competitions/{competition_id}/matches"  # Replace `{competition_id}` dynamically

# Function to fetch live match data
def fetch_live_match_data():
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(API_URL_LIVE, headers=headers)
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        match_data = []

        for match in matches:
            match_info = {
                "match_name": f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}",
                "team_1": match['homeTeam']['name'],
                "team_2": match['awayTeam']['name'],
                "score": f"{match['score']['fullTime']['homeTeam']} - {match['score']['fullTime']['awayTeam']}",
                "status": match['status']
            }
            match_data.append(match_info)
        return pd.DataFrame(match_data)
    else:
        st.error(f"Error fetching live data: {response.status_code}")
        return pd.DataFrame()

# Function to fetch old match data
def fetch_old_match_data(competition_id):
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(API_URL_OLD.format(competition_id=competition_id), headers=headers)
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        match_data = []

        for match in matches:
            match_info = {
                "match_name": f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}",
                "date": match['utcDate'],
                "team_1": match['homeTeam']['name'],
                "team_2": match['awayTeam']['name'],
                "score": f"{match['score']['fullTime']['homeTeam']} - {match['score']['fullTime']['awayTeam']}",
                "status": match['status']
            }
            match_data.append(match_info)
        return pd.DataFrame(match_data)
    else:
        st.error(f"Error fetching old data: {response.status_code}")
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

# Streamlit Interactive Elements
st.sidebar.header("Choose Match Type")
match_type = st.sidebar.radio("Match Type", ["Live Matches", "Historical Matches"])

if match_type == "Live Matches":
    data = fetch_live_match_data()
    if data.empty:
        st.write("No live matches found.")
    else:
        match_options = data["match_name"].unique()
        selected_match = st.sidebar.selectbox("Select a Live Match", match_options)
        match_data = data[data["match_name"] == selected_match]

        st.subheader(f"Match: {selected_match}")
        st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
        st.write(f"Score: {match_data['score'].values[0]}")
        st.write(f"Status: {match_data['status'].values[0]}")
        st.subheader("Expected Goals (xG) Visualization")
        st.pyplot(plot_xg())

elif match_type == "Historical Matches":
    competition_id = st.sidebar.text_input("Enter Competition ID", "PL")  # Example: PL for Premier League
    data = fetch_old_match_data(competition_id)
    if data.empty:
        st.write("No historical matches found.")
    else:
        match_options = data["match_name"].unique()
        selected_match = st.sidebar.selectbox("Select a Historical Match", match_options)
        match_data = data[data["match_name"] == selected_match]

        st.subheader(f"Historical Match: {selected_match}")
        st.write(f"Date: {match_data['date'].values[0]}")
        st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
        st.write(f"Score: {match_data['score'].values[0]}")
        st.write(f"Status: {match_data['status'].values[0]}")
        st.subheader("Expected Goals (xG) Visualization")
        st.pyplot(plot_xg())
               
