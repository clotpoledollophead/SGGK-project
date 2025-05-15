# src/word_search.py
import streamlit as st

def display_word_search(df):
    """Display the word search section"""
    st.markdown("---")
    st.subheader("🔍 Search Words in the Text")
    st.markdown("""
    Search for specific Middle English words to see where they appear in the text. Note that 
    Middle English spelling can be variable - try different spellings if you don't find what 
    you're looking for. The special characters þ (thorn) and ȝ (yogh) are preserved from the 
    original text.
    """)
    
    search_term = st.text_input("Search for a Middle English word...", "")
    
    if search_term:
        filtered_df = df[df['Word'].str.contains(search_term, case=False, na=False)]
        
        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} occurrences of words containing '{search_term}':")
            
            # Show first 100 results
            display_df = filtered_df.head(100)[['Word', 'Frequency', 'Line Number', 'Line Content']]
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Word": st.column_config.TextColumn("Word", width=100),
                    "Frequency": st.column_config.NumberColumn("Frequency", width=100),
                    "Line Number": st.column_config.NumberColumn("Line Number", width=100),
                    "Line Content": st.column_config.TextColumn("Line Content", width=500)
                }
            )
            
            if len(filtered_df) > 100:
                st.info(f"Showing first 100 of {len(filtered_df)} occurrences")
        else:
            st.warning(f"No words found containing '{search_term}'")