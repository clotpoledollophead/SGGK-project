import pandas as pd
import re

def classify_words(input_file, output_file):
    """
    Classify words in a CSV file as religious or emotion-related based on
    the word itself and its contextual usage in the line content.
    """
    # Define classification keywords
    religious_terms = [
        'lord', 'christ', 'jesus', 'holy', 'sacred', 'divine', 'prayer', 'pray',
        'blessing', 'bless', 'church', 'chapel', 'altar', 'mass', 'service', 'priest',
        'monk', 'nun', 'saint', 'heaven', 'hell', 'soul', 'spirit', 'faith', 'believe',
        'sin', 'virtue', 'grace', 'mercy', 'forgive', 'absolution', 'confession',
        'penance', 'salvation', 'redemption', 'trinity', 'cross', 'crucifix', 'bible',
        'scripture', 'gospel', 'sermon', 'hymn', 'psalm', 'miracle', 'resurrection',
        'angel', 'devil', 'satan', 'demon', 'blessed', 'eternal', 'immortal',
        'almighty', 'omnipotent', 'worship', 'adore', 'praise', 'glory', 'hallelujah',
        'amen',
        # Middle English religious terms (excluding god variants)
        'absolucioun', 'auter', 'blessyng', 'lorde', 'cryst',
        'crist', 'haly', 'kirke', 'kyrke', 'preest', 'masse', 'chirche'
    ]
    
    emotion_terms = [
        'joy', 'happy', 'happiness', 'glad', 'cheerful', 'delight', 'pleasure',
        'bliss', 'elated', 'sad', 'sadness', 'sorrow', 'grief', 'melancholy',
        'despair', 'misery', 'woe', 'lament', 'angry', 'anger', 'rage', 'fury',
        'wrath', 'ire', 'mad', 'furious', 'livid', 'indignant', 'fear', 'afraid',
        'scared', 'terror', 'horror', 'dread', 'anxiety', 'worry', 'panic',
        'love', 'affection', 'adore', 'cherish', 'devotion', 'passion', 'romance',
        'tender', 'hate', 'hatred', 'loathe', 'despise', 'detest', 'abhor',
        'disgust', 'revulsion', 'hope', 'hopeful', 'optimism', 'confidence',
        'trust', 'shame', 'embarrassment', 'guilt', 'remorse', 'regret',
        'humiliation', 'pride', 'proud', 'arrogance', 'vanity', 'conceit',
        'hubris', 'envy', 'jealous', 'jealousy', 'covet', 'resentment',
        'bitter', 'bitterness', 'surprise', 'amazement', 'wonder', 'astonishment',
        'shock', 'startled',
        # Middle English emotional terms
        'blis', 'blys', 'blysse', 'blysful', 'blyþe', 'wraþ', 'angre', 'sorwe',
        'joye', 'glade', 'murþe', 'mirth', 'drede', 'fere', 'luf', 'lufe',
        'hatrede'
    ]
    
    def is_capitalized_god_religious(word, line_content):
        """Check if capitalized God/Gode/Goddez should be classified as religious"""
        if pd.isna(word) or pd.isna(line_content):
            return False
        
        word_str = str(word)
        content_str = str(line_content)
        
        if word_str in ["God", "Gode", "Goddez"]:
            pattern = r'\b' + re.escape(word_str) + r'\b'
            matches = list(re.finditer(pattern, content_str))
            
            for match in matches:
                start_pos = match.start()
                if start_pos == 0:
                    continue  # very beginning of text
                preceding_text = content_str[:start_pos]
                # Check if the match is preceded by sentence-ending punctuation
                if re.search(r'[.!?]\s*$', preceding_text.strip()):
                    continue  # after sentence end
                return True  # it's not sentence-initial, so it's religious
        return False

    def is_religious(word, line_content):
        if pd.isna(word) or pd.isna(line_content):
            return False
        if is_capitalized_god_religious(word, line_content):
            return True
        word_lower = str(word).lower()
        content_lower = str(line_content).lower()
        return any(term in word_lower or term in content_lower for term in religious_terms)

    def is_emotional(word, line_content):
        if pd.isna(word) or pd.isna(line_content):
            return False
        if is_capitalized_god_religious(word, line_content):
            return False
        word_lower = str(word).lower()
        content_lower = str(line_content).lower()
        return any(term in word_lower or term in content_lower for term in emotion_terms)

    try:
        print(f"Reading {input_file}...")
        df = pd.read_csv(input_file, encoding='utf-8')
        df = df.dropna(axis=1, how='all')
        print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

        print("Classifying words...")
        df['Religious'] = df.apply(lambda row: 'Yes' if is_religious(row['Word'], row['Line Content']) else 'No', axis=1)
        df['Emotion-Related'] = df.apply(lambda row: 'Yes' if is_emotional(row['Word'], row['Line Content']) else 'No', axis=1)

        total_words = len(df)
        religious_count = len(df[df['Religious'] == 'Yes'])
        emotion_count = len(df[df['Emotion-Related'] == 'Yes'])
        both_count = len(df[(df['Religious'] == 'Yes') & (df['Emotion-Related'] == 'Yes')])

        print("\nClassification Summary:")
        print(f"Total words: {total_words}")
        print(f"Religious words: {religious_count} ({religious_count/total_words*100:.1f}%)")
        print(f"Emotion-related words: {emotion_count} ({emotion_count/total_words*100:.1f}%)")
        print(f"Words that are both: {both_count} ({both_count/total_words*100:.1f}%)")

        print("\nExamples of Religious words:")
        for _, row in df[df['Religious'] == 'Yes'].head(5).iterrows():
            print(f"- {row['Word']}: \"{row['Line Content']}\"")

        print("\nExamples of Emotion-related words:")
        for _, row in df[(df['Emotion-Related'] == 'Yes') & (df['Religious'] == 'No')].head(5).iterrows():
            print(f"- {row['Word']}: \"{row['Line Content']}\"")

        print("\nExamples of words that are both:")
        for _, row in df[(df['Religious'] == 'Yes') & (df['Emotion-Related'] == 'Yes')].head(5).iterrows():
            print(f"- {row['Word']}: \"{row['Line Content']}\"")

        god_examples = df[df['Word'].isin(['God', 'Gode', 'Goddez'])]
        if len(god_examples) > 0:
            print("\nExamples of God/Gode/Goddez classifications:")
            for _, row in god_examples.head(5).iterrows():
                print(f"- {row['Word']}: \"{row['Line Content']}\" -> Religious: {row['Religious']}, Emotion: {row['Emotion-Related']}")

        print(f"\nSaving results to {output_file}...")
        df.to_csv(output_file, index=False, encoding='utf-8')
        print("Classification complete!")
        return df

    except FileNotFoundError:
        print(f"Error: Could not find file '{input_file}'")
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

# Main execution
if __name__ == "__main__":
    input_filename = "target_word_data_sel.csv"
    output_filename = "target_word_data_classified.csv"
    result_df = classify_words(input_filename, output_filename)
    if result_df is not None:
        print(f"\nFirst few rows of the classified data:")
        print(result_df[['Word', 'Line Content', 'Religious', 'Emotion-Related']].head(10))
