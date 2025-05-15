# src/about_section.py
import streamlit as st

def display_about_section():
    """Display the about section"""
    st.markdown("---")
    st.subheader("ℹ️ About This Project")
    st.markdown("""
                *Sir Gawain and the Green Knight*, written in the mid to late 1300s, survives in what is now known as the 
                *Cotton MS Nero A.x* manuscript, tells the story of Sir Gawain's encounter with the mysterious Green Knight 
                and explores themes of chivalry, honor, temptation, and Christian morality.

                The unique blend of traditions from the widespread Christianity to local traditions provides modern 
                readers insight into what would have been medieval Britain. After centuries, the work remains popular, 
                especially in modern adaptations both on paper and screen, demonstrating its enduring appeal.

                This project, building upon the foundations set by previous research, 
                aims to provide researchers and students an alternative way to explore the poem's textual patterns 
                through computational methods, revealing insights about its vocabulary, style, and thematic 
                distribution that offers alternative perspectives to this iconic poem.
    """)