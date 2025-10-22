"""
Utility functions for Chaitanya Academy Link Finder
Extracted from the original Google Apps Script
"""

import re
import unicodedata
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
import time


class TextProcessor:
    """Handle text processing operations like the original Google Apps Script"""
    
    @staticmethod
    def remove_diacritics(text: str) -> str:
        """Remove diacritical marks from Latvian text"""
        if not text:
            return ""
            
        # Specific Latvian diacritics mapping
        diacritics_map = {
            'ā': 'a', 'č': 'c', 'ē': 'e', 'ģ': 'g', 'ī': 'i', 'ķ': 'k', 
            'ļ': 'l', 'ņ': 'n', 'š': 's', 'ū': 'u', 'ž': 'z',
            'Ā': 'A', 'Č': 'C', 'Ē': 'E', 'Ģ': 'G', 'Ī': 'I', 'Ķ': 'K',
            'Ļ': 'L', 'Ņ': 'N', 'Š': 'S', 'Ū': 'U', 'Ž': 'Z',
            # Additional Sanskrit/IAST characters
            'ś': 's', 'ṣ': 's', 'ṁ': 'm', 'ḍ': 'd', 'ṭ': 't', 
            'ṇ': 'n', 'ṅ': 'n', 'ñ': 'n', 'ṛ': 'r', 'ḷ': 'l'
        }
        
        result = text
        for char, replacement in diacritics_map.items():
            result = result.replace(char, replacement)
        
        return result
    
    @staticmethod
    def is_cyrillic(text: str) -> bool:
        """Check if text contains Cyrillic characters"""
        return bool(re.search('[а-яА-ЯЁё]', text))
    
    @staticmethod
    def transliterate(word: str) -> str:
        """Transliterate Latin to Cyrillic as in original Google Apps Script"""
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
            # Check for multi-character combinations first
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
    
    @staticmethod
    def split_search_terms(search_term: str) -> List[str]:
        """Split search terms like the original function"""
        return [term.strip() for term in search_term.lower().split(';') if term.strip()]


class DateProcessor:
    """Handle date processing and sorting"""
    
    @staticmethod
    def parse_date_for_sorting(date_str: Union[str, pd.NaType]) -> Tuple[int, int, int]:
        """
        Parse date string for sorting, handling formats like YYYY.MM.DD
        Returns tuple (year, month, day) for sorting
        """
        if pd.isna(date_str) or not date_str or str(date_str).lower() == 'unknown':
            return (9999, 99, 99)  # Put unknown dates last
        
        date_str = str(date_str).strip()
        
        # Handle YYYY.MM.DD format with possible 'xx' values
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
        
        return (9999, 99, 99)  # Default for unparseable dates
    
    @staticmethod
    def compare_dates(date_a: str, date_b: str) -> int:
        """Compare two dates as in the original Google Apps Script"""
        if date_a == 'unknown' and date_b == 'unknown':
            return 0
        if date_a == 'unknown':
            return 1
        if date_b == 'unknown':
            return -1
        
        parts_a = date_a.split('.')
        parts_b = date_b.split('.')
        
        # Compare years
        if parts_a[0] != parts_b[0]:
            return int(parts_b[0]) - int(parts_a[0])
        
        # Compare months
        if parts_a[1] != 'xx' and parts_b[1] != 'xx':
            if parts_a[1] != parts_b[1]:
                return int(parts_b[1]) - int(parts_a[1])
        elif parts_a[1] == 'xx' and parts_b[1] != 'xx':
            return 1
        elif parts_a[1] != 'xx' and parts_b[1] == 'xx':
            return -1
        
        # Compare days
        if parts_a[2] != 'xx' and parts_b[2] != 'xx':
            return int(parts_b[2]) - int(parts_a[2])
        elif parts_a[2] == 'xx' and parts_b[2] != 'xx':
            return 1
        elif parts_a[2] != 'xx' and parts_b[2] == 'xx':
            return -1
        
        return 0


class LengthFormatter:
    """Handle length formatting as in the original Google Apps Script"""
    
    @staticmethod
    def format_length(length) -> str:
        """Format length field to match original display"""
        if pd.isna(length) or length == "":
            return ""
        
        # Convert to string for processing
        if isinstance(length, (int, float)):
            # Handle numeric values (fraction of day)
            if 0 <= length < 1:
                total_minutes = round(length * 24 * 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                if hours == 0:
                    return f"{minutes}min"
                else:
                    return f"{hours}h {minutes:02d}min"
            return str(length)
        
        length_str = str(length)
        
        # If it's already formatted, return as is
        if 'h' in length_str and 'min' in length_str:
            return length_str
        
        # If it's in H:MM format
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
    
    @staticmethod
    def pad_zero(num: int) -> str:
        """Pad number with zero if less than 10"""
        return f"{num:02d}" if num < 10 else str(num)


class SearchEngine:
    """Main search functionality replicating Google Apps Script logic"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.date_processor = DateProcessor()
    
    def search_data(self, search_term: str, df: pd.DataFrame) -> Tuple[pd.DataFrame, float, int]:
        """
        Main search function replicating the original searchData() from Google Apps Script
        Returns: (filtered_df, search_time, total_results)
        """
        start_time = time.time()
        
        if df.empty or not search_term.strip():
            return pd.DataFrame(), 0.0, 0
        
        # Parse search terms exactly like the original
        search_terms = self.text_processor.split_search_terms(search_term)
        source_terms = [term for term in search_terms if term.startswith('@')]
        other_terms = [term for term in search_terms if not term.startswith('@')]
        
        # Start with all rows
        mask = pd.Series([True] * len(df), index=df.index)
        
        # Apply source filtering (like the original)
        if source_terms:
            source_mask = pd.Series([False] * len(df), index=df.index)
            for source_term in source_terms:
                source_value = source_term[1:].lower()  # Remove @
                if 'Source' in df.columns:
                    source_mask |= df['Source'].astype(str).str.lower().str.contains(
                        source_value, na=False, regex=False
                    )
            mask &= source_mask
        
        # Apply other term filtering with OR logic
        if other_terms:
            for term in other_terms:
                term_mask = pd.Series([False] * len(df), index=df.index)
                
                # Handle OR terms (term1 // term2)
                or_terms = [t.strip() for t in term.split('//') if t.strip()]
                
                for or_term in or_terms:
                    or_term_mask = self._search_single_term(or_term, df)
                    term_mask |= or_term_mask
                
                mask &= term_mask
        
        # Filter the dataframe
        filtered_df = df[mask].copy()
        
        # Sort by date (newest first, handling 'unknown' dates)
        if not filtered_df.empty and 'Date' in filtered_df.columns:
            filtered_df = self._sort_by_date(filtered_df)
        
        search_time = time.time() - start_time
        total_results = len(filtered_df)
        
        return filtered_df, search_time, total_results
    
    def _search_single_term(self, term: str, df: pd.DataFrame) -> pd.Series:
        """Search for a single term across relevant columns"""
        term_mask = pd.Series([False] * len(df), index=df.index)
        
        # Normalize the search term
        normalized_term = self.text_processor.remove_diacritics(term.lower())
        transliterated_term = self.text_processor.transliterate(normalized_term)
        
        # Search columns (matching the original columnIndexes)
        search_columns = ['Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 
                         'Country', 'Lang.', 'Links', 'Dwnld.', 'Length']
        
        for col in search_columns:
            if col in df.columns:
                # Convert column to string and normalize
                col_values = df[col].astype(str).str.lower()
                normalized_col_values = col_values.apply(self.text_processor.remove_diacritics)
                
                # Search for exact matches and transliterated matches
                term_mask |= normalized_col_values.str.contains(normalized_term, na=False, regex=False)
                term_mask |= normalized_col_values.str.contains(transliterated_term, na=False, regex=False)
        
        return term_mask
    
    def _sort_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort dataframe by date using the original logic"""
        if df.empty:
            return df
        
        # Create sort keys for each date
        sort_keys = df['Date'].apply(self.date_processor.parse_date_for_sorting)
        
        # Sort by the keys (descending order - newest first)
        sorted_indices = sorted(range(len(sort_keys)), 
                              key=lambda i: sort_keys.iloc[i], 
                              reverse=True)
        
        return df.iloc[sorted_indices].reset_index(drop=True)


class HighlightEngine:
    """Handle search term highlighting in results"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def highlight_search_terms(self, text: str, search_terms: List[str]) -> str:
        """
        Highlight search terms in text with different colors
        Replicates the original highlightSearchTerms() function
        """
        if not search_terms or pd.isna(text):
            return str(text)
        
        text = str(text)
        result = text
        
        # Process each search term
        for term in search_terms:
            term = term.strip()
            if not term:
                continue
            
            # Handle source terms (@source) - green highlighting
            if term.startswith('@'):
                source_term = term[1:].lower()
                pattern = re.compile(f'({re.escape(source_term)})', re.IGNORECASE)
                result = pattern.sub(r'<span style="background-color: green; color: white; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
                continue
            
            # Handle OR terms (term1 // term2)
            or_terms = [t.strip() for t in term.split('//') if t.strip()]
            
            for or_term in or_terms:
                normalized_term = self.text_processor.remove_diacritics(or_term.lower())
                
                # Exact match highlighting (yellow)
                exact_pattern = re.compile(f'({re.escape(or_term)})', re.IGNORECASE)
                result = exact_pattern.sub(r'<span style="background-color: yellow; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
                
                # Diacritic match highlighting (light blue)
                if normalized_term != or_term.lower():
                    diacritic_pattern = re.compile(f'({re.escape(normalized_term)})', re.IGNORECASE)
                    # Only highlight if not already highlighted
                    if '<span' not in result:
                        result = diacritic_pattern.sub(r'<span style="background-color: lightblue; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
                
                # Cyrillic transliteration highlighting (orange)
                transliterated_term = self.text_processor.transliterate(normalized_term)
                if transliterated_term != normalized_term and not re.search('[a-zA-Z0-9]', transliterated_term):
                    cyrillic_pattern = re.compile(f'({re.escape(transliterated_term)})', re.IGNORECASE)
                    result = cyrillic_pattern.sub(r'<span style="background-color: orange; padding: 2px 4px; border-radius: 3px;">\1</span>', result)
        
        return result


class DataValidator:
    """Validate and clean data from Google Sheets"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean the dataframe structure"""
        if df.empty:
            return df
        
        # Ensure required columns exist
        required_columns = [
            'Date', 'Type', 'Subtype', 'Nr.', 'Original file name', 
            'Country', 'Lang.', 'Links', 'Dwnld.', 'Length', 'Source'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Fill NaN values with empty strings
        df = df.fillna("")
        
        # Format Length column
        if 'Length' in df.columns:
            formatter = LengthFormatter()
            df['Length'] = df['Length'].apply(formatter.format_length)
        
        return df
    
    @staticmethod
    def get_sources_list(df: pd.DataFrame) -> List[Dict[str, any]]:
        """Get list of unique sources with counts"""
        if df.empty or 'Source' not in df.columns:
            return []
        
        # Filter out empty sources and count
        valid_sources = df[df['Source'].astype(str).str.strip() != '']['Source']
        source_counts = valid_sources.value_counts()
        
        sources = []
        for source, count in source_counts.items():
            sources.append({
                'sourceName': str(source).strip(),
                'count': int(count)
            })
        
        return sources


# Test functions for development
def test_search_functionality():
    """Test the search functionality with sample data"""
    # Create sample data
    sample_data = {
        'Date': ['2023.12.25', '2023.11.15', 'unknown'],
        'Original file name': ['Guru Tattva', 'Krishna Prema', 'Bhakti Yoga'],
        'Source': ['ChaitanyaAcademy', 'ChaitanyaAcademyLive', 'BihariPrabhu'],
        'Type': ['Lecture', 'Seminar', 'Class'],
        'Length': ['1:30', '45:00', '2:15']
    }
    
    df = pd.DataFrame(sample_data)
    df = DataValidator.validate_dataframe(df)
    
    # Test search
    search_engine = SearchEngine()
    result_df, search_time, total_results = search_engine.search_data('guru', df)
    
    print(f"Search results: {total_results}")
    print(f"Search time: {search_time:.3f}s")
    print(result_df)


if __name__ == "__main__":
    test_search_functionality()
```
