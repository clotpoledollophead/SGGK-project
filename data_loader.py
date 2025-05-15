# src/data_loader.py
import streamlit as st
import pandas as pd
import re

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

@st.cache_data
def load_text_file(filepath='full-sggk.txt'):
    """Load the full text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().lower()
        return text
    except Exception as e:
        st.error(f"Error loading text file: {str(e)}")
        return None