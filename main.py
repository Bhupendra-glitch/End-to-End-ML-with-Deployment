import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page Title
st.title("🏏 IPL Data Analysis Dashboard")
st.write("Interactive IPL analysis using Streamlit")

# Load dataset
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries.csv")

# Sidebar
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Select Analysis",
    ("Home", "Team Wins", "Top Run Scorers", "Top Wicket Takers")
)

# Home Page
if option == "Home":
    st.header("IPL Dataset Overview")
    st.write(matches.head())
    st.write("Total Matches:", matches.shape[0])
    st.write("Total Teams:", matches['team1'].nunique())

# Team Wins Analysis
elif option == "Team Wins":

    st.header("🏆 Team Wins Analysis")

    team_wins = matches['winner'].value_counts()

    fig, ax = plt.subplots()
    team_wins.plot(kind='bar', ax=ax)

    plt.title("Total Wins by Team")
    plt.xlabel("Team")
    plt.ylabel("Wins")

    st.pyplot(fig)

# Top Run Scorers
elif option == "Top Run Scorers":

    st.header("🏏 Top Run Scorers")

    runs = deliveries.groupby('batter')['batsman_runs'].sum()
    top_runs = runs.sort_values(ascending=False).head(10)

    fig, ax = plt.subplots()

    sns.barplot(
        x=top_runs.values,
        y=top_runs.index,
        ax=ax
    )

    plt.title("Top 10 Run Scorers in IPL")

    st.pyplot(fig)

# Top Wicket Takers
elif option == "Top Wicket Takers":

    st.header("🎯 Top Wicket Takers")

    wickets = deliveries[deliveries['dismissal_kind'] != "run out"]
    wickets = wickets.groupby('bowler')['player_dismissed'].count()

    top_wickets = wickets.sort_values(ascending=False).head(10)

    fig, ax = plt.subplots()

    sns.barplot(
        x=top_wickets.values,
        y=top_wickets.index,
        ax=ax
    )

    plt.title("Top 10 Wicket Takers")

    st.pyplot(fig)