import streamlit as st
import requests
import pandas as pd
from mplsoccer.pitch import Pitch
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Streamlit Page Setup
st.set_page_config(page_title="Premium AI Football Match Analysis", layout="wide")
st.markdown("<h1 style='text-align: center; color: #0078FF;'>Premium AI Football Match Analysis</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>DEV • ALVEXD</h3>", unsafe_allow_html=True)
st.write("Unleash the power of AI for advanced football match analytics, player performance heatmaps, and xG data.")

# API Setup
API_KEY = "a2d5140b518d4c9db46decce1aacdb82"  # Replace with your actual API key
API_URL_LIVE = "https://api.football-data.org/v4/matches"
API_URL_OLD = "https://api.football-data.org/v4/competitions/{competition_id}/matches"

# Caching API Requests
@st.cache_data(ttl=300)
def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API Request Failed: {response.status_code}")
        return {}

# Functions
def fetch_live_match_data():
    headers = {"X-Auth-Token": API_KEY}
    response = fetch_data(API_URL_LIVE, headers)
    matches = response.get('matches', [])
    return [
        {
            "match_name": f"{match.get('homeTeam', {}).get('name', 'N/A')} vs {match.get('awayTeam', {}).get('name', 'N/A')}",
            "team_1": match.get('homeTeam', {}).get('name', 'N/A'),
            "team_2": match.get('awayTeam', {}).get('name', 'N/A'),
            "score": f"{match.get('score', {}).get('fullTime', {}).get('homeTeam', 'N/A')} - {match.get('score', {}).get('fullTime', {}).get('awayTeam', 'N/A')}",
            "status": match.get('status', 'Unknown'),
            "date": match.get('utcDate', 'N/A'),
            "statistics": match.get('statistics', {})
        }
        for match in matches
    ]

def fetch_old_match_data(competition_id):
    headers = {"X-Auth-Token": API_KEY}
    url = API_URL_OLD.format(competition_id=competition_id)
    response = fetch_data(url, headers)
    matches = response.get('matches', [])
    return [
        {
            "match_name": f"{match.get('homeTeam', {}).get('name', 'N/A')} vs {match.get('awayTeam', {}).get('name', 'N/A')}",
            "team_1": match.get('homeTeam', {}).get('name', 'N/A'),
            "team_2": match.get('awayTeam', {}).get('name', 'N/A'),
            "score": f"{match.get('score', {}).get('fullTime', {}).get('homeTeam', 'N/A')} - {match.get('score', {}).get('fullTime', {}).get('awayTeam', 'N/A')}",
            "date": match.get('utcDate', 'N/A'),
            "status": match.get('status', 'Unknown'),
            "statistics": match.get('statistics', {})
        }
        for match in matches
    ]

def generate_heatmap(player_name, heatmap_data):
    pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(12, 8))
    sns.kdeplot(
        x=heatmap_data['X'], y=heatmap_data['Y'], shade=True,
        cmap="coolwarm", n_levels=50, ax=ax
    )
    ax.set_title(f"{player_name}'s Performance Heatmap", fontsize=16)
    return fig

def plot_xg(team_1, team_2, xg_1, xg_2):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh([team_1, team_2], [xg_1, xg_2], color=['blue', 'red'])
    ax.set_xlabel("Expected Goals (xG)")
    ax.set_title("xG Comparison")
    return fig

def display_statistics(statistics):
    if not statistics:
        st.write("No statistics available for this match.")
    else:
        for key, value in statistics.items():
            st.write(f"**{key.capitalize()}**: {value}")

def plot_timeline(events):
    fig, ax = plt.subplots(figsize=(12, 4))
    times = [event['minute'] for event in events if event['type'] == 'Goal']
    players = [event['player'] for event in events if event['type'] == 'Goal']
    ax.scatter(times, [1] * len(times), c='gold', label="Goals")
    for i, txt in enumerate(players):
        ax.annotate(txt, (times[i], 1.1))
    ax.set_yticks([])
    ax.set_xlabel("Time (minutes)")
    ax.set_title("Match Timeline")
    return fig

# Sidebar
st.sidebar.header("Match Analysis")
match_type = st.sidebar.radio("Select Match Type", ["Live Matches", "Old Matches"])

if match_type == "Live Matches":
    live_data = fetch_live_match_data()
    if not live_data:
        st.write("No live matches available.")
    else:
        selected_match = st.sidebar.selectbox("Select a Match", [match["match_name"] for match in live_data])
        match_data = next((match for match in live_data if match["match_name"] == selected_match), {})
        st.subheader(f"Match: {selected_match}")
        st.write(f"Teams: {match_data['team_1']} vs {match_data['team_2']}")
        st.write(f"Score: {match_data['score']}")
        st.write(f"Status: {match_data['status']}")
        st.write(f"Date: {match_data['date']}")

        st.subheader("Team Statistics")
        display_statistics(match_data['statistics'])

        st.subheader("xG Comparison")
        st.pyplot(plot_xg(match_data['team_1'], match_data['team_2'], 1.5, 2.1))

elif match_type == "Old Matches":
    competition_id = st.sidebar.text_input("Enter Competition ID (e.g., PL, CL, WC)", "PL")
    old_data = fetch_old_match_data(competition_id)
    if not old_data:
        st.write("No old matches found for this competition.")
    else:
        selected_match = st.sidebar.selectbox("Select a Match", [match["match_name"] for match in old_data])
        match_data = next((match for match in old_data if match["match_name"] == selected_match), {})
        st.subheader(f"Match: {selected_match}")
        st.write(f"Teams: {match_data['team_1']} vs {match_data['team_2']}")
        st.write(f"Score: {match_data['score']}")
        st.write(f"Status: {match_data['status']}")
        st.write(f"Date: {match_data['date']}")

        st.subheader("Team Statistics")
        display_statistics(match_data['statistics'])

        st.subheader("Match Timeline")
        events = [{"minute": 45, "type": "Goal", "player": "Player A"}]
        st.pyplot(plot_timeline(events))
    
