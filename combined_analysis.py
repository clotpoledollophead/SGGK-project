# src/combined_analysis.py
import streamlit as st
import plotly.graph_objects as go
import re
import pandas as pd # Import pandas for DataFrame operations

# Import necessary functions from other modules
from data_loader import load_data, load_text_file, load_target_word_data
from visualizations import get_frequency_by_position_figure
from distribution_analysis import (
    find_fitt_positions,
    read_csv_by_theme,
    get_positions
)

# Helper function to get distribution traces for overlay
# This function is new or significantly modified to fit the overlay logic
def get_distribution_overlay_traces(positions, color, name, y_base_level, line_height_ratio=0.05):
    """
    Generates Plotly traces for word distribution to be overlaid on a frequency plot.
    The y-values are relative to a base level, allowing them to appear above the main line.
    """
    traces = []
    if positions:
        # Add vertical lines for each word occurrence
        for pos in positions:
            traces.append(go.Scatter(
                x=[pos, pos],
                y=[y_base_level, y_base_level + (y_base_level * line_height_ratio)], # Lines extending upwards from base
                mode='lines',
                line=dict(color=color, width=1.0),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add a single marker for legend entry
        traces.append(go.Scatter(
            x=[None], # No actual x-data for legend entry
            y=[None], # No actual y-data for legend entry
            mode='markers',
            marker=dict(size=10, color=color, symbol='line-ns'), # Use a line symbol for legend
            name=name,
            showlegend=True
        ))
    return traces

def display_combined_analysis_page():
    """
    Displays the combined analysis page with three distinct graphs:
    1. Combined distribution of selected words graphed on top of Average Word Frequency by Line Position.
    2. Emotion words graphed on top of Average Word Frequency by Line Position.
    3. Religious words graphed on top of Average Word Frequency by Line Position.
    """
    st.markdown("### Combined Word Distribution and Frequency Analysis")
    st.markdown("""
    This page presents a unique perspective by overlaying specific word distributions
    (from AI models and target words) onto the average word frequency across the poem's lines.
    This allows for direct visual correlation between thematic density and linguistic patterns.
    """)

    # Load all necessary data
    df_main = load_data() # Main word occurrences dataframe
    df_target = load_target_word_data() # Specific target words dataframe
    full_text = load_text_file() # Full text for tokenization and fitt positions

    if df_main is None or full_text is None:
        st.error("Could not load essential data (word occurrences or full text). Please ensure 'word_occurrences.csv' and 'full-sggk.txt' are available.")
        return

    # Prepare common data for distribution plots
    tokens = re.findall(r"[a-zþȝ]+", full_text.lower())
    total_tokens = len(tokens)
    
    fitt_end_markers = [
        "Þat þou hatz tan on honde.",
        "Cowþe wel halde layk alofte.",
        "I schal telle yow how þay wroȝt.",
        "HONY SOYT QUI MAL PENCE."
    ]
    fitt_positions = find_fitt_positions(full_text, fitt_end_markers)

    # Calculate max average frequency for dynamic y-scaling of distribution markers
    # Ensure df_main has 'Line Group' and 'Frequency' columns for this calculation
    if 'Line Number' in df_main.columns and 'Frequency' in df_main.columns:
        df_main['Line Group'] = (df_main['Line Number'] // 100) * 100
        max_avg_freq = df_main.groupby('Line Group')['Frequency'].mean().max()
    else:
        # Fallback if columns are missing or data is not suitable for this calculation
        max_avg_freq = 50 # Default to a reasonable value if calculation fails
        st.warning("Could not calculate max average frequency from df_main. Using a default value for plot scaling.")


    # --- Graph 1: Combined Distribution of Specific Target Words ---
    st.markdown("---")
    st.subheader("1. Specific Target Words vs. Average Word Frequency")
    st.markdown("""
    This plot shows the distribution of words from your `target_word_data.csv`
    overlaid on the average word frequency across the text. This helps in
    understanding if specific thematic words cluster in areas of higher or lower
    linguistic density.
    """)
    if not df_target.empty:
        # Get base frequency figure
        fig1 = get_frequency_by_position_figure(df_main)
        
        # Get target word distribution traces
        # Place them slightly above the max average frequency for visibility
        target_word_positions = []
        target_words_set = set(df_target['Word'].unique())
        for index, token in enumerate(tokens):
            if token in target_words_set:
                target_word_positions.append(index / total_tokens)

        # Generate traces for target words, starting from a y-level above max_avg_freq
        # Use a distinct color like 'red' for target words
        target_traces_overlay = get_distribution_overlay_traces(
            target_word_positions, "red", "Target Words", max_avg_freq * 1.1, line_height_ratio=0.1
        )
        
        # Add target word traces to the frequency figure
        for trace in target_traces_overlay:
            fig1.add_trace(trace)

        # Add fitt boundaries to the combined plot
        if fitt_positions:
            for i, pos in enumerate(fitt_positions):
                fig1.add_vline(
                    x=pos,
                    line_dash="dash",
                    line_color="gray",
                    opacity=0.7,
                    annotation_text=f"Fitt {i+1} end" if i < len(fitt_positions) else None,
                    annotation_position="top"
                )

        # Adjust y-axis range and ticks for clarity
        fig1.update_layout(
            title="Specific Target Words Distribution Overlaid on Average Word Frequency",
            height=500,
            showlegend=True,
            yaxis=dict(
                range=[0, max_avg_freq * 1.25], # Extend range to show distribution lines
                title="Frequency / Word Presence"
            )
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("Specific target word data not loaded. This combined plot is unavailable.")

    # --- Graph 2: Emotion Words Combined ---
    st.markdown("---")
    st.subheader("2. Emotion Words Distribution vs. Average Word Frequency")
    st.markdown("""
    This plot shows how emotion-related words, as identified by different AI models,
    are distributed across the text, overlaid on the average word frequency.
    Observe if emotional peaks align with changes in linguistic density.
    """)
    words_chatgpt_e, words_claude_e, words_grok_e = read_csv_by_theme("Emotion")
    if words_chatgpt_e or words_claude_e or words_grok_e:
        positions_chatgpt_e, positions_claude_e, positions_grok_e = get_positions(
            words_chatgpt_e, words_claude_e, words_grok_e, tokens, total_tokens
        )
        
        fig2 = get_frequency_by_position_figure(df_main)
        
        # Generate traces for AI model emotion words
        # Stack them slightly above max_avg_freq
        base_y_dist = max_avg_freq * 1.15 # Base level for AI distributions
        
        ai_models_emotion = [
            ("ChatGPT Emotion", positions_chatgpt_e, "#1EE196", base_y_dist + max_avg_freq * 0.08),
            ("Claude Emotion", positions_claude_e, "#1ECBE1", base_y_dist + max_avg_freq * 0.04),
            ("Grok Emotion", positions_grok_e, "#1E6AE1", base_y_dist)
        ]

        for name, positions, color, y_level in ai_models_emotion:
            traces = get_distribution_overlay_traces(positions, color, name, y_level, line_height_ratio=0.05)
            for trace in traces:
                fig2.add_trace(trace)
        
        # Add fitt boundaries
        if fitt_positions:
            for i, pos in enumerate(fitt_positions):
                fig2.add_vline(
                    x=pos,
                    line_dash="dash",
                    line_color="gray",
                    opacity=0.7,
                    annotation_text=f"Fitt {i+1} end" if i < len(fitt_positions) else None,
                    annotation_position="top"
                )

        # Adjust y-axis range and ticks for clarity
        fig2.update_layout(
            title="Emotion Words Distribution Overlaid on Average Word Frequency",
            height=500,
            showlegend=True,
            yaxis=dict(
                range=[0, max_avg_freq * 1.3], # Extend range to show distribution lines
                title="Frequency / Word Presence"
            )
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No emotion word data available for combined analysis.")

    # --- Graph 3: Religious Words Combined ---
    st.markdown("---")
    st.subheader("3. Religious Words Distribution vs. Average Word Frequency")
    st.markdown("""
    This plot illustrates the distribution of religious words, as identified by AI models,
    overlaid on the average word frequency. This can highlight sections of the poem
    where religious themes are more prominent and how they correlate with changes in
    linguistic patterns.
    """)
    words_chatgpt_r, words_claude_r, words_grok_r = read_csv_by_theme("Religious")
    if words_chatgpt_r or words_claude_r or words_grok_r:
        positions_chatgpt_r, positions_claude_r, positions_grok_r = get_positions(
            words_chatgpt_r, words_claude_r, words_grok_r, tokens, total_tokens
        )
        
        fig3 = get_frequency_by_position_figure(df_main)
        
        # Generate traces for AI model religious words
        # Stack them slightly above max_avg_freq
        base_y_dist = max_avg_freq * 1.15 # Base level for AI distributions
        
        ai_models_religious = [
            ("ChatGPT Religious", positions_chatgpt_r, "#1EE196", base_y_dist + max_avg_freq * 0.08),
            ("Claude Religious", positions_claude_r, "#1ECBE1", base_y_dist + max_avg_freq * 0.04),
            ("Grok Religious", positions_grok_r, "#1E6AE1", base_y_dist)
        ]

        for name, positions, color, y_level in ai_models_religious:
            traces = get_distribution_overlay_traces(positions, color, name, y_level, line_height_ratio=0.05)
            for trace in traces:
                fig3.add_trace(trace)
        
        # Add fitt boundaries
        if fitt_positions:
            for i, pos in enumerate(fitt_positions):
                fig3.add_vline(
                    x=pos,
                    line_dash="dash",
                    line_color="gray",
                    opacity=0.7,
                    annotation_text=f"Fitt {i+1} end" if i < len(fitt_positions) else None,
                    annotation_position="top"
                )

        # Adjust y-axis range and ticks for clarity
        fig3.update_layout(
            title="Religious Words Distribution Overlaid on Average Word Frequency",
            height=500,
            showlegend=True,
            yaxis=dict(
                range=[0, max_avg_freq * 1.3], # Extend range to show distribution lines
                title="Frequency / Word Presence"
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No religious word data available for combined analysis.")

