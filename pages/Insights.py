import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None

from utils import load_data

st.title("📌 Insights & Conclusions")

matches, deliveries = load_data()

st.markdown("""
## Key Insights from IPL Data Analysis

Based on comprehensive analysis of IPL matches from 2008-2022, here are the major findings:
""")

# 1. Teams chasing have higher win probability
st.header("1. 🏃 Teams Chasing Have Higher Win Probability")

chasing_matches = matches[matches['toss_decision'] == 'field']
batting_first_matches = matches[matches['toss_decision'] == 'bat']

chasing_wins = len(chasing_matches[chasing_matches['toss_winner'] == chasing_matches['winner']])
batting_first_wins = len(batting_first_matches[batting_first_matches['toss_winner'] == batting_first_matches['winner']])

chasing_win_rate = (chasing_wins / len(chasing_matches)) * 100 if len(chasing_matches) > 0 else 0
batting_win_rate = (batting_first_wins / len(batting_first_matches)) * 100 if len(batting_first_matches) > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("Chasing Win Rate", f"{chasing_win_rate:.1f}%", f"+{chasing_win_rate - batting_win_rate:.1f}%")
    st.metric("Chasing Matches", len(chasing_matches))

with col2:
    st.metric("Batting First Win Rate", f"{batting_win_rate:.1f}%")
    st.metric("Batting First Matches", len(batting_first_matches))

# Visualization
if px and go:
    fig1 = go.Figure(data=[
        go.Bar(name='Chasing', x=['Win Rate'], y=[chasing_win_rate], marker_color='green'),
        go.Bar(name='Batting First', x=['Win Rate'], y=[batting_win_rate], marker_color='blue')
    ])
    fig1.update_layout(title="Win Rates: Chasing vs Batting First", barmode='group')
    st.plotly_chart(fig1)
else:
    st.warning("Plotly not available. Install plotly to see visualizations.")

st.markdown(f"""
**Analysis**: Teams that win the toss and choose to field (chasing) have a **{chasing_win_rate:.1f}%** win rate compared to **{batting_win_rate:.1f}%** for teams batting first.
This suggests that chasing might be psychologically advantageous in IPL cricket.
""")

# 2. Top-order batsmen dominate scoring
st.header("2. 🏏 Top-Order Batsmen Dominate Scoring")

# Calculate runs by batsman
batter_runs = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False)

# Get top 10 batsmen
top_batsmen = batter_runs.head(10)

if px:
    fig2 = px.bar(top_batsmen, x=top_batsmen.index, y=top_batsmen.values,
                  title="Top 10 Run Scorers in IPL History",
                  labels={'x': 'Batsman', 'y': 'Total Runs'})
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2)
else:
    st.warning("Plotly not available. Install plotly to see visualizations.")
    st.dataframe(top_batsmen)

# Calculate percentage of total runs by top batsmen
total_runs = deliveries['batsman_runs'].sum()
top_10_runs = top_batsmen.sum()
top_10_percentage = (top_10_runs / total_runs) * 100

st.metric("Runs by Top 10 Batsmen", f"{top_10_runs:,}", f"{top_10_percentage:.1f}% of total runs")

st.markdown(f"""
**Analysis**: The top 10 batsmen in IPL history have scored **{top_10_runs:,}** runs, which represents **{top_10_percentage:.1f}%** of all runs scored.
This shows that a small group of elite batsmen dominate the scoring, with Virat Kohli leading with {batter_runs.iloc[0]:,} runs.
""")

# 3. Certain venues favor high scoring
st.header("3. 🏟️ Certain Venues Favor High Scoring")

# Calculate average target runs by venue (excluding NaN)
venue_scores = matches.groupby('venue')['target_runs'].mean().dropna().sort_values(ascending=False)

# Get top 10 high-scoring venues
top_venues = venue_scores.head(10)

if px:
    fig3 = px.bar(top_venues, x=top_venues.index, y=top_venues.values,
                  title="Top 10 High-Scoring Venues",
                  labels={'x': 'Venue', 'y': 'Average Target Runs'})
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3)
else:
    st.warning("Plotly not available. Install plotly to see visualizations.")
    st.dataframe(top_venues)

# Venue comparison
col1, col2 = st.columns(2)
with col1:
    st.metric("Highest Scoring Venue", venue_scores.index[0][:30] + "...",
              f"{venue_scores.iloc[0]:.1f} avg runs")
with col2:
    st.metric("Lowest Scoring Venue", venue_scores.index[-1][:30] + "...",
              f"{venue_scores.iloc[-1]:.1f} avg runs")

st.markdown(f"""
**Analysis**: Venue conditions significantly impact scoring in IPL cricket. The **{venue_scores.index[0]}** has the highest average target of **{venue_scores.iloc[0]:.1f}** runs,
while **{venue_scores.index[-1]}** has the lowest at **{venue_scores.iloc[-1]:.1f}** runs.
This suggests that teams should adapt their strategies based on venue characteristics.
""")

# Additional insights
st.header("📊 Additional Statistical Insights")

# Win percentage by season
season_wins = matches.groupby('season').agg({
    'id': 'count',
    'winner': lambda x: x.notna().sum()
}).rename(columns={'id': 'total_matches', 'winner': 'completed_matches'})

season_wins['win_percentage'] = (season_wins['completed_matches'] / season_wins['total_matches']) * 100

if px:
    fig4 = px.line(season_wins, x=season_wins.index, y='win_percentage',
                   title="Match Completion Rate by Season",
                   labels={'x': 'Season', 'y': 'Completion Rate (%)'})
    st.plotly_chart(fig4)
else:
    st.warning("Plotly not available. Install plotly to see visualizations.")
    st.dataframe(season_wins)

# Toss impact analysis
toss_impact = matches.groupby(['toss_decision', 'winner']).size().unstack().fillna(0)
toss_impact['total'] = toss_impact.sum(axis=1)
toss_impact['win_rate'] = (toss_impact['toss_winner'] / toss_impact['total']) * 100

st.subheader("Toss Decision Impact")
st.dataframe(toss_impact[['win_rate']].round(1))

st.markdown("""
### 🎯 Strategic Recommendations

1. **For Teams**: When winning toss, consider chasing to leverage the psychological advantage
2. **For Batsmen**: Focus on developing top-order batsmen as they contribute disproportionately to team scores
3. **For Captains**: Study venue statistics and adjust team composition and strategy accordingly
4. **For Fantasy Players**: Prioritize top-order batsmen and consider venue factors in team selection

### 📈 Data Summary
- **Total Matches Analyzed**: {len(matches):,}
- **Total Deliveries**: {len(deliveries):,}
- **Seasons Covered**: {len(matches['season'].unique())}
- **Teams**: {len(matches['team1'].unique())}
""".format(len(matches), len(deliveries), len(matches['season'].unique()), len(matches['team1'].unique())))