import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

# Google Sheets configuration
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1O66GTEB2AfBWYEq0sDLusVkJk9gg1XpmZNJmmQkvtls/export?format=csv&gid=0"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_google_sheets():
    """
    Ielādē datus tieši no Google Sheets
    """
    try:
        df = pd.read_csv(GOOGLE_SHEETS_URL)
        return df
    except Exception as e:
        st.error(f"Kļūda ielādējot datus: {str(e)}")
        return None

def create_clickable_link(url, text="🔗 Atvērt"):
    """Izveido klikšķināmu linku"""
    if url and isinstance(url, str) and url.startswith('http'):
        return f'<a href="{url}" target="_blank">{text}</a>'
    return "Nav pieejams"

def process_links(df):
    """
    Apstrādā linkus no Google Sheets datiem
    """
    # YouTube links from Direct URL column
    if 'Direct URL' in df.columns:
        df['YouTube_Link'] = df['Direct URL'].apply(
            lambda x: create_clickable_link(x, "▶️ YouTube") if pd.notna(x) else "❌ Nav"
        )
    
    # Look for MP3 links in any column that might contain them
    mp3_link_created = False
    
    # Check various possible column names for MP3 links
    possible_mp3_columns = ['MP3 Link', 'Audio Link', 'Google Drive', 'Mp3', 'Audio']
    
    for col_name in possible_mp3_columns:
        if col_name in df.columns:
            df['MP3_Link'] = df[col_name].apply(
                lambda x: create_clickable_link(x, "🎵 MP3") if pd.notna(x) and str(x).startswith('http') else "❌ Nav"
            )
            mp3_link_created = True
            break
    
    # If no MP3 links found, create empty column
    if not mp3_link_created:
        df['MP3_Link'] = "❌ Nav"
    
    return df

def main():
    st.set_page_config(
        page_title="CA Datu Bāze",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 Chaitanya Academy Datu Bāze")
    st.subheader("📁 Audio failu katalogs")
    
    # Load data
    with st.spinner('Ielādē datus no Google Sheets...'):
        df = load_data_from_google_sheets()
    
    if df is None:
        st.error("❌ Neizdevās ielādēt datus no Google Sheets")
        st.stop()
    
    st.success(f"✅ Dati ielādēti! Kopā ieraksti: {len(df)}")
    
    # Process links
    df = process_links(df)
    
    # Show data info
    col1, col2, col3 = st.columns(3)
    with col1:
        youtube_count = df['Direct URL'].notna().sum() if 'Direct URL' in df.columns else 0
        st.metric("YouTube linki", youtube_count)
    
    with col2:
        total_records = len(df)
        st.metric("Kopā ieraksti", total_records)
    
    with col3:
        latest_date = df['Date'].max() if 'Date' in df.columns else "Nav"
        st.metric("Jaunākais ieraksts", latest_date)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtri")
    
    # Source filter
    if 'Source' in df.columns:
        sources = ['Visi'] + sorted(df['Source'].dropna().unique().tolist())
        selected_source = st.sidebar.selectbox("Avots:", sources)
        
        if selected_source != 'Visi':
            df = df[df['Source'] == selected_source]
    
    # Subject filter
    if 'Subject' in df.columns:
        subjects = ['Visi'] + sorted(df['Subject'].dropna().unique().tolist())
        selected_subject = st.sidebar.selectbox("Temats:", subjects)
        
        if selected_subject != 'Visi':
            df = df[df['Subject'] == selected_subject]
    
    # Date filter
    if 'Date' in df.columns:
        st.sidebar.subheader("📅 Datuma filtrs")
        date_filter = st.sidebar.radio("Periods:", ["Visi", "Pēdējie 30 dienas", "Pēdējie 7 dienas"])
        
        if date_filter != "Visi":
            try:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                today = pd.Timestamp.now()
                
                if date_filter == "Pēdējie 30 dienas":
                    cutoff_date = today - pd.Timedelta(days=30)
                elif date_filter == "Pēdējie 7 dienas":
                    cutoff_date = today - pd.Timedelta(days=7)
                
                df = df[df['Date'] >= cutoff_date]
            except:
                pass
    
    # Search
    search_term = st.sidebar.text_input("🔍 Meklēt:")
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df = df[mask]
    
    # Refresh button
    if st.sidebar.button("🔄 Atjaunot datus"):
        st.cache_data.clear()
        st.rerun()
    
    st.write(f"**Rāda {len(df)} ierakstus**")
    
    # Display data
    if len(df) > 0:
        # Select important columns for display
        display_cols = []
        for col in ['Original file name', 'Subject', 'Date', 'Source', 'Length', 'YouTube_Link', 'MP3_Link']:
            if col in df.columns:
                display_cols.append(col)
        
        # Rename columns for display
        display_df = df[display_cols].copy()
        
        # Rename columns to Latvian
        column_names = {
            'Original file name': 'Nosaukums',
            'Subject': 'Temats', 
            'Date': 'Datums',
            'Source': 'Avots',
            'Length': 'Garums',
            'YouTube_Link': 'YouTube',
            'MP3_Link': 'MP3'
        }
        
        display_df = display_df.rename(columns=column_names)
        
        # Display with clickable links
        st.markdown(
            display_df.to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )
        
        # Download options
        st.subheader("📥 Lejupielāde")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv = df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="💾 Lejupielādēt CSV",
                data=csv,
                file_name=f"CA_database_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='CA_Data')
            
            st.download_button(
                label="📊 Lejupielādēt Excel",
                data=output.getvalue(),
                file_name=f"CA_database_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    else:
        st.warning("⚠️ Nav atrasti ieraksti pēc jūsu filtriem")
    
    # Footer info
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Pēdējā atjaunināšana: {datetime.now().strftime('%H:%M:%S')}")
    st.sidebar.caption("Dati tiek ielādēti tieši no Google Sheets")

if __name__ == "__main__":
    main()
