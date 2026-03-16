import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="IPL Data Analysis", layout="wide")

# -----------------------------
# Title
# -----------------------------
st.title("🏏 IPL Data Analysis Dashboard")
st.write("Explore IPL trends, team performances, batsman stats, and bowler insights.")

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    matches = pd.read_csv("matches.csv")
    deliveries = pd.read_csv("deliveries.csv")
    return matches, deliveries

matches, deliveries = load_data()

# -----------------------------
# Sidebar Navigation
# -----------------------------
menu = st.sidebar.selectbox(
    "Select Analysis",
    [
        "Dataset Overview",
        "Team Analysis",
        "Batsman Stats",
        "Bowler Stats",
        "Winning Probability"
    ]
)

# -----------------------------
# Dataset Overview
# -----------------------------
if menu == "Dataset Overview":

    st.header("Dataset Overview")

    st.subheader("Matches Dataset")
    st.dataframe(matches.head())

    st.subheader("Deliveries Dataset")
    st.dataframe(deliveries.head())

    st.write("Number of Matches:", matches.shape[0])
    st.write("Number of Deliveries:", deliveries.shape[0])

# -----------------------------
# Team Analysis
# -----------------------------
elif menu == "Team Analysis":

    st.header("Team Analysis")

    st.subheader("Teams with Most Wins")

    wins = matches['winner'].value_counts()

    fig, ax = plt.subplots()
    wins.plot(kind='bar', ax=ax)
    ax.set_ylabel("Wins")
    ax.set_xlabel("Teams")
    st.pyplot(fig)

    st.subheader("Highest Team Scores")

    team_scores = deliveries.groupby(['match_id', 'batting_team'])['total_runs'].sum().reset_index()
    highest_scores = team_scores.sort_values('total_runs', ascending=False).head(10)

    st.dataframe(highest_scores)

# -----------------------------
# Batsman Stats
# -----------------------------
elif menu == "Batsman Stats":

    st.header("Batsman Statistics")

    batsman_runs = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False)

    st.subheader("Top 10 Run Scorers")

    top10 = batsman_runs.head(10)

    fig, ax = plt.subplots()
    top10.plot(kind='bar', ax=ax)
    ax.set_ylabel("Runs")
    st.pyplot(fig)

    st.subheader("Most Sixes")

    sixes = deliveries[deliveries['batsman_runs'] == 6]
    sixes_count = sixes.groupby('batter').size().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots()
    sixes_count.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# -----------------------------
# Bowler Stats
# -----------------------------
elif menu == "Bowler Stats":

    st.header("Bowler Statistics")

    wickets = deliveries[deliveries['dismissal_kind'].notna()]
    bowler_wickets = wickets.groupby('bowler').size().sort_values(ascending=False)

    st.subheader("Top 10 Bowlers")

    top10 = bowler_wickets.head(10)

    fig, ax = plt.subplots()
    top10.plot(kind='bar', ax=ax)
    ax.set_ylabel("Wickets")
    st.pyplot(fig)

# -----------------------------
# Winning Probability
# -----------------------------
elif menu == "Winning Probability":

    st.header("Winning Probability of Two Teams")

    teams = matches['team1'].unique()

    team1 = st.selectbox("Select Team 1", teams)
    team2 = st.selectbox("Select Team 2", teams)

    head_to_head = matches[
        ((matches['team1'] == team1) & (matches['team2'] == team2)) |
        ((matches['team1'] == team2) & (matches['team2'] == team1))
    ]

    wins = head_to_head['winner'].value_counts()

    st.write("Head to Head Record")

    st.write(wins)

    fig, ax = plt.subplots()
    wins.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# -----------------------------
# Footer
# -----------------------------
st.sidebar.write("👨‍💻 Developed by Bhupendra Sahu")
