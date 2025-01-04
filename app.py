import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page Configuration
st.set_page_config(
    page_title="Football Transfer Market Insights",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS for Styling
st.markdown("""
    <style>
        body {
            background-color: #f4f4f9;
            color: #333;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-title {
            text-align: center;
            font-size: 3.5em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #f39c12;
            background: linear-gradient(to right, #f39c12, #8e44ad);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .description {
            text-align: center;
            font-size: 1.2em;
            color: #555;
            margin-bottom: 50px;
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
st.markdown("<div class='main-title'>⚽ Football Transfer Market Insights</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='description'>
        Explore player transfers, league spending, emerging talents, and much more.  
        This professional tool provides advanced insights into the football transfer market.
    </div>
""", unsafe_allow_html=True)

# Sidebar for Navigation
st.sidebar.title("⚙️ Navigation")
page = st.sidebar.radio(
    "Explore Features", 
    ["Home", "League Spending Analysis", "Player Search", "Young Talent Tracker", 
     "Top Transfers", "Transfer Comparison", "Transfer Trends"]
)

# API Integration
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
    - **Analyze transfer data:** Discover how leagues and clubs spend on players.  
    - **Track young talent:** Identify emerging stars with high potential.  
    - **Compare transfers:** Dive into transfer fees, clubs, and players.  
    """)
    st.write("Start exploring by selecting a feature from the sidebar.")

# League Spending Analysis
elif page == "League Spending Analysis":
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
        st.warning("No data available. Check the API or dataset.")

# Player Search
elif page == "Player Search":
    st.header("🔎 Search for Player Transfers")
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
        st.write("These are the top young talents based on transfer fees:")
        st.dataframe(young_players)
    else:
        st.warning("No data available.")

# Top Transfers
elif page == "Top Transfers":
    st.header("📊 Top Transfers by Season")
    if not data.empty:
        season = st.selectbox("Select Season", data['season'].dropna().unique())
        top_transfers = data[data['season'] == season].sort_values(by="fee.amount", ascending=False)
        st.write(f"Top transfers for the {season} season:")
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
            st.write(f"Comparison between {player1} and {player2}:")
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

# Footer
st.markdown("""
    <div class='footer'>
        Built with ❤️ by <b>DEV ALVEXD</b>. Transforming data into insights.
    </div>
""", unsafe_allow_html=True)
                                         
