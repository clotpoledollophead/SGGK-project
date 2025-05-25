import pandas as pd

# Load the CSV file
df = pd.read_csv("target_word_data_classified.csv")

# Drop the 'Unnamed: 5' column
df = df.drop(columns=['Unnamed: 5'])

# Keep only rows where at least one of the two columns is 'yes'
df = df[(df['Emotion-Related'] == 'Yes') | (df['Religious'] == 'Yes')]

# Convert 'yes' to 1 and 'no' to 0
df['Emotion-Related'] = df['Emotion-Related'].map({'Yes': 1, 'No': 0})
df['Religious'] = df['Religious'].map({'Yes': 1, 'No': 0})

# Save the cleaned DataFrame if needed
df.to_csv("cleaned_words.csv", index=False)

# Print preview
print(df.head())
