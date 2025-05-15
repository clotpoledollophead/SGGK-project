# src/about_section.py
import streamlit as st

def display_about_section():
    """Display the about section"""
    st.markdown("---")
    st.subheader("ℹ️ About This Analysis")
    st.markdown("""
    *Sir Gawain and the Green Knight* is one of the finest works of medieval English literature, 
    written in the late 14th century by an unknown author. This alliterative poem tells the story 
    of Sir Gawain's encounter with the mysterious Green Knight and explores themes of chivalry, 
    honor, temptation, and Christian morality.

    This analysis tool allows researchers and students to explore the poem's linguistic patterns 
    through computational methods, revealing insights about its vocabulary, style, and thematic 
    distribution that might not be apparent from traditional reading alone.
    """)