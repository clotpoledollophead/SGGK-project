# word_search.py
import streamlit as st
import re

def display_word_search(df_main, df_target):
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
    
    # New: Select which dataset to search
    search_data_source = st.radio(
        "Select search scope:",
        ("All words (from main text)", "Specific target words"),
        index=0, # Default to "All words"
        key="search_scope_radio" # Unique key for this radio button
    )

    if search_data_source == "All words (from main text)":
        df_to_search = df_main
        data_source_name = "main text"
    else:
        df_to_search = df_target
        data_source_name = "specific target words"
        if df_target.empty:
            st.warning("Specific target word data not loaded. Please ensure 'target_word_data.csv' is available and correctly formatted.")
            return # Exit if target data isn't available

    # Initialize session state for pagination (ensure uniqueness for each search type)
    session_key_prefix = "search_all_" if search_data_source == "All words (from main text)" else "search_target_"

    if session_key_prefix + 'page' not in st.session_state:
        st.session_state[session_key_prefix + 'page'] = 1
    if session_key_prefix + 'last_search' not in st.session_state:
        st.session_state[session_key_prefix + 'last_search'] = ""
    if session_key_prefix + 'page_size' not in st.session_state:
        st.session_state[session_key_prefix + 'page_size'] = 50 # Default page size

    search_term = st.text_input(f"Search for a Middle English word in {data_source_name}...", "", key=f"{session_key_prefix}search_input")
    
    # Reset page if search term changed or source changed
    if search_term != st.session_state[session_key_prefix + 'last_search']:
        st.session_state[session_key_prefix + 'page'] = 1
        st.session_state[session_key_prefix + 'last_search'] = search_term
    
    if search_term:
        # Check if the search term is enclosed in quotes for exact match
        if search_term.startswith('"') and search_term.endswith('"') and len(search_term) >= 1:
            # Extract the exact word to search (remove quotes)
            exact_word = search_term[1:-1]
            # Search for exact match (case-insensitive)
            filtered_df = df_to_search[df_to_search['Word'].str.lower() == exact_word.lower()]
            search_type = f"exact match '{exact_word}'"
        else:
            # Search for partial matches (contains)
            filtered_df = df_to_search[df_to_search['Word'].str.contains(search_term, case=False, na=False)]
            search_type = f"words containing '{search_term}'"
        
        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} occurrences of {search_type} in {data_source_name}:")
            
            st.markdown("##### Occurrences in text:")
            
            # Pagination settings
            page_size = st.session_state[f'{session_key_prefix}page_size']
            total_rows = len(filtered_df)
            total_pages = (total_rows + page_size - 1) // page_size
            
            # Create columns for pagination controls
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮ First", disabled=st.session_state[session_key_prefix + 'page'] == 1, key=f"{session_key_prefix}first_btn"):
                    st.session_state[session_key_prefix + 'page'] = 1
            
            with col2:
                if st.button("◀ Previous", disabled=st.session_state[session_key_prefix + 'page'] == 1, key=f"{session_key_prefix}prev_btn"):
                    st.session_state[session_key_prefix + 'page'] -= 1
            
            with col3:
                st.session_state[session_key_prefix + 'page'] = st.selectbox(
                    "Page",
                    range(1, total_pages + 1),
                    index=st.session_state[session_key_prefix + 'page'] - 1,
                    format_func=lambda x: f"Page {x} of {total_pages}",
                    key=f"{session_key_prefix}page_selector"
                )
            
            with col4:
                if st.button("Next ▶", disabled=st.session_state[session_key_prefix + 'page'] == total_pages, key=f"{session_key_prefix}next_btn"):
                    st.session_state[session_key_prefix + 'page'] += 1
            
            with col5:
                if st.button("Last ⏭", disabled=st.session_state[session_key_prefix + 'page'] == total_pages, key=f"{session_key_prefix}last_btn"):
                    st.session_state[session_key_prefix + 'page'] = total_pages
            
            # Calculate start and end indices for current page
            start_idx = (st.session_state[session_key_prefix + 'page'] - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            
            # Show current page results
            # Ensure 'Meaning Category' is available if searching target words, otherwise don't include it.
            columns_to_display = ['Word', 'Frequency', 'Line Number', 'Line Content']
            if search_data_source == "Specific target words" and 'Meaning Category' in filtered_df.columns:
                columns_to_display.append('Meaning Category')

            display_df = filtered_df.iloc[start_idx:end_idx][columns_to_display]
            
            column_configs = {
                "Word": st.column_config.TextColumn("Word", width=100),
                "Frequency": st.column_config.NumberColumn("Frequency", width=100),
                "Line Number": st.column_config.NumberColumn("Line Number", width=100),
                "Line Content": st.column_config.TextColumn("Line Content", width=500)
            }
            if 'Meaning Category' in columns_to_display:
                column_configs["Meaning Category"] = st.column_config.TextColumn("Meaning Category", width=150)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config=column_configs
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
                    index=[25, 50, 100, 200].index(page_size), # Set index to current page_size
                    key=f"{session_key_prefix}page_size_selector"
                )
                if new_page_size != page_size:
                    st.session_state[f'{session_key_prefix}page_size'] = new_page_size
                    st.session_state[session_key_prefix + 'page'] = 1 # Reset page on size change
                    st.rerun() # Rerun to apply new page size immediately
        else:
            st.warning(f"No {search_type} found in {data_source_name}")