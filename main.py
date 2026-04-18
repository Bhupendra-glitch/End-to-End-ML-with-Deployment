"""
IPL Data Analysis and Prediction Dashboard
==========================================

This project provides a comprehensive analysis of Indian Premier League (IPL) cricket data
with machine learning predictions and interactive visualizations.

Project Overview:
----------------
- Dataset: IPL matches (2008-2022) and ball-by-ball deliveries data
- Technologies: Python, Streamlit, Pandas, Scikit-learn, Plotly
- Features: Exploratory Data Analysis, Player Performance Analysis, Team Analysis,
           Head-to-Head Comparisons, Venue Analysis, Season Trends, ML Predictions

Key Analysis Areas:
------------------
1. Data Preprocessing: Cleaning and preparing IPL datasets
2. Exploratory Data Analysis: Statistical insights and visualizations
3. Player Analysis: Individual player performance metrics
4. Team Analysis: Team-wise statistics and comparisons
5. Head-to-Head: Team vs Team performance analysis
6. Venue Analysis: Impact of venues on match outcomes
7. Season Trends: Year-wise performance patterns
8. ML Predictions: Score prediction and match winner prediction
9. Fantasy Team Generator: Optimal team selection
10. Live Match Predictor: Real-time match predictions

Data Sources:
------------
- matches.csv: Contains match-level information (season, teams, winner, etc.)
- deliveries.csv: Ball-by-ball delivery data (runs, wickets, players, etc.)

Machine Learning Models:
-----------------------
- Score Prediction: Regression models to predict final scores
- Winner Prediction: Classification models for match outcomes
- Player Performance: Statistical modeling for fantasy points

Usage:
-----
Run the application using: streamlit run app.py
Navigate through different analysis sections using the sidebar.

Author: IPL Analytics Team
Version: 1.0
Date: 2024
"""

import streamlit as st

st.set_page_config(
    page_title="IPL Analysis",
    page_icon="🏏",
    initial_sidebar_state="expanded",
    layout="wide"
)

import app
import homePage
import exploratoryDataAnalysis
import playerAnalysis
import batter_vs_bowlerAnalysis
import teamAnalysis
import team_vs_teamAnalysis
import scorePrediction
import winnerPrediction

