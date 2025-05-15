# word_search.py
import streamlit as st
import re

def display_word_search(df):
    """Display the word search section"""
    st.markdown("---")
    st.subheader("🔍 Search Words in the Text")
    st.markdown("""
    Search for specific Middle English words to see where they appear in the text. 
    - Use quotes ("") for exact word matches only
    - Without quotes, search finds all words containing your search term
    
    Note that Middle English spelling can be variable - try different spellings if you don't find what 
    you're looking for. The special characters þ (thorn) and ȝ (yogh) are preserved from the 
    original text.
    """)
    
    # Initialize session state for pagination
    if 'search_page' not in st.session_state:
        st.session_state.search_page = 1
    if 'last_search' not in st.session_state:
        st.session_state.last_search = ""
    
    search_term = st.text_input("Search for a Middle English word...", "")
    
    # Reset page if search term changed
    if search_term != st.session_state.last_search:
        st.session_state.search_page = 1
        st.session_state.last_search = search_term
    
    if search_term:
        # Check if the search term is enclosed in quotes for exact match
        if search_term.startswith('"') and search_term.endswith('"') and len(search_term) >= 1:
            # Extract the exact word to search (remove quotes)
            exact_word = search_term[1:-1]
            # Search for exact match (case-insensitive)
            filtered_df = df[df['Word'].str.lower() == exact_word.lower()]
            search_type = f"exact match '{exact_word}'"
        else:
            # Search for partial matches (contains)
            filtered_df = df[df['Word'].str.contains(search_term, case=False, na=False)]
            search_type = f"words containing '{search_term}'"
        
        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} occurrences of {search_type}:")
            
            # Group by unique words and show count
            word_counts = filtered_df['Word'].value_counts()
            
            st.markdown("##### Occurrences in text:")
            
            # Pagination settings
            page_size = 50
            total_rows = len(filtered_df)
            total_pages = (total_rows + page_size - 1) // page_size
            
            # Create columns for pagination controls
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮ First", disabled=st.session_state.search_page == 1):
                    st.session_state.search_page = 1
            
            with col2:
                if st.button("◀ Previous", disabled=st.session_state.search_page == 1):
                    st.session_state.search_page -= 1
            
            with col3:
                st.session_state.search_page = st.selectbox(
                    "Page",
                    range(1, total_pages + 1),
                    index=st.session_state.search_page - 1,
                    format_func=lambda x: f"Page {x} of {total_pages}",
                    key="page_selector"
                )
            
            with col4:
                if st.button("Next ▶", disabled=st.session_state.search_page == total_pages):
                    st.session_state.search_page += 1
            
            with col5:
                if st.button("Last ⏭", disabled=st.session_state.search_page == total_pages):
                    st.session_state.search_page = total_pages
            
            # Calculate start and end indices for current page
            start_idx = (st.session_state.search_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            
            # Show current page results
            display_df = filtered_df.iloc[start_idx:end_idx][['Word', 'Frequency', 'Line Number', 'Line Content']]
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
            
            # Show page info and results per page selector
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"Showing occurrences {start_idx + 1} to {end_idx} of {total_rows}")
            with col2:
                # Allow users to change page size
                new_page_size = st.selectbox(
                    "Results per page:",
                    [25, 50, 100, 200],
                    index=1,
                    key="page_size_selector"
                )
                if new_page_size != page_size:
                    st.session_state.search_page = 1
                    st.rerun()
        else:
            st.warning(f"No {search_type} found")