# visualizations.py
import streamlit as st
import plotly.express as px
import pandas as pd

def display_visualizations(df):
    """Display the visualization section of the app"""
    # Get word frequencies
    word_freq = df.drop_duplicates(subset=['Word'])[['Word', 'Frequency']].sort_values('Frequency', ascending=False)
    
    # Chart selection
    st.markdown("---")
    st.subheader("📈 Visualization Options")
    st.markdown("""
    Choose different visualization types to explore various aspects of the text's word usage 
    and patterns. Each visualization reveals different insights about the poem's language.
    """)
    
    chart_type = st.selectbox(
        "Select Visualization Type",
        ["Top Words", "Frequency Distribution", "Word Frequency by Line Position", "Frequency Dot Plot"]
    )
    
    # Display selected chart
    if chart_type == "Top Words":
        display_top_words(word_freq)
    elif chart_type == "Frequency Distribution":
        display_frequency_distribution(word_freq)
    elif chart_type == "Word Frequency by Line Position":
        display_frequency_by_position(df)
    else:  # Frequency Dot Plot
        display_frequency_dot_plot(word_freq)

def display_top_words(word_freq):
    """Display the top words chart"""
    st.subheader("Top 20 Most Frequent Words")
    st.markdown("""
    This chart shows the most commonly used words in the text. In Middle English texts, 
    articles (þe = "the"), conjunctions (and), and pronouns dominate the top positions. 
    Understanding these patterns helps identify the text's linguistic style and structure.
    """)
    
    top_words = word_freq.head(20)
    
    fig = px.bar(
        top_words, 
        x='Frequency', 
        y='Word', 
        orientation='h',
        color='Frequency',
        color_continuous_scale='Greens',
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

def display_frequency_distribution(word_freq):
    """Display the frequency distribution chart"""
    st.subheader("Word Frequency Distribution")
    st.markdown("""
    This pie chart shows how words are distributed across frequency ranges. Most words appear 
    only a few times (1-5 occurrences), while very few words have high frequencies. This 
    follows Zipf's law, a common pattern in natural language where a small number of words 
    account for most usage.
    """)
    
    # Create frequency ranges
    ranges = []
    
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
        color_discrete_sequence=[
            '#f0f9e8', '#bae4bc', '#7bccc4', '#43a2ca', '#0868ac'  # Light to dark greens/blues
        ],
        height=600, # Adjust height to make it bigger,
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label+value',
        hovertemplate='<b>%{label}</b><br>Words: %{value}<br>Percentage: %{percent}<extra></extra>',
        textfont_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_frequency_by_position(df):
    """Display the frequency by line position chart"""
    st.subheader("Average Word Frequency by Line Position")
    st.markdown("""
    This line chart shows how average word frequency changes throughout the text. Variations 
    might indicate shifts in narrative style, dialogue versus description, or different 
    thematic sections. Peaks could represent formulaic passages or repetitive elements 
    common in medieval poetry.
    """)
    
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
        hovertemplate='<b>Lines %{customdata}</b><br>Avg Frequency: %{y:.1f}<extra></extra>',
        customdata=line_groups['Line Range'],
        marker=dict(color='#00a86b'),
        line=dict(color='#00a86b')
    )
    st.plotly_chart(fig, use_container_width=True)
    
def display_frequency_dot_plot(word_freq):
    """Display a dot plot of word frequencies"""
    st.subheader("Distribution of Word Frequencies (Dot Plot)")
    st.markdown("""
    This dot plot visualizes the individual frequency of each word. 
    It helps identify clusters of words with similar frequencies and 
    highlights the distribution of word occurrences more clearly, 
    especially for lower frequencies.
    """)

    fig = px.strip(
        word_freq, 
        y="Frequency", 
        orientation="v", # Vertical orientation
        title="Dot Plot of Word Frequencies",
        stripmode="overlay", # Overlay dots for better visibility of density
        color_discrete_sequence=['#00a86b'] # A nice green color
    )
    
    fig.update_layout(
        height=600,
        yaxis_title="Word Frequency",
        xaxis_title="" # No x-axis label needed for a single strip
    )

    st.plotly_chart(fig, use_container_width=True)