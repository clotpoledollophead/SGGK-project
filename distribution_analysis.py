# src/distribution_analysis.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import re
from data_loader import load_text_file

def display_distribution_analysis():
    """Display the word distribution analysis section"""
    st.markdown("---")
    st.subheader("📍 Word Distribution Analysis")
    st.markdown("""
    This section compares how different AI models (ChatGPT, Claude, and Grok) identify 
    emotion-related and religious words throughout the text. The visualization shows where 
    these thematic words appear in the poem's structure, with vertical dashed lines marking 
    the boundaries between the four main sections (fitts) of the poem.
    """)
    
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
        
        # Explain themes
        if theme == "Emotion":
            st.markdown("""
            **Emotion words** include terms related to feelings, psychological states, and 
            emotional expressions. The distribution of these words can reveal the poem's 
            emotional arc and intensity at different narrative moments.
            """)
        else:
            st.markdown("""
            **Religious words** include terms related to Christian faith, spirituality, and 
            medieval religious practices. Their distribution shows how religious themes are 
            woven throughout this medieval narrative.
            """)
        
        # Load words for selected theme
        words_chatgpt, words_claude, words_grok = read_csv_by_theme(theme)
        
        if words_chatgpt or words_claude or words_grok:
            # Get positions
            positions_chatgpt, positions_claude, positions_grok = get_positions(
                words_chatgpt, words_claude, words_grok, tokens, total_tokens
            )
            
            # Create and display the plot
            create_distribution_plot(positions_chatgpt, positions_claude, positions_grok, 
                                   fitt_positions, theme)
            
            # Display statistics
            display_distribution_stats(positions_chatgpt, positions_claude, positions_grok)
            
            # Display overlap analysis
            display_overlap_analysis(words_chatgpt, words_claude, words_grok)
        else:
            st.warning(f"No word data available for {theme} theme. Please check that the required CSV files exist.")
    else:
        st.warning("Could not load the text file. Distribution analysis is unavailable.")

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

def create_distribution_plot(positions_chatgpt, positions_claude, positions_grok, 
                           fitt_positions, theme):
    """Create and display the distribution plot"""
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

def display_distribution_stats(positions_chatgpt, positions_claude, positions_grok):
    """Display statistics about the distribution"""
    st.markdown("#### 📊 Model Comparison")
    st.markdown("""
    These metrics show how many thematic words each AI model identified. Differences 
    might reflect varying approaches to understanding medieval language or different 
    interpretations of what constitutes emotional or religious content.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ChatGPT Words", len(positions_chatgpt))
    with col2:
        st.metric("Claude Words", len(positions_claude))
    with col3:
        st.metric("Grok Words", len(positions_grok))

def display_overlap_analysis(words_chatgpt, words_claude, words_grok):
    """Display the overlap analysis"""
    st.markdown("#### 🔄 Word Overlap Analysis")
    st.markdown("""
    This analysis shows which words were identified by multiple AI models, revealing 
    consensus about key thematic terms. Higher overlap suggests stronger agreement 
    about which words carry emotional or religious significance.
    """)
    
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