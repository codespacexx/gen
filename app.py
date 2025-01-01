import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer.pitch import Pitch
import numpy as np

# Streamlit Page Setup
st.set_page_config(page_title="AI Football Match Analysis", layout="wide")
st.title("AI Football Match Analysis - Premium Insights")
st.markdown("**Developed by DEV • ALVEXD**")
st.write("Analyze football matches with AI-driven insights in real-time or from past data.")

# API Setup
API_KEY = "a2d5140b518d4c9db46decce1aacdb82"  # Replace with your API key
API_URL_LIVE = "https://api.football-data.org/v4/matches"
API_URL_COMPETITIONS = "https://api.football-data.org/v4/competitions/{competition_id}/matches"

# Function to fetch all competitions
def fetch_competitions():
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get("https://api.football-data.org/v4/competitions", headers=headers)
    if response.status_code == 200:
        data = response.json()
        competitions = [{"id": comp["code"], "name": comp["name"]} for comp in data["competitions"]]
        return competitions
    else:
        st.error("Error fetching competitions.")
        return []

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
                "status": match['status'],
                "home_score": match['score']['fullTime']['homeTeam'],
                "away_score": match['score']['fullTime']['awayTeam']
            }
            match_data.append(match_info)
        return pd.DataFrame(match_data)
    else:
        st.error(f"Error fetching live match data: {response.status_code}")
        return pd.DataFrame()

# Function to fetch match data for any competition
def fetch_competition_match_data(competition_id):
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(API_URL_COMPETITIONS.format(competition_id=competition_id), headers=headers)
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
                "status": match['status'],
                "home_score": match['score']['fullTime']['homeTeam'],
                "away_score": match['score']['fullTime']['awayTeam']
            }
            match_data.append(match_info)
        return pd.DataFrame(match_data)
    else:
        st.error(f"Error fetching competition match data: {response.status_code}")
        return pd.DataFrame()

# Helper Function for Heatmap
def create_heatmap():
    # Simulated player performance data
    heatmap_data = np.random.rand(12, 8)  # Simulating 12 players with 8 performance metrics
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".2f", ax=ax, cbar_kws={"label": "Performance"})
    ax.set_title("Player Performance Heatmap")
    return fig

# Sidebar
st.sidebar.header("Match Options")
match_type = st.sidebar.radio("Match Type", ["Live Matches", "Old Matches"])

if match_type == "Live Matches":
    data = fetch_live_match_data()
    if data.empty:
        st.write("No live matches available at the moment.")
    else:
        match_options = data["match_name"].unique()
        selected_match = st.sidebar.selectbox("Select a Match", match_options)
        match_data = data[data["match_name"] == selected_match]

        st.subheader(f"Match: {selected_match}")
        st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
        st.write(f"Score: {match_data['home_score'].values[0]} - {match_data['away_score'].values[0]}")
        st.write(f"Status: {match_data['status'].values[0]}")
        st.subheader("Player Performance Heatmap")
        st.pyplot(create_heatmap())

elif match_type == "Old Matches":
    competitions = fetch_competitions()
    competition_names = [comp["name"] for comp in competitions]
    selected_competition = st.sidebar.selectbox("Select a Competition", competition_names)
    selected_competition_id = [comp["id"] for comp in competitions if comp["name"] == selected_competition][0]

    data = fetch_competition_match_data(selected_competition_id)
    if data.empty:
        st.write("No match data available for this competition.")
    else:
        match_options = data["match_name"].unique()
        selected_match = st.sidebar.selectbox("Select a Match", match_options)
        match_data = data[data["match_name"] == selected_match]

        st.subheader(f"Old Match: {selected_match}")
        st.write(f"Date: {match_data['date'].values[0]}")
        st.write(f"Teams: {match_data['team_1'].values[0]} vs {match_data['team_2'].values[0]}")
        st.write(f"Score: {match_data['home_score'].values[0]} - {match_data['away_score'].values[0]}")
        st.write(f"Status: {match_data['status'].values[0]}")
        st.subheader("Player Performance Heatmap")
        st.pyplot(create_heatmap())
    
