import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer.pitch import Pitch
import numpy as np
from datetime import datetime

# Streamlit Page Setup
st.set_page_config(page_title="AI Football Match Analysis", layout="wide")
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>AI Football Match Analysis</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>DEV • ALVEXD</h3>", unsafe_allow_html=True)
st.write("Analyze football matches with advanced AI-driven insights in real-time or from old data.")

# API Setup
API_KEY = "a2d5140b518d4c9db46decce1aacdb82"  # Replace with your actual API key
API_URL_LIVE = "https://api.football-data.org/v4/matches"
API_URL_OLD = "https://api.football-data.org/v4/competitions/{competition_id}/matches"

# Function to fetch live match data
def fetch_live_match_data():
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(API_URL_LIVE, headers=headers)
    if response.status_code == 200:
        matches = response.json().get('matches', [])
        match_data = []
        for match in matches:
            match_info = {
                "match_name": f"{match.get('homeTeam', {}).get('name', 'N/A')} vs {match.get('awayTeam', {}).get('name', 'N/A')}",
                "team_1": match.get('homeTeam', {}).get('name', 'N/A'),
                "team_2": match.get('awayTeam', {}).get('name', 'N/A'),
                "score": f"{match.get('score', {}).get('fullTime', {}).get('homeTeam', 0)} - {match.get('score', {}).get('fullTime', {}).get('awayTeam', 0)}",
                "status": match.get('status', 'Unknown'),
                "date": match.get('utcDate', 'N/A')
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
        matches = response.json().get('matches', [])
        match_data = []
        for match in matches:
            match_info = {
                "match_name": f"{match.get('homeTeam', {}).get('name', 'N/A')} vs {match.get('awayTeam', {}).get('name', 'N/A')}",
                "date": match.get('utcDate', 'N/A'),
                "team_1": match.get('homeTeam', {}).get('name', 'N/A'),
                "team_2": match.get('awayTeam', {}).get('name', 'N/A'),
                "score": f"{match.get('score', {}).get('fullTime', {}).get('homeTeam', 0)} - {match.get('score', {}).get('fullTime', {}).get('awayTeam', 0)}",
                "status": match.get('status', 'Unknown')
            }
            match_data.append(match_info)
        return pd.DataFrame(match_data)
    else:
        st.error(f"Error fetching old data: {response.status_code}")
        return pd.DataFrame()

# Additional Features: Match Statistics
def display_match_stats(data):
    st.subheader("Match Statistics")
    stats = {
        "Total Matches": len(data),
        "Completed Matches": len(data[data["status"] == "FINISHED"]),
        "Upcoming Matches": len(data[data["status"] == "SCHEDULED"])
    }
    st.write(stats)

# Visualization Functions
def plot_xg():
    pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))
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
    heatmap_data = np.random.rand(8, 12)
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax, cbar_kws={'label': 'xG Value'})
    ax.set_title("xG Heatmap")
    return fig

# Sidebar Setup
st.sidebar.header("Match Analysis")
match_type = st.sidebar.radio("Select Match Type", ["Live Matches", "Old Matches"])

if match_type == "Live Matches":
    data = fetch_live_match_data()
    if data.empty:
        st.write("No live matches available at the moment.")
    else:
        display_match_stats(data)
        selected_match = st.sidebar.selectbox("Select a Live Match", data["match_name"].unique())
        match_data = data[data["match_name"] == selected_match]
        st.subheader(f"Match: {selected_match}")
        st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
        st.write(f"Score: {match_data['score'].values[0]}")
        st.write(f"Status: {match_data['status'].values[0]}")
        st.write(f"Date: {datetime.strptime(match_data['date'].values[0], '%Y-%m-%dT%H:%M:%SZ')}")
        st.pyplot(plot_xg())

elif match_type == "Old Matches":
    competition_id = st.sidebar.text_input("Enter Competition ID", "PL")
    data = fetch_old_match_data(competition_id)
    if data.empty:
        st.write("No old matches found for this competition.")
    else:
        display_match_stats(data)
        selected_match = st.sidebar.selectbox("Select an Old Match", data["match_name"].unique())
        match_data = data[data["match_name"] == selected_match]
        st.subheader(f"Old Match: {selected_match}")
        st.write(f"Date: {datetime.strptime(match_data['date'].values[0], '%Y-%m-%dT%H:%M:%SZ')}")
        st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
        st.write(f"Score: {match_data['score'].values[0]}")
        st.write(f"Status: {match_data['status'].values[0]}")
        st.pyplot(plot_xg())
                
