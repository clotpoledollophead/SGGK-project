# app.py (Main file)
import streamlit as st
import pandas as pd

# Import all modules
from config import set_page_config
from data_loader import load_data
from stats_section import display_stats_section
from visualizations import display_visualizations
from word_search import display_word_search
from distribution_analysis import display_distribution_analysis
from about_section import display_about_section

# Set page configuration
set_page_config()

# Title and description
st.title("Sir Gawain and the Green Knight: A Text Analysis")
st.markdown("### Textual Visualization of Sir Gawain and the Green Knight")

# Introduction
st.markdown("""
This application provides an interactive exploration of *Sir Gawain and the Green Knight*, 
a 14th-century Middle English poem. Through various visualizations, we can explore word 
patterns, frequencies, and distributions within this medieval masterpiece.
""")

# Load the data
df = load_data()

if df is not None:
    # Display stats section
    word_freq = display_stats_section(df)
    
    # Display visualizations
    display_visualizations(df)
    
    # Display word search
    display_word_search(df)
    
    # Display distribution analysis
    display_distribution_analysis()
else:
    st.error("Could not load the data. Please ensure 'word_occurrences.csv' is in the same directory as this script.")

# Display about section
display_about_section()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 12px; color: grey;">
      &copy; Hsin-Ying Lee, 2025. Licensed under the Apache License 2.0.
      <a href="https://github.com/clotpoledollophead/SGGK-project/blob/main/LICENSE" style="color: grey;">View license</a>
    </div><br>
    <div style='text-align: center; color: #666; font-size: 0.875rem;'>
    Middle English Text Word Frequency Analysis | Created with Streamlit and Plotly
    </div>
    """,
    unsafe_allow_html=True
)