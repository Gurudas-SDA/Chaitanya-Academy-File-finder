import streamlit as st
import pandas as pd
import numpy as np
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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
    st.session_state.search_results = pd.DataFrame()
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

# Utility functions
def remove_diacritics(text: str) -> str:
    """Remove diacritical marks from Latvian text"""
    if not text:
        return ""
        
    diacritics_map = {
        'ā': 'a', 'č': 'c', 'ē': 'e', 'ģ': 'g', 'ī': 'i', 'ķ': 'k', 
        'ļ': 'l', 'ņ': 'n', 'š': 's', 'ū': 'u', 'ž': 'z',
        'Ā': 'A', 'Č': 'C', 'Ē': 'E', 'Ģ': 'G', 'Ī': 'I', 'Ķ': 'K',
        'Ļ': 'L', 'Ņ': 'N', 'Š': 'S', 'Ū': 'U', 'Ž': 'Z',
        'ś': 's', 'ṣ': 's', 'ṁ': 'm', 'ḍ': 'd', 'ṭ': 't', 
        'ṇ': 'n', 'ṅ': 'n', 'ñ': 'n', 'ṛ': 'r', 'ḷ': 'l'
    }
    
    result = text
    for char, replacement in diacritics_map.items():
        result = result.replace(char, replacement)
    
    return result

def transliterate(word: str) -> str:
    """Transliterate Latin to Cyrillic"""
    transliteration_map = {
        "a": "а", "b": "б", "v": "в", "g": "г", "d": "д",
        "e": "е", "yo": "ё", "zh": "ж", "z": "з", "i": "и",
        "y": "й", "k": "к", "l": "л", "m": "м", "n": "н",
        "o": "о", "p": "п", "r": "р", "s": "с", "t": "т",
        "u": "у", "f": "ф", "h": "х", "ts": "ц", "ch": "ч",
        "sh": "ш", "sch": "щ", "yu": "ю", "ya": "я", "j": "дж"
    }
    
    result = []
    i = 0
    word_lower = word.lower()
    
    while i < len(word_lower):
        found = False
        for length in [3, 2, 1]:
            if i + length <= len(word_lower):
                substr = word_lower[i:i+length]
                if substr in transliteration_map:
                    result.append(transliteration_map[substr])
                    i += length
                    found = True
                    break
        
        if not found:
            result.append(word_lower[i])
            i += 1
    
    return ''.join(result)

def format_length(length) -> str:
    """Format length field to match original display"""
    if pd.isna(length) or length == "":
        return ""
    
    length_str = str(length)
    
    if 'h' in length_str and 'min' in length_str:
        return length_str
    
    if ':' in length_str:
        parts = length_str.split(':')
        if len(parts) >= 2:
            try:
                hours = int(parts[0])
                minutes = int(parts[1])
                if hours == 0:
                    return f"{minutes}min"
                else:
                    return f"{hours}h {minutes:02d}min"
            except ValueError:
                return length_str
    
    return length_str

def highlight_search_terms(text: str, search_terms: List[str]) -> str:
    """Highlight search terms in text with different colors"""
    if not search_terms or pd.isna(text):
        return str(text)
    
    text = str(text)
    result = text
    
    for term in search_terms:
        term = term.strip()
        if not term:
            continue
        
        if term.startswith('@'):
            source_term = term[1:].lower()
            pattern = re.compile(f'({re.escape(source_term)})', re.IGNORECASE)
            result = pattern.sub(r'<span style="background-color: green; color: white; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
            continue
        
        or_terms = [t.strip() for t in term.split('//') if t.strip()]
        
        for or_term in or_terms:
            normalized_term = remove_diacritics(or_term.lower())
            
            exact_pattern = re.compile(f'({re.escape(or_term)})', re.IGNORECASE)
            result = exact_pattern.sub(r'<span style="background-color: yellow; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
            
            if normalized_term != or_term.lower():
                diacritic_pattern = re.compile(f'({re.escape(normalized_term)})', re.IGNORECASE)
                if '<span' not in result:
                    result = diacritic_pattern.sub(r'<span style="background-color: lightblue; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
            
            transliterated_term = transliterate(normalized_term)
            if transliterated_term != normalized_term and not re.search('[a-zA-Z0-9]', transliterated_term):
                cyrillic_pattern = re.compile(f'({re.escape(transliterated_term)})', re.IGNORECASE)
                result = cyrillic_pattern.sub(r'<span style="background-color: orange; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
    
    return result

def parse_date_for_sorting(date_str) -> Tuple[int, int, int]:
    """Parse date string for sorting"""
    if pd.isna(date_str) or not date_str or str(date_str).lower() == 'unknown':
        return (9999, 99, 99)
    
    date_str = str(date_str).strip()
    
    if '.' in date_str:
        parts = date_str.split('.')
        if len(parts) == 3:
            try:
                year = int(parts[0]) if parts[0] != 'xx' else 9999
                month = int(parts[1]) if parts[1] != 'xx' else 99
                day = int(parts[2]) if parts[2] != 'xx' else 99
                return (year, month, day)
            except (ValueError, IndexError):
                pass
    
    return (9999, 99, 99)

@st.cache_data(ttl=300)
def load_spreadsheet_data() -> pd.DataFrame:
    """Load data from Google Sheets"""
    try:
        df = pd.read_csv(SPREADSHEET_URL)
        
        # Clean and standardize column names
        df.columns = df.columns.str.strip()
        
        # Ensure required columns exist
        required_columns = [
            'Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 
            'Country', 'Lang.', 'Links', 'Dwnld.', 'Length', 'Source'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        # Format length column
        if 'Length' in df.columns:
            df['Length'] = df['Length'].apply(format_length)
        
        # Fill NaN values
        df = df.fillna("")
        
        return df
        
    except Exception as e:
        st.error(f"Error loading spreadsheet data: {str(e)}")
        
        # Create sample data as fallback
        sample_data = {
            'Date': ['2023.12.25', '2023.11.15', '2023.10.01'],
            'Type': ['Lecture', 'Seminar', 'Class'],
            'Subtype': ['BG', 'SB', 'CC'],
            'Nr.': ['001', '002', '003'],
            'Original file name': ['Guru Tattva Krishna', 'Bhakti Yoga Prema', 'Spiritual Master Wisdom'],
            'Country': ['Latvia', 'India', 'USA'],
            'Lang.': ['LV', 'EN', 'EN'],
            'Links': ['https://example.com/1', 'https://example.com/2', 'https://example.com/3'],
            'Dwnld.': ['https://example.com/dl1', 'https://example.com/dl2', 'https://example.com/dl3'],
            'Length': ['1h 30min', '45min', '2h 15min'],
            'Source': ['ChaitanyaAcademy', 'ChaitanyaAcademyLive', 'BihariPrabhu']
        }
        return pd.DataFrame(sample_data)

def search_data(search_term: str, df: pd.DataFrame) -> Tuple[pd.DataFrame, float, int]:
    """Search through the dataframe based on search terms"""
    start_time = time.time()
    
    if df.empty or not search_term.strip():
        return pd.DataFrame(), 0.0, 0
    
    # Parse search terms
    search_terms = [term.strip() for term in search_term.lower().split(';') if term.strip()]
    source_terms = [term for term in search_terms if term.startswith('@')]
    other_terms = [term for term in search_terms if not term.startswith('@')]
    
    # Start with all rows
    mask = pd.Series([True] * len(df), index=df.index)
    
    # Apply source filtering
    if source_terms:
        source_mask = pd.Series([False] * len(df), index=df.index)
        for source_term in source_terms:
            source_value = source_term[1:].lower()
            if 'Source' in df.columns:
                source_mask |= df['Source'].astype(str).str.lower().str.contains(
                    source_value, na=False, regex=False
                )
        mask &= source_mask
    
    # Apply other term filtering
    if other_terms:
        for term in other_terms:
            term_mask = pd.Series([False] * len(df), index=df.index)
            
            or_terms = [t.strip() for t in term.split('//') if t.strip()]
            
            for or_term in or_terms:
                normalized_term = remove_diacritics(or_term.lower())
                transliterated_term = transliterate(normalized_term)
                
                search_columns = ['Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 
                                'Country', 'Lang.', 'Links', 'Dwnld.', 'Length']
                
                for col in search_columns:
                    if col in df.columns:
                        col_values = df[col].astype(str).str.lower()
                        normalized_col_values = col_values.apply(remove_diacritics)
                        
                        term_mask |= normalized_col_values.str.contains(normalized_term, na=False, regex=False)
                        term_mask |= normalized_col_values.str.contains(transliterated_term, na=False, regex=False)
            
            mask &= term_mask
    
    # Filter the dataframe
    filtered_df = df[mask].copy()
    
    # Sort by date
    if not filtered_df.empty and 'Date' in filtered_df.columns:
        sort_keys = filtered_df['Date'].apply(parse_date_for_sorting)
        sorted_indices = sorted(range(len(sort_keys)), 
                              key=lambda i: sort_keys.iloc[i], 
                              reverse=True)
        filtered_df = filtered_df.iloc[sorted_indices].reset_index(drop=True)
    
    search_time = time.time() - start_time
    total_results = len(filtered_df)
    
    return filtered_df, search_time, total_results

def get_sources_list(df: pd.DataFrame) -> List[Dict[str, any]]:
    """Get list of unique sources with counts"""
    if df.empty or 'Source' not in df.columns:
        return []
    
    valid_sources = df[df['Source'].astype(str).str.strip() != '']['Source']
    source_counts = valid_sources.value_counts()
    
    sources = []
    for source, count in source_counts.items():
        sources.append({
            'sourceName': str(source).strip(),
            'count': int(count)
        })
    
    return sources

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
    
    # Apply highlighting to text columns
    text_columns = ['Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 'Country', 'Lang.']
    for col in text_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: highlight_search_terms(x, search_terms)
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
                    for source in sources[:10]:
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
                filtered_df, search_time, total_results = search_data(search_input, df)
                
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
