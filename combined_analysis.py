# combined_analysis.py
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

def display_combined_analysis_page():
    """
    Displays the combined analysis page, now including the word timeline
    with bars for markers and divided into four Fitts.
    """
    st.markdown("### Combined Analysis: Word Timeline & More")
    st.write("This page offers a comprehensive view, including the distribution of specific word categories throughout the text, divided by the poem's 'Fitts'.")

    # --- Word Timeline Section ---
    st.subheader("Word Occurrence Timeline (Bars & Fitts)")
    st.write("Visualizing the appearance of religious and emotion-related words across the poem's lines, represented by vertical bars and separated by the four 'Fitts' of the poem.")

    # Define file paths (assuming they are in the same directory as app.py or accessible)
    csv_file_path = 'tableConvert.com_9xq76i.csv'
    text_file_path = 'full-sggk.txt'

    # Fitt boundaries as provided from distribution_analysis.py
    fitt_boundaries = {
        'Fitt 1': (1, 532),
        'Fitt 2': (533, 1125),
        'Fitt 3': (1126, 1893),
        'Fitt 4': (1894, 2530)
    }

    try:
        csv_df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        st.error(f"Error: CSV file '{csv_file_path}' not found. Please ensure it's in the same directory.")
        return
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return

    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except FileNotFoundError:
        st.error(f"Error: Text file '{text_file_path}' not found. Please ensure it's in the same directory.")
        return
    except Exception as e:
        st.error(f"Error reading text file: {e}")
        return

    plot_data = []

    for index, row in csv_df.iterrows():
        word = str(row['Word']).lower()
        is_religious = row['Religious'] == 1
        is_emotion_related = row['Emotion-Related'] == 1

        for i, line in enumerate(text_content.splitlines()):
            if re.search(r'\b' + re.escape(word) + r'\b', line.lower()):
                if is_religious:
                    plot_data.append({'line_number': i + 1, 'category': 'Religious'})
                if is_emotion_related:
                    plot_data.append({'line_number': i + 1, 'category': 'Emotion-Related'})

    if not plot_data:
        st.warning("No relevant word occurrences found for plotting based on the provided CSV and text files.")
    else:
        plot_df = pd.DataFrame(plot_data)

        fig, ax = plt.subplots(figsize=(18, 6)) # Increased width for better Fitt visibility

        # Filter data for each category
        religious_data = plot_df[plot_df['category'] == 'Religious']
        emotion_data = plot_df[plot_df['category'] == 'Emotion-Related']

        # Y-levels for plotting
        y_level_religious = 1
        y_level_emotion = 2
        line_height = 0.8 # Height of the vertical lines (bars)

        # Plot 'Religious' words as vertical lines (bars)
        if not religious_data.empty:
            ax.vlines(x=religious_data['line_number'], ymin=y_level_religious - line_height/2, ymax=y_level_religious + line_height/2,
                       color='lightgreen', label='Religious Words', linewidth=1.5, alpha=0.7)

        # Plot 'Emotion-Related' words as vertical lines (bars)
        if not emotion_data.empty:
            ax.vlines(x=emotion_data['line_number'], ymin=y_level_emotion - line_height/2, ymax=y_level_emotion + line_height/2,
                       color='darkgreen', label='Emotion-Related Words', linewidth=1.5, alpha=0.7)

        ax.set_xlabel('Line Number')
        ax.set_title('Timeline of Religious and Emotion-Related Words in Sir Gawain and the Green Knight by Fitt')

        # Set specific y-ticks and labels
        ax.set_yticks([y_level_religious, y_level_emotion])
        ax.set_yticklabels(['Religious Words', 'Emotion-Related Words'])

        # Adjust y-axis limits to give some padding around the levels
        ax.set_ylim(0.5, 2.5)

        # Add vertical lines for Fitt boundaries
        fitt_line_styles = {'color': 'gray', 'linestyle': '--', 'linewidth': 1.0, 'alpha': 0.8}
        fitt_label_y_pos = 2.6 # Position for Fitt labels slightly above the top markers

        for fitt_name, (start_line, end_line) in fitt_boundaries.items():
            if fitt_name != 'Fitt 1': # Draw boundary lines for Fitt 2, 3, 4 starts
                ax.axvline(x=start_line - 1, **fitt_line_styles) # -1 to mark the boundary *before* the start of the fitt

            # Add Fitt labels
            mid_point = (start_line + end_line) / 2
            ax.text(mid_point, fitt_label_y_pos, fitt_name, ha='center', va='bottom', fontsize=10, color='darkgray')

        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        ax.legend(loc='upper right')

        plt.tight_layout() # Adjust layout to prevent labels from overlapping

        st.pyplot(fig)

        st.markdown("""
        **Explanation:**
        * **Light Green Bars (at Y-level 1):** Each bar represents an occurrence of a word categorized as "Religious".
        * **Dark Green Bars (at Y-level 2):** Each bar represents an occurrence of a word categorized as "Emotion-Related".
        * **Gray Dashed Vertical Lines:** Indicate the boundaries between the four "Fitts" (sections) of the poem.
        * **Fitt Labels:** Show which section of the poem you are viewing.

        This graph visually separates the word categories and provides clear divisions for the major sections of the poem, allowing for analysis of word distribution within each Fitt.
        """)
    # --- End Word Timeline Section ---
