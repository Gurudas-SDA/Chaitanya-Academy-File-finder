import streamlit as st
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import io

# Import our utility modules
try:
    from utils import SearchEngine, HighlightEngine, DataValidator, LengthFormatter
except ImportError:
    st.error("utils.py file not found. Please check if utils.py is in the same directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Chaitanya Academy Video & Audio Link Finder",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match the original design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: darkblue;
        font-weight: bold;
        margin-bottom: 30px;
    }
    
    .search-container {
        text-align: center;
        margin: 20px 0;
    }
    
    .search-time {
        font-size: 12px;
        color: #00008B;
        margin-top: 5px;
    }
    
    .results-info {
        margin-top: 10px;
        font-size: 14px;
        color: darkred;
        font-weight: bold;
    }
    
    .empty-result-message {
        font-size: 13px;
        color: darkred;
        padding: 14px;
        text-align: center;
    }
    
    .source-highlight {
        background-color: green;
        color: white;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    .exact-match {
        background-color: yellow;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    .diacritic-match {
        background-color: lightblue;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    .cyrillic-match {
        background-color: orange;
        padding: 2px 4px;
        border-radius: 3px;
    }
    
    .stDataFrame {
        text-align: center;
    }
    
    .stButton > button {
        background-color: red;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background-color: darkred;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'total_results' not in st.session_state:
    st.session_state.total_results = 0
if 'search_time' not in st.session_state:
    st.session_state.search_time = 0

# Configuration constants
PAGE_SIZE = 10
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1O66GTEB2AfBWYEq0sDLusVkJk9gg1XpmZNJmmQkvtls/export?format=csv&gid=0"

# Initialize engines
search_engine = SearchEngine()
highlight_engine = HighlightEngine()
data_validator = DataValidator()
length_formatter = LengthFormatter()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_spreadsheet_data() -> pd.DataFrame:
    """Load data from Google Sheets"""
    try:
        df = pd.read_csv(SPREADSHEET_URL)
        
        # Validate and clean the dataframe using our utility
        df = data_validator.validate_dataframe(df)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading spreadsheet data: {str(e)}")
        return pd.DataFrame()

def get_sources_list(df: pd.DataFrame) -> List[Dict[str, any]]:
    """Get list of unique sources with counts"""
    return data_validator.get_sources_list(df)

def create_hyperlink(url: str, text: str) -> str:
    """Create HTML hyperlink"""
    if pd.isna(url) or not url:
        return text
    return f'<a href="{url}" target="_blank">{text}</a>'

def display_results_table(df: pd.DataFrame, search_terms: List[str], page: int):
    """Display paginated results table"""
    if df.empty:
        st.markdown('<div class="empty-result-message">No results found</div>', 
                   unsafe_allow_html=True)
        return
    
    # Calculate pagination
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, len(df))
    page_df = df.iloc[start_idx:end_idx].copy()
    
    # Display results info
    st.markdown(f'<div class="results-info">{len(df)} files found - Showing results {start_idx + 1}-{end_idx}</div>', 
                unsafe_allow_html=True)
    
    # Prepare display dataframe
    display_df = page_df[['Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 
                         'Country', 'Lang.', 'Links', 'Dwnld.', 'Length']].copy()
    
    # Apply highlighting to text columns using our highlight engine
    text_columns = ['Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 'Country', 'Lang.']
    for col in text_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: highlight_engine.highlight_search_terms(x, search_terms)
            )
    
    # Handle links with HTML
    if 'Links' in display_df.columns:
        display_df['Links'] = display_df['Links'].apply(
            lambda x: f'<a href="{x}" target="_blank">Link</a>' if x else ''
        )
    
    if 'Dwnld.' in display_df.columns:
        display_df['Dwnld.'] = display_df['Dwnld.'].apply(
            lambda x: f'<a href="{x}" target="_blank">Mp3</a>' if x else ''
        )
    
    # Display table
    st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header with logo
    st.markdown("""
    <div style="text-align: center;">
        <img src="https://i.imgur.com/XCLdkrh.png" alt="Chaitanya Academy logo" style="max-width: 300px; margin-bottom: 20px;">
        <h1 class="main-header">Video & Audio Link Finder</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Tools")
        
        # Test connection
        if st.button("Test Server Connection"):
            st.success(f"Connection successful: Server is responding. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load data and show sources
        if st.button("Load & Show Sources"):
            with st.spinner("Loading data..."):
                df = load_spreadsheet_data()
                if not df.empty:
                    sources = get_sources_list(df)
                    st.subheader("📊 Sources List")
                    for source in sources[:10]:  # Show top 10 sources
                        st.write(f"**@{source['sourceName']}** - {source['count']} files")
                    
                    if len(sources) > 10:
                        st.write(f"... and {len(sources) - 10} more sources")
                else:
                    st.error("Failed to load data")
        
        st.markdown("---")
        st.info("💡 **Search Tips:**\n"
                "- Use `;` to separate multiple terms\n" 
                "- Use `@source` to filter by source\n"
                "- Use `term1 // term2` for OR search\n"
                "- Supports Latvian and Cyrillic text")
    
    # Main search interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Load data for search
        df = load_spreadsheet_data()
        total_records = len(df) if not df.empty else 0
        
        # Search input
        search_placeholder = f"Search for wisdom among {total_records} links" if total_records > 0 else "Loading..."
        search_input = st.text_input("", placeholder=search_placeholder, key="search_input")
        
        # Search button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            search_clicked = st.button("🔍 Search", use_container_width=True)
        
        st.markdown('<div class="search-time">Up to 1 minute to find and upload.</div>', 
                   unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Perform search
    if search_clicked or (search_input and search_input != st.session_state.search_term):
        if search_input.strip():
            with st.spinner("Searching for best results..."):
                
                filtered_df, search_time, total_results = search_engine.search_data(search_input, df)
                
                # Update session state
                st.session_state.search_results = filtered_df
                st.session_state.search_term = search_input
                st.session_state.total_results = total_results
                st.session_state.search_time = search_time
                st.session_state.current_page = 1
        else:
            # Clear results for empty search
            st.session_state.search_results = pd.DataFrame()
            st.session_state.search_term = ""
            st.session_state.total_results = 0
            st.session_state.current_page = 1
    
    # Display results
    if not st.session_state.search_results.empty:
        search_terms = [term.strip() for term in st.session_state.search_term.split(';')]
        
        # Results table
        display_results_table(
            st.session_state.search_results, 
            search_terms, 
            st.session_state.current_page
        )
        
        # Pagination
        if st.session_state.total_results > PAGE_SIZE:
            total_pages = (st.session_state.total_results + PAGE_SIZE - 1) // PAGE_SIZE
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("◀ Previous", disabled=(st.session_state.current_page <= 1)):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col2:
                st.write(f"Page {st.session_state.current_page}")
            
            with col3:
                st.write(f"{total_pages} pages total")
            
            with col4:
                page_input = st.number_input("Go to page:", min_value=1, max_value=total_pages, 
                                           value=st.session_state.current_page, key="page_input")
                if page_input != st.session_state.current_page:
                    st.session_state.current_page = page_input
                    st.rerun()
            
            with col5:
                if st.button("Next ▶", disabled=(st.session_state.current_page >= total_pages)):
                    st.session_state.current_page += 1
                    st.rerun()
        
        # Display search time
        st.caption(f"Search completed in {st.session_state.search_time:.3f} seconds")
    
    elif st.session_state.search_term:
        st.markdown('<div class="empty-result-message">No results found</div>', 
                   unsafe_allow_html=True)
    
    else:
        # Show empty state
        st.markdown('<div class="empty-result-message">↑ Enter search terms to see results ↑</div>', 
                   unsafe_allow_html=True)

if __name__ == "__main__":
    main()
