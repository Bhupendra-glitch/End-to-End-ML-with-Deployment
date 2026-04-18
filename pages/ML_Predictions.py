import streamlit as st
import pandas as pd
import numpy as np
from utils import load_data, get_teams

# Try to import scikit-learn components
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    st.error("❌ scikit-learn is not available. Please install it with: `pip install scikit-learn`")

st.title("🤖 Machine Learning Predictions")

matches, deliveries = load_data()
teams = get_teams(matches)

if not SKLEARN_AVAILABLE:
    st.error("⚠️ Machine Learning features are disabled due to missing scikit-learn dependency.")
    st.info("To enable ML predictions, run: `pip install scikit-learn`")
    st.stop()

# Create tabs for different prediction types
tab1, tab2, tab3 = st.tabs(["🏆 Match Winner Prediction", "📊 Score Prediction", "📈 Model Performance"])

with tab1:
    st.header("🏆 Match Winner Prediction")

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Select Team 1", teams, key="pred_team1")
        venue = st.selectbox("Venue", sorted(matches['venue'].dropna().unique()), key="venue")

    with col2:
        team2 = st.selectbox("Select Team 2", teams, key="pred_team2")
        toss_winner = st.selectbox("Toss Winner", [team1, team2], key="toss_winner")
        toss_decision = st.selectbox("Toss Decision", ["bat", "field"], key="toss_decision")

    if st.button("🔮 Predict Match Winner", type="primary"):
        with st.spinner("Training model and making prediction..."):
            # Prepare data for training
            pred_data = matches[['team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'winner']].dropna()

            if len(pred_data) == 0:
                st.error("Not enough data for prediction. Please check your dataset.")
                st.stop()

            # Create features
            X = pd.get_dummies(pred_data[['team1', 'team2', 'venue', 'toss_winner', 'toss_decision']])
            y = pred_data['winner']

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            # Test accuracy
            test_accuracy = accuracy_score(y_test, model.predict(X_test))

            # Make prediction
            pred_features = pd.DataFrame({
                'team1': [team1],
                'team2': [team2],
                'venue': [venue],
                'toss_winner': [toss_winner],
                'toss_decision': [toss_decision]
            })

            pred_X = pd.get_dummies(pred_features)

            # Align columns with training data
            for col in X_train.columns:
                if col not in pred_X.columns:
                    pred_X[col] = 0
            pred_X = pred_X[X_train.columns]

            prediction = model.predict(pred_X)[0]
            probas = model.predict_proba(pred_X)[0]

            # Get team names and probabilities
            team_names = model.classes_
            team1_idx = list(team_names).index(team1) if team1 in team_names else -1
            team2_idx = list(team_names).index(team2) if team2 in team_names else -1

            team1_prob = probas[team1_idx] * 100 if team1_idx >= 0 else 0
            team2_prob = probas[team2_idx] * 100 if team2_idx >= 0 else 0

            # Display results
            st.success(f"🏆 Predicted Winner: **{prediction}**")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"{team1} Win Probability", f"{team1_prob:.1f}%")
            with col2:
                st.metric(f"{team2} Win Probability", f"{team2_prob:.1f}%")

            st.info(f"🤖 Model Accuracy: {test_accuracy:.1f}% (based on test data)")

            # Additional insights
            st.subheader("📋 Prediction Insights")

            # Head-to-head record
            h2h_matches = matches[((matches['team1'] == team1) & (matches['team2'] == team2)) |
                                 ((matches['team1'] == team2) & (matches['team2'] == team1))]
            if len(h2h_matches) > 0:
                team1_h2h_wins = len(h2h_matches[h2h_matches['winner'] == team1])
                team2_h2h_wins = len(h2h_matches[h2h_matches['winner'] == team2])
                st.write(f"**Head-to-Head Record:** {team1}: {team1_h2h_wins} wins, {team2}: {team2_h2h_wins} wins")

            # Venue performance
            venue_matches = matches[matches['venue'] == venue]
            if len(venue_matches) > 0:
                venue_avg_score = venue_matches['target_runs'].mean()
                st.write(f"**Venue Average Score:** {venue_avg_score:.1f} runs")

with tab2:
    st.header("📊 Score Prediction")

    col1, col2 = st.columns(2)

    with col1:
        score_team1 = st.selectbox("Batting Team", teams, key="score_team1")
        score_venue = st.selectbox("Venue", sorted(matches['venue'].dropna().unique()), key="score_venue")
        overs_completed = st.slider("Overs Completed", 0, 20, 10)

    with col2:
        current_score = st.number_input("Current Score", min_value=0, value=100)
        wickets_lost = st.slider("Wickets Lost", 0, 10, 2)
        score_team2 = st.selectbox("Bowling Team", teams, key="score_team2")

    if st.button("🎯 Predict Final Score", type="primary"):
        with st.spinner("Analyzing historical data for score prediction..."):
            # Simple score prediction based on historical averages
            venue_matches = matches[matches['venue'] == score_venue]
            team_matches = matches[(matches['team1'] == score_team1) | (matches['team2'] == score_team1)]

            if len(venue_matches) > 0 and len(team_matches) > 0:
                venue_avg = venue_matches['target_runs'].mean()
                team_avg = team_matches[team_matches['winner'] == score_team1]['target_runs'].mean()

                # Calculate predicted score based on current situation
                remaining_overs = 20 - overs_completed
                remaining_balls = remaining_overs * 6

                # Simple linear prediction (this could be enhanced with ML)
                avg_runs_per_ball = venue_avg / 120  # Average runs per ball in T20
                predicted_remaining = remaining_balls * avg_runs_per_ball

                final_prediction = current_score + predicted_remaining

                # Adjust for wickets
                wicket_penalty = wickets_lost * 10  # Rough estimate
                final_prediction -= wicket_penalty

                st.success(f"🎯 Predicted Final Score: **{max(0, int(final_prediction))}** runs")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Score", current_score)
                with col2:
                    st.metric("Predicted Total", f"{max(0, int(final_prediction))}")
                with col3:
                    st.metric("Runs Needed", f"{max(0, int(final_prediction - current_score))}")

                # Historical comparison
                st.subheader("📈 Historical Comparison")
                venue_scores = venue_matches['target_runs'].describe()
                st.write(f"**Venue Average:** {venue_scores['mean']:.1f} runs")
                st.write(f"**Venue Range:** {venue_scores['min']:.0f} - {venue_scores['max']:.0f} runs")

            else:
                st.error("Not enough historical data for this combination.")

with tab3:
    st.header("📈 Model Performance Analysis")

    if st.button("🔍 Analyze Model Performance", type="primary"):
        with st.spinner("Analyzing model performance..."):
            # Prepare comprehensive dataset
            analysis_data = matches[['team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'winner']].dropna()

            if len(analysis_data) < 50:
                st.error("Not enough data for comprehensive analysis.")
                st.stop()

            # Create features
            X = pd.get_dummies(analysis_data[['team1', 'team2', 'venue', 'toss_winner', 'toss_decision']])
            y = analysis_data['winner']

            # Multiple train-test splits for robust evaluation
            accuracies = []
            for i in range(5):
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=i)
                model = RandomForestClassifier(n_estimators=100, random_state=i)
                model.fit(X_train, y_train)
                pred = model.predict(X_test)
                accuracies.append(accuracy_score(y_test, pred))

            avg_accuracy = np.mean(accuracies)
            std_accuracy = np.std(accuracies)

            st.success(f"🎯 Average Model Accuracy: **{avg_accuracy:.1f}%** (±{std_accuracy:.1f}%)")

            # Feature importance
            st.subheader("🔍 Feature Importance")
            model.fit(X, y)  # Fit on full dataset for feature importance
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False).head(10)

            st.dataframe(feature_importance)

            # Confusion matrix style analysis
            st.subheader("📊 Team-wise Performance")
            team_performance = analysis_data.groupby('winner').size().sort_values(ascending=False)
            st.bar_chart(team_performance)

            # Model insights
            st.subheader("💡 Model Insights")
            st.info(f"""
            - **Best Performing Teams:** {team_performance.index[0]} ({team_performance.iloc[0]} wins)
            - **Most Predictive Factor:** {feature_importance.iloc[0]['feature']} ({feature_importance.iloc[0]['importance']:.3f})
            - **Model Stability:** {std_accuracy:.3f} standard deviation across runs
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>Machine Learning Predictions</strong></p>
    <p>Powered by Random Forest Classifier • Real-time model training on IPL data</p>
</div>
""", unsafe_allow_html=True)