import streamlit as st
import pandas as pd
import numpy as np
from utils import load_data, get_teams

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(
    page_title="Fantasy Team Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Fantasy Team Generator")
st.markdown("**Build your optimal fantasy cricket team with data-driven insights**")

matches, deliveries = load_data()

# Fantasy cricket constants
MAX_BUDGET = 100
MIN_PLAYERS = 11
MAX_PLAYERS = 11
MAX_FROM_TEAM = 7

# Player roles and base prices (simplified)
PLAYER_ROLES = {
    'WK': ['MS Dhoni', 'KD Karthik', 'RR Pant', 'KL Rahul', 'RV Uthappa', 'Q de Kock', 'Dinesh Karthik'],
    'BAT': ['V Kohli', 'S Dhawan', 'RG Sharma', 'DA Warner', 'SK Raina', 'AB de Villiers', 'CH Gayle', 'AM Rahane', 'F du Plessis'],
    'AR': ['R Jadeja', 'DJ Bravo', 'RA Jadeja', 'YK Pathan', 'JP Duminy', 'AT Rayudu', 'SPD Smith'],
    'BOWL': ['R Ashwin', 'JJ Bumrah', 'YS Chahal', 'Mohammed Shami', 'Harbhajan Singh', 'PP Chawla', 'A Mishra', 'UT Yadav']
}

# Calculate player statistics
@st.cache_data
def calculate_player_stats():
    # Batting stats
    batting_stats = deliveries.groupby('batter').agg({
        'batsman_runs': ['sum', 'count', 'mean'],
        'is_wicket': 'sum'
    }).fillna(0)

    batting_stats.columns = ['total_runs', 'balls_faced', 'avg_runs_per_ball', 'dismissals']
    batting_stats['batting_avg'] = batting_stats['total_runs'] / batting_stats['dismissals'].replace(0, 1)
    batting_stats['strike_rate'] = (batting_stats['total_runs'] / batting_stats['balls_faced'] * 100).fillna(0)

    # Bowling stats
    bowling_stats = deliveries.groupby('bowler').agg({
        'is_wicket': 'sum',
        'total_runs': 'sum',
        'over': 'nunique'
    }).fillna(0)

    bowling_stats.columns = ['wickets', 'runs_conceded', 'overs_bowled']
    bowling_stats['bowling_avg'] = bowling_stats['runs_conceded'] / bowling_stats['wickets'].replace(0, 1)
    bowling_stats['economy'] = bowling_stats['runs_conceded'] / bowling_stats['overs_bowled'].replace(0, 1)

    return batting_stats, bowling_stats

batting_stats, bowling_stats = calculate_player_stats()

# Calculate fantasy points (simplified Dream11-style system)
@st.cache_data
def calculate_fantasy_points():
    # Get top players by runs
    top_batsmen = batting_stats.nlargest(50, 'total_runs')

    # Get top bowlers by wickets
    top_bowlers = bowling_stats.nlargest(30, 'wickets')

    # Combine and calculate fantasy points
    all_players = []

    for player in top_batsmen.index:
        stats = batting_stats.loc[player]
        # Fantasy points calculation (simplified)
        points = (
            stats['total_runs'] * 1 +  # 1 point per run
            (stats['total_runs'] // 50) * 5 +  # Bonus for fifties
            (stats['total_runs'] // 100) * 10 +  # Bonus for centuries
            stats['strike_rate'] // 10  # Strike rate bonus
        )
        all_players.append({
            'name': player,
            'role': 'BAT',
            'points': points,
            'runs': stats['total_runs'],
            'avg': stats['batting_avg'],
            'sr': stats['strike_rate']
        })

    for player in top_bowlers.index:
        stats = bowling_stats.loc[player]
        # Fantasy points for bowlers
        points = (
            stats['wickets'] * 25 +  # 25 points per wicket
            (stats['wickets'] // 3) * 10 +  # Bonus for 3-wicket hauls
            (stats['wickets'] // 5) * 20  # Bonus for 5-wicket hauls
        )
        all_players.append({
            'name': player,
            'role': 'BOWL',
            'points': points,
            'wickets': stats['wickets'],
            'avg': stats['bowling_avg'],
            'economy': stats['economy']
        })

    return pd.DataFrame(all_players).drop_duplicates(subset='name')

fantasy_players = calculate_fantasy_points()

# Sidebar for team building
st.sidebar.header("⚙️ Team Builder")

budget = st.sidebar.slider("Budget (in lakhs)", min_value=50, max_value=MAX_BUDGET, value=MAX_BUDGET)
strategy = st.sidebar.selectbox("Strategy", ["Balanced", "Aggressive", "Conservative", "Wicket-Taking"])

# Team composition requirements
st.sidebar.subheader("Team Composition")
wk_count = st.sidebar.slider("Wicket-Keepers", 1, 4, 1)
bat_count = st.sidebar.slider("Batsmen", 3, 6, 4)
ar_count = st.sidebar.slider("All-Rounders", 1, 4, 2)
bowl_count = st.sidebar.slider("Bowlers", 3, 5, 4)

total_selected = wk_count + bat_count + ar_count + bowl_count
if total_selected != 11:
    st.sidebar.error(f"Total players must be 11. Currently: {total_selected}")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Build Team", "📊 Player Stats", "📈 Analysis", "💡 Recommendations"])

with tab1:
    st.header("🏏 Build Your Fantasy Team")

    if total_selected != 11:
        st.error("Please adjust player counts to total 11 players.")
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Available Players")

            # Filter players by role and sort by points
            wk_players = fantasy_players[fantasy_players['role'] == 'BAT'].head(10)  # Simplified
            bat_players = fantasy_players[fantasy_players['role'] == 'BAT'].head(15)
            bowl_players = fantasy_players[fantasy_players['role'] == 'BOWL'].head(15)

            # Display players by category
            st.write("**Wicket-Keepers:**")
            for _, player in wk_players.head(wk_count * 2).iterrows():
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                with col_a:
                    selected = st.checkbox(f"{player['name']}", key=f"wk_{player['name']}")
                with col_b:
                    st.write(f"{player['points']:.0f} pts")
                with col_c:
                    st.write(f"{player.get('runs', 0):.0f} runs")
                with col_d:
                    st.write(f"{player.get('avg', 0):.1f} avg")

            st.write("**Batsmen:**")
            for _, player in bat_players.head(bat_count * 3).iterrows():
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                with col_a:
                    selected = st.checkbox(f"{player['name']}", key=f"bat_{player['name']}")
                with col_b:
                    st.write(f"{player['points']:.0f} pts")
                with col_c:
                    st.write(f"{player.get('runs', 0):.0f} runs")
                with col_d:
                    st.write(f"{player.get('avg', 0):.1f} avg")

            st.write("**Bowlers:**")
            for _, player in bowl_players.head(bowl_count * 3).iterrows():
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                with col_a:
                    selected = st.checkbox(f"{player['name']}", key=f"bowl_{player['name']}")
                with col_b:
                    st.write(f"{player['points']:.0f} pts")
                with col_c:
                    st.write(f"{player.get('wickets', 0):.0f} wkts")
                with col_d:
                    st.write(f"{player.get('avg', 0):.1f} avg")

        with col2:
            st.subheader("Your Team")

            # Calculate selected players and budget
            selected_players = []
            total_cost = 0
            total_points = 0

            # This is a simplified version - in reality you'd track selections
            st.info("Team selection logic would go here")
            st.metric("Budget Used", f"₹{total_cost}L", f"₹{budget - total_cost}L remaining")
            st.metric("Total Points", total_points)

            if st.button("🚀 Generate Optimal Team", type="primary"):
                st.success("Optimal team generated based on your strategy!")

                # Show recommended team
                st.subheader("Recommended XI")

                # Get top players by strategy
                if strategy == "Aggressive":
                    recommended = fantasy_players.nlargest(11, 'points')
                elif strategy == "Wicket-Taking":
                    bowlers = fantasy_players[fantasy_players['role'] == 'BOWL'].nlargest(5, 'wickets')
                    others = fantasy_players[fantasy_players['role'] != 'BOWL'].nlargest(6, 'points')
                    recommended = pd.concat([bowlers, others])
                else:  # Balanced
                    recommended = fantasy_players.nlargest(11, 'points')

                for i, (_, player) in enumerate(recommended.iterrows(), 1):
                    st.write(f"{i}. {player['name']} ({player['role']}) - {player['points']:.0f} pts")

with tab2:
    st.header("📊 Player Statistics")

    # Player search and filter
    search_term = st.text_input("Search Player", "")

    role_filter = st.selectbox("Filter by Role", ["All", "BAT", "BOWL", "WK", "AR"])

    # Filter players
    filtered_players = fantasy_players.copy()
    if search_term:
        filtered_players = filtered_players[filtered_players['name'].str.contains(search_term, case=False)]
    if role_filter != "All":
        filtered_players = filtered_players[filtered_players['role'] == role_filter]

    # Display player stats
    if not filtered_players.empty:
        st.dataframe(filtered_players.sort_values('points', ascending=False).head(20))

        # Top performers chart
        if PLOTLY_AVAILABLE:
            fig = px.bar(
                filtered_players.nlargest(10, 'points'),
                x='name',
                y='points',
                title="Top Fantasy Performers",
                color='role'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found matching your criteria.")

with tab3:
    st.header("📈 Fantasy Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Points Distribution")
        if PLOTLY_AVAILABLE:
            fig = px.histogram(fantasy_players, x='points', nbins=20, title="Fantasy Points Distribution")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Role Distribution")
        role_counts = fantasy_players['role'].value_counts()
        if PLOTLY_AVAILABLE:
            fig = px.pie(values=role_counts.values, names=role_counts.index, title="Player Roles")
            st.plotly_chart(fig, use_container_width=True)

    # Performance insights
    st.subheader("💡 Key Insights")

    top_scorer = fantasy_players.loc[fantasy_players['points'].idxmax()]
    st.metric("Highest Fantasy Points", f"{top_scorer['points']:.0f}", f"by {top_scorer['name']}")

    avg_points = fantasy_players['points'].mean()
    st.metric("Average Fantasy Points", f"{avg_points:.1f}")

    # Role-wise analysis
    role_avg = fantasy_players.groupby('role')['points'].mean().sort_values(ascending=False)
    st.write("**Average Points by Role:**")
    st.dataframe(role_avg.to_frame())

with tab4:
    st.header("💡 Fantasy Recommendations")

    st.subheader("Strategy Tips")

    tips = {
        "Balanced": [
            "Mix of top-order batsmen and reliable bowlers",
            "Include 1-2 all-rounders for flexibility",
            "Focus on players with consistent performance"
        ],
        "Aggressive": [
            "Prioritize high-risk, high-reward players",
            "Focus on players with high strike rates",
            "Include pace bowlers for wicket-taking potential"
        ],
        "Conservative": [
            "Choose proven performers with consistent stats",
            "Include reliable wicket-keepers",
            "Balance with steady all-rounders"
        ],
        "Wicket-Taking": [
            "Prioritize bowlers with good economy rates",
            "Include specialist wicket-keepers",
            "Focus on teams with strong bowling attacks"
        ]
    }

    selected_tips = tips.get(strategy, tips["Balanced"])

    for tip in selected_tips:
        st.write(f"• {tip}")

    st.subheader("Captain/Vice-Captain Suggestions")

    # Suggest captain based on recent form (simplified)
    captain_suggestion = fantasy_players.nlargest(3, 'points')
    st.write("**Captain Options:**")
    for _, player in captain_suggestion.iterrows():
        st.write(f"🏏 {player['name']} - {player['points']:.0f} points")

    st.subheader("Must-Pick Players")
    must_picks = fantasy_players.nlargest(5, 'points')
    for _, player in must_picks.iterrows():
        st.write(f"⭐ {player['name']} ({player['role']})")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>Fantasy Team Generator</strong></p>
    <p>Data-driven fantasy cricket team selection • Powered by IPL statistics</p>
    <p>🏏 Build your winning XI with analytics</p>
</div>
""", unsafe_allow_html=True)