import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import numpy as np

# Set page config
st.set_page_config(
    page_title="SGGK Text Analysis",
    page_icon="🏇🏼",
    layout="wide"
)

# Title and description
st.title("Sir Gawain and the Green Knight: A Text Analysis")
st.markdown("### Textual Visualization of Sir Gawain and the Green Knight")

# Cache the data loading function
@st.cache_data
def load_data():
    """Load and process the CSV data with forward fill"""
    try:
        # Read the CSV
        df = pd.read_csv('word_occurrences.csv')
        
        # Forward fill missing values
        df['Word'] = df['Word'].fillna(method='ffill')
        df['Frequency'] = df['Frequency'].fillna(method='ffill')
        
        # Remove any remaining null values
        df = df.dropna(subset=['Word', 'Frequency', 'Line Number'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Cache the text loading function
@st.cache_data
def load_text_file(filepath='./corpus/full-sggk.txt'):
    """Load the full text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().lower()
        return text
    except Exception as e:
        st.error(f"Error loading text file: {str(e)}")
        return None

# Functions for distribution analysis
def find_fitt_positions(text, fitt_end_markers):
    """Find the normalized positions of fitt endings in the text."""
    fitt_positions = []
    
    for marker in fitt_end_markers:
        index = text.lower().find(marker.lower())
        if index != -1:
            tokens_to_marker = len(re.findall(r"[a-zþȝ]+", text[:index]))
            total_tokens = len(re.findall(r"[a-zþȝ]+", text))
            normalized_pos = tokens_to_marker / total_tokens
            fitt_positions.append(normalized_pos)
    
    return fitt_positions

def read_csv_by_theme(plot_theme):
    """Read CSV files for different AI models based on theme"""
    pt = plot_theme.lower()
    try:
        if pt == "emotion":
            df_chatgpt = pd.read_csv('./from_full_text/chatgpt/emotion_words.csv')
            df_claude = pd.read_csv('./from_full_text/claude/sggk-emotion-words.csv')
            df_grok = pd.read_csv('./from_full_text/grok/emotion_words_sggk.csv')
        elif pt == "religious":
            df_chatgpt = pd.read_csv('./from_full_text/chatgpt/religious_words.csv')
            df_claude = pd.read_csv('./from_full_text/claude/sggk-religious-words.csv')
            df_grok = pd.read_csv('./from_full_text/grok/religious_words_sggk.csv')
        else:
            raise ValueError(f"Unknown theme {plot_theme!r}")
        
        words_chatgpt = set(df_chatgpt.iloc[:,0].str.lower())
        words_claude = set(df_claude.iloc[:,0].str.lower())
        words_grok = set(df_grok.iloc[:,0].str.lower())
        
        return words_chatgpt, words_claude, words_grok
    except Exception as e:
        st.error(f"Error loading theme data: {str(e)}")
        return set(), set(), set()

def get_positions(words_chatgpt, words_claude, words_grok, tokens, total_tokens):
    """Get normalized positions of words in the text"""
    positions_chatgpt = []
    positions_claude = []
    positions_grok = []
    
    for index, token in enumerate(tokens):
        relative_position = index / total_tokens
        
        if token in words_chatgpt:
            positions_chatgpt.append(relative_position)
        if token in words_claude:
            positions_claude.append(relative_position)
        if token in words_grok:
            positions_grok.append(relative_position)
    
    return positions_chatgpt, positions_claude, positions_grok

# Load the data
df = load_data()

if df is not None:
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Unique Words", f"{unique_words:,}")
    
    with col2:
        st.metric("Most Frequent Word", f'"{most_frequent_word["Word"]}"', f'{most_frequent_word["Frequency"]:,} occurrences')
    
    with col3:
        st.metric("Text Lines", f"{min_line} - {max_line}")
    
    with col4:
        st.metric("Total Occurrences", f"{total_occurrences:,}")
    
    # Chart selection
    st.markdown("---")
    chart_type = st.selectbox(
        "Select Visualization Type",
        ["Top Words", "Frequency Distribution", "Word Frequency by Line Position"]
    )
    
    # Display selected chart
    if chart_type == "Top Words":
        st.subheader("Top 20 Most Frequent Words")
        
        top_words = word_freq.head(20)
        
        fig = px.bar(
            top_words, 
            x='Frequency', 
            y='Word', 
            orientation='h',
            color='Frequency',
            color_continuous_scale='Blues',
            text='Frequency'
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Frequency",
            yaxis_title="Word",
            yaxis={'categoryorder':'total ascending'}
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Frequency Distribution":
        st.subheader("Word Frequency Distribution")
        
        # Create frequency ranges
        ranges = []
        labels = []
        
        for _, row in word_freq.iterrows():
            freq = row['Frequency']
            if freq <= 5:
                ranges.append('1-5')
            elif freq <= 20:
                ranges.append('6-20')
            elif freq <= 50:
                ranges.append('21-50')
            elif freq <= 100:
                ranges.append('51-100')
            else:
                ranges.append('100+')
        
        range_counts = pd.Series(ranges).value_counts()
        
        fig = px.pie(
            values=range_counts.values,
            names=range_counts.index,
            title="Distribution of Word Frequencies",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            hovertemplate='<b>%{label}</b><br>Words: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Word Frequency by Line Position
        st.subheader("Average Word Frequency by Line Position")
        
        # Group by line ranges (every 100 lines)
        df['Line Group'] = (df['Line Number'] // 100) * 100
        line_groups = df.groupby('Line Group')['Frequency'].mean().reset_index()
        line_groups['Line Range'] = line_groups['Line Group'].apply(lambda x: f"{x}-{x+99}")
        
        fig = px.line(
            line_groups,
            x='Line Group',
            y='Frequency',
            markers=True,
            title="Average Word Frequency Throughout the Text"
        )
        
        fig.update_layout(
            xaxis_title="Line Position",
            yaxis_title="Average Frequency",
            hovermode='x unified'
        )
        
        fig.update_traces(
            hovertemplate='<b>Lines %{x}-%{x}99</b><br>Avg Frequency: %{y:.1f}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Word Search Section
    st.markdown("---")
    st.subheader("Search Words in the Text")
    
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
    # Word Distribution Analysis Section
    st.markdown("---")
    st.subheader("Word Distribution Analysis")
    
    # Load the full text
    text = load_text_file()
    
    if text is not None:
        tokens = re.findall(r"[a-zþȝ]+", text)
        total_tokens = len(tokens)
        
        # Define fitt boundaries
        fitt_end_markers = [
            "Þat þou hatz tan on honde.",
            "Cowþe wel halde layk alofte.",
            "I schal telle yow how þay wroȝt.",
            "HONY SOYT QUI MAL PENCE."
        ]
        
        fitt_positions = find_fitt_positions(text, fitt_end_markers)
        
        # Theme selection
        theme = st.selectbox(
            "Select Word Category",
            ["Emotion", "Religious"]
        )
        
        # Load words for selected theme
        words_chatgpt, words_claude, words_grok = read_csv_by_theme(theme)
        
        if words_chatgpt or words_claude or words_grok:
            # Get positions
            positions_chatgpt, positions_claude, positions_grok = get_positions(
                words_chatgpt, words_claude, words_grok, tokens, total_tokens
            )
            
            # Create distribution plot
            fig = go.Figure()
            
            # Add traces for each AI model
            ai_models = [
                ("ChatGPT", positions_chatgpt, "#1EE196", 3),
                ("Claude", positions_claude, "#1ECBE1", 2),
                ("Grok", positions_grok, "#1E6AE1", 1)
            ]
            
            for model_name, positions, color, y_pos in ai_models:
                if positions:
                    # Add vertical lines for each word occurrence
                    for pos in positions:
                        fig.add_trace(go.Scatter(
                            x=[pos, pos],
                            y=[y_pos - 0.3, y_pos + 0.3],
                            mode='lines',
                            line=dict(color=color, width=0.7),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                    
                    # Add legend entry
                    fig.add_trace(go.Scatter(
                        x=[None],
                        y=[None],
                        mode='markers',
                        marker=dict(size=8, color=color),
                        name=model_name
                    ))
            
            # Add fitt boundaries
            if fitt_positions:
                for i, pos in enumerate(fitt_positions):
                    fig.add_vline(
                        x=pos,
                        line_dash="dash",
                        line_color="gray",
                        opacity=0.7,
                        annotation_text=f"Fitt {i+1} end" if i < len(fitt_positions) else None,
                        annotation_position="top"
                    )
            
            # Update layout
            fig.update_layout(
                title=f"{theme}-Word Occurrences Across Sir Gawain and the Green Knight",
                xaxis_title="Position in text (0 = start, 1 = end)",
                yaxis_title="",
                yaxis=dict(
                    tickmode='array',
                    tickvals=[1, 2, 3],
                    ticktext=['Grok', 'Claude', 'ChatGPT'],
                    range=[0.5, 3.5]
                ),
                xaxis=dict(range=[0, 1]),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics about the distribution
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("ChatGPT Words", len(positions_chatgpt))
            with col2:
                st.metric("Claude Words", len(positions_claude))
            with col3:
                st.metric("Grok Words", len(positions_grok))
            
            # Additional analysis
            st.markdown("#### Word Overlap Analysis")
            
            # Calculate overlaps
            overlap_all = words_chatgpt & words_claude & words_grok
            overlap_chatgpt_claude = words_chatgpt & words_claude
            overlap_chatgpt_grok = words_chatgpt & words_grok
            overlap_claude_grok = words_claude & words_grok
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Words identified by all three models:** {len(overlap_all)}")
                st.write(f"**ChatGPT & Claude overlap:** {len(overlap_chatgpt_claude)}")
            
            with col2:
                st.write(f"**ChatGPT & Grok overlap:** {len(overlap_chatgpt_grok)}")
                st.write(f"**Claude & Grok overlap:** {len(overlap_claude_grok)}")
        else:
            st.warning(f"No word data available for {theme} theme. Please check that the required CSV files exist.")
    else:
        st.warning("Could not load the text file. Distribution analysis is unavailable.")

else:
    st.error("Could not load the data. Please ensure 'word_occurrences.csv' is in the same directory as this script.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.875rem;'>
    Middle English Text Word Frequency Analysis | Created with Streamlit and Plotly
    </div>
    """,
    unsafe_allow_html=True
)