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

# Create a more visually appealing navigation menu
st.sidebar.title("Navigation")

# Load external CSS file
def load_css(css_file):
    with open(css_file, 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the CSS
load_css('style.css')

# Initialize session state for page navigation if not already set
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

# Function to change page
def nav_to(page_name):
    st.session_state['page'] = page_name
    
# Create custom styled navigation buttons
with st.sidebar:
    # Add some spacing and styling
    st.markdown('<div style="margin-bottom: 15px;"></div>', unsafe_allow_html=True)
    
    # Create custom buttons with conditional styling
    if st.button('Home', key='home_btn', 
                use_container_width=True, 
                type="primary" if st.session_state['page'] == 'Home' else "secondary"):
        nav_to('Home')
        
    if st.button('Textual Analysis', key='analysis_btn', 
                use_container_width=True,
                type="primary" if st.session_state['page'] == 'Textual Analysis' else "secondary"):
        nav_to('Textual Analysis')
        
    if st.button('Word Search', key='search_btn', 
                use_container_width=True,
                type="primary" if st.session_state['page'] == 'Word Search' else "secondary"):
        nav_to('Word Search')
        
    if st.button('Distribution Analysis', key='dist_btn', 
                use_container_width=True,
                type="primary" if st.session_state['page'] == 'Distribution Analysis' else "secondary"):
        nav_to('Distribution Analysis')
        
    if st.button('About', key='about_btn', 
                use_container_width=True,
                type="primary" if st.session_state['page'] == 'About' else "secondary"):
        nav_to('About')
        
# Get current page from session state
page = st.session_state['page']

# Title (shown on all pages)
st.title("Sir Gawain and the Green Knight: A Textual Analysis")

# Load the data (needed for most pages)
df = load_data()

# Display selected page
if page == "Home":
    
    st.markdown("""
    ## Welcome!
    
    Explore the linguistic patterns and textual features of the medieval poem *Sir Gawain and the Green Knight*.
    
    Use the navigation menu on the left to:
    - View comprehensive textual analysis
    - Search for specific words
    - Analyze distribution patterns
    - Learn about this project
    """)
    
    # Call-to-action button
    st.markdown("## Get Started")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Explore Textual Analysis", use_container_width=True):
            nav_to('Textual Analysis')
            st.rerun()

elif page == "Textual Analysis":
    st.markdown("### Textual Visualization of Sir Gawain and the Green Knight")
    
    # Introduction
    st.markdown("""
    This section provides an interactive exploration of *Sir Gawain and the Green Knight*, 
    a 14th-century Middle English poem. Through various visualizations, we can explore word 
    patterns, frequencies, and distributions within this medieval masterpiece.
    """)
    
    if df is not None:
        # Display stats section
        word_freq = display_stats_section(df)
        
        # Display visualizations
        display_visualizations(df)
    else:
        st.error("Could not load the data. Please ensure 'word_occurrences.csv' is in the same directory as this script.")

elif page == "Word Search":
    st.markdown("### Word Search and Analysis")
    
    if df is not None:
        display_word_search(df)
    else:
        st.error("Could not load the data. Please ensure 'word_occurrences.csv' is in the same directory as this script.")

elif page == "Distribution Analysis":
    st.markdown("### Distribution Analysis")
    
    if df is not None:
        display_distribution_analysis()
    else:
        st.error("Could not load the data. Please ensure 'word_occurrences.csv' is in the same directory as this script.")

elif page == "About":
    st.markdown("### About This Project")
    display_about_section()

# Footer (shown on all pages)
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