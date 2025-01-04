import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# Page Configuration
st.set_page_config(
    page_title="Football Transfer Analytics",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS for Styling
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
            color: #333;
            font-family: Arial, sans-serif;
        }
        .main-title {
            text-align: center;
            font-size: 4em;
            font-weight: bold;
            margin: 20px 0;
            color: #1abc9c;
        }
        .description {
            text-align: center;
            font-size: 1.2em;
            color: #555;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .footer b {
            color: #3498db;
        }
    </style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown("<div class='main-title'>Football Transfer Analytics</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='description'>
        Explore transfer data, league spending, young talents, predictive analytics, and much more.
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("⚙️ Navigation")
page = st.sidebar.radio(
    "Choose a Feature",
    ["Home", "League Spending", "Player Search", "Young Talent Tracker", "Top Transfers",
     "Transfer Comparison", "Transfer Trends", "Predict Future Fees", "Club Spending Breakdown"]
)

# Fetch and Cache Data
@st.cache_data
def fetch_data():
    try:
        url = "https://api.football-data.org/v4/transfers"
        headers = {"Authorization": "Bearer a2d5140b518d4c9db46decce1aacdb82"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.json_normalize(data['transfers'])
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

data = fetch_data()

# Home Page
if page == "Home":
    st.header("Welcome to the Football Transfer Analytics Tool")
    st.write("""
    - Explore player transfers, league and club spending, emerging young talents, and more.  
    - Use advanced tools like predictive analytics and data visualizations for insights.
    - Select a feature from the sidebar to begin.
    """)

# League Spending
elif page == "League Spending":
    st.header("💰 League Spending Analysis")
    if not data.empty:
        league_spending = data.groupby("league.name")["fee.amount"].sum().reset_index()
        fig = px.bar(
            league_spending, x="league.name", y="fee.amount",
            color="league.name", title="Total Spending by League",
            labels={"fee.amount": "Total Spending (€M)", "league.name": "League"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available.")

# Player Search
elif page == "Player Search":
    st.header("🔎 Player Transfer Search")
    player_name = st.text_input("Enter Player Name")
    if player_name and not data.empty:
        search_results = data[data['player.name'].str.contains(player_name, case=False, na=False)]
        if not search_results.empty:
            st.dataframe(search_results)
        else:
            st.warning("No results found for the given player.")
    elif not player_name:
        st.info("Enter a player's name to search.")
    else:
        st.warning("No data available.")

# Young Talent Tracker
elif page == "Young Talent Tracker":
    st.header("🌟 Top Young Talents")
    if not data.empty:
        young_players = data[data['player.age'] < 22].sort_values(by="fee.amount", ascending=False)
        st.dataframe(young_players)
    else:
        st.warning("No data available.")

# Top Transfers
elif page == "Top Transfers":
    st.header("📊 Top Transfers by Season")
    if not data.empty:
        season = st.selectbox("Select Season", data['season'].dropna().unique())
        top_transfers = data[data['season'] == season].sort_values(by="fee.amount", ascending=False)
        st.dataframe(top_transfers)
    else:
        st.warning("No data available.")

# Transfer Comparison
elif page == "Transfer Comparison":
    st.header("⚔️ Compare Transfers")
    if not data.empty:
        player1 = st.selectbox("Select Player 1", data['player.name'].unique())
        player2 = st.selectbox("Select Player 2", data['player.name'].unique())
        if player1 and player2:
            comparison = data[data['player.name'].isin([player1, player2])]
            st.dataframe(comparison)
    else:
        st.warning("No data available.")

# Transfer Trends
elif page == "Transfer Trends":
    st.header("📈 Transfer Trends")
    if not data.empty:
        spending_over_time = data.groupby("season")["fee.amount"].sum().reset_index()
        fig = px.line(
            spending_over_time, x="season", y="fee.amount",
            title="Spending Trends Over Seasons",
            labels={"fee.amount": "Total Spending (€M)", "season": "Season"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available.")

# Predict Future Fees
elif page == "Predict Future Fees":
    st.header("🔮 Predict Future Player Fees")
    if not data.empty:
        st.write("Using regression models to predict future transfer fees based on player attributes.")
        # Prepare data
        features = ["player.age", "league.name", "fee.amount"]
        data = data.dropna(subset=features)
        le = LabelEncoder()
        data["league_encoded"] = le.fit_transform(data["league.name"])
        
        # Model
        X = data[["player.age", "league_encoded"]]
        y = data["fee.amount"]
        model = LinearRegression()
        model.fit(X, y)
        
        # Input
        age = st.slider("Player Age", 16, 40, 25)
        league = st.selectbox("League", le.classes_)
        league_encoded = le.transform([league])[0]
        
        # Prediction
        predicted_fee = model.predict([[age, league_encoded]])[0]
        st.write(f"Predicted Transfer Fee: **€{predicted_fee:.2f}M**")
    else:
        st.warning("No data available.")

# Club Spending Breakdown
elif page == "Club Spending Breakdown":
    st.header("🏟️ Club Spending Breakdown")
    if not data.empty:
        club_spending = data.groupby("team.name")["fee.amount"].sum().reset_index()
        club_spending = club_spending.sort_values(by="fee.amount", ascending=False).head(10)
        fig = px.pie(club_spending, values="fee.amount", names="team.name", title="Top 10 Clubs by Spending")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available.")

# Footer
st.markdown("""
    <div class='footer'>
        Built with ❤️ by <b>DEV ALVEXD</b>. Empowering football insights.
    </div>
""", unsafe_allow_html=True)
