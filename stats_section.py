# src/stats_section.py
import streamlit as st

def display_stats_section(df):
    """Display the statistics section of the app"""
    # Calculate statistics
    unique_words = df['Word'].nunique()
    total_occurrences = len(df)
    max_line = df['Line Number'].max()
    min_line = df['Line Number'].min()
    
    # Get word frequencies (unique words with their frequencies)
    word_freq = df.drop_duplicates(subset=['Word'])[['Word', 'Frequency']].sort_values('Frequency', ascending=False)
    most_frequent_word = word_freq.iloc[0]
    
    # Info section
    st.info(f"""
    This visualization analyzes a Middle English text containing **{unique_words:,} unique words** 
    with **{total_occurrences:,} total occurrences** across **{max_line:,} lines**. 
    Notable Middle English words include *þe* (the), *þat* (that), and *hym* (him).
    """)
    
    # Statistics cards
    st.subheader("📊 Key Statistics")
    st.markdown("""
    These metrics provide an overview of the text's linguistic properties. The high frequency 
    of certain words (particularly articles and pronouns) is typical of Middle English texts.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Unique Words", f"{unique_words:,}")
    
    with col2:
        st.metric("Most Frequent Word", f'"{most_frequent_word["Word"]}"', f'{most_frequent_word["Frequency"]:,} occurrences')
    
    with col3:
        st.metric("Text Lines", f"{min_line} - {max_line}")
    
    with col4:
        st.metric("Total Occurrences", f"{total_occurrences:,}")
    
    return word_freq