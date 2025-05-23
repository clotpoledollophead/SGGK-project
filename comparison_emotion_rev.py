import pandas as pd

# Get a list of the uploaded files
file_names = ['chatgpt_emo.csv', 'chatgpt_relig.csv',
              'claude_emo.csv', 'claude_relig.csv',
              'grok_emo.csv', 'grok_relig.csv']

# Create a mapping from file names to descriptive names for output
file_display_names = {
    'chatgpt_emo.csv': 'ChatGPT Emotion-Related Words',
    'chatgpt_relig.csv': 'ChatGPT Religiosity-Related Words',
    'claude_emo.csv': 'Claude AI Emotion-Related Words',
    'claude_relig.csv': 'Claude AI Religiosity-Related Words',
    'grok_emo.csv': 'Grok Emotion-Related Words',
    'grok_relig.csv': 'Grok Religiosity-Related Words'
}

# Dictionary to store words and the files they appear in (excluding target_file_name itself)
word_to_files = {}

# --- Step 1: Process target_word_data_sel.csv and store its words from 'Word' column ---
target_words = set()
target_file_name = 'target_word_data_sel.csv'
word_column_name = 'Word' # The column to compare

try:
    df_target = pd.read_csv(target_file_name, sep=None, engine='python', on_bad_lines='skip')
    if word_column_name in df_target.columns:
        for item in df_target[word_column_name].dropna():
            # Convert to string and lower for case-insensitive comparison
            word = str(item).lower()
            target_words.add(word)
    else:
        print(f"Error: '{word_column_name}' column not found in {target_file_name}")
        exit() # Exit if the target file does not have the required column
except Exception as e:
    print(f"Error reading file {target_file_name}: {e}")
    exit() # Exit if the target file cannot be read, as comparison is not possible

# --- Step 2: Compare 'Word' column of other files against target_words ---
for file_name in file_names:
    # We explicitly skip the target file as it's already processed and we don't want
    # it in the comparison list for the output column.
    if file_name == target_file_name:
        continue

    try:
        df_other = pd.read_csv(file_name, sep=None, engine='python', on_bad_lines='skip')
        if word_column_name in df_other.columns:
            for item in df_other[word_column_name].dropna():
                # Convert to string and lower for case-insensitive comparison
                word = str(item).lower()
                # Only add files for words that are present in target_words
                if word in target_words:
                    if word not in word_to_files:
                        word_to_files[word] = []
                    # Use the original filename for internal tracking, but display name for output
                    if file_name not in word_to_files[word]:
                        word_to_files[word].append(file_name)
        else:
            print(f"Warning: '{word_column_name}' column not found in {file_name}. Skipping this file for comparison.")
    except Exception as e:
        print(f"Error reading file {file_name}: {e}")

# Prepare data for DataFrame
data = []
# Only include words that are in the target_words set in the final output
for word in sorted(list(target_words)): # Sort for consistent output
    files = word_to_files.get(word, [])
    # Use file_display_names to show descriptive names in the output DataFrame
    display_file_names = [file_display_names.get(f, f) for f in files]
    data.append([word, ", ".join(display_file_names)])

# Create DataFrame
df_output = pd.DataFrame(data, columns=['Word', 'Files Appearing In'])

# Save DataFrame to CSV
df_output.to_csv('word_file_comparison.csv', index=False)

print("Comparison data saved to 'word_file_comparison.csv'")