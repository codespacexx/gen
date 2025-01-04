import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Page Configuration
st.set_page_config(
    page_title="Football Transfer Analytics - Transfermarkt",
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
st.markdown("<div class='main-title'>Football Transfer Analytics - Transfermarkt</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='description'>
        Explore transfer data, player images, and much more scraped from Transfermarkt.
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("⚙️ Navigation")
page = st.sidebar.radio(
    "Choose a Feature",
    ["Home", "Player Search", "Transfer Trends"]
)

# Function to scrape data from Transfermarkt
def scrape_transfermarkt():
    url = "https://www.transfermarkt.com/transfers"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract player names, transfer fees, and images
        players = []
        for row in soup.find_all("tr", class_="odd") + soup.find_all("tr", class_="even"):
            name = row.find("a", class_="spielprofil_tooltip").text if row.find("a", class_="spielprofil_tooltip") else None
            image = row.find("img", class_="bilderrahmen-fixed")['src'] if row.find("img", class_="bilderrahmen-fixed") else None
            fee = row.find("td", class_="rechts").text.strip() if row.find("td", class_="rechts") else None

            if name and image and fee:
                players.append({"Name": name, "Image URL": image, "Transfer Fee": fee})
        
        return pd.DataFrame(players)
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return pd.DataFrame()

# Fetch data from Transfermarkt
data = scrape_transfermarkt()

# Home Page
if page == "Home":
    st.header("Welcome to the Football Transfer Analytics Tool")
    st.write("""
    - Explore player transfers, images, and other data scraped from Transfermarkt.  
    - Use advanced tools like trend analysis and player search.
    """)

# Player Search Page
elif page == "Player Search":
    st.header("🔎 Player Transfer Search")
    player_name = st.text_input("Enter Player Name")
    if player_name and not data.empty:
        search_results = data[data['Name'].str.contains(player_name, case=False, na=False)]
        if not search_results.empty:
            for _, row in search_results.iterrows():
                st.image(row["Image URL"], width=100)
                st.write(f"**{row['Name']}**")
                st.write(f"**Transfer Fee**: {row['Transfer Fee']}")
        else:
            st.warning("No results found for the given player.")
    elif not player_name:
        st.info("Enter a player's name to search.")
    else:
        st.warning("No data available.")

# Transfer Trends Page (Example of trend analysis)
elif page == "Transfer Trends":
    st.header("📈 Transfer Trends")
    if not data.empty:
        data['Transfer Fee'] = data['Transfer Fee'].apply(lambda x: float(x.replace('€', '').replace('M', '').replace(',', '').strip()) if x else 0)
        trends = data.groupby("Name")["Transfer Fee"].sum().reset_index()
        st.dataframe(trends.sort_values(by="Transfer Fee", ascending=False).head(10))
    else:
        st.warning("No data available.")

# Footer
st.markdown("""
    <div class='footer'>
        Built with ❤️ by <b>DEV ALVEXD</b>. Empowering football insights from Transfermarkt.
    </div>
""", unsafe_allow_html=True)
