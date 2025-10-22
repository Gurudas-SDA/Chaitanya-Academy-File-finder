# Chaitanya Academy Video & Audio Link Finder

Streamlit aplikācija, kas reproducē Google Apps Script funkcionalitāti audio un video failu meklēšanai.

## Funkcionalitāte

### 🔍 Galvenās iezīmes
- **Meklēšana**: Meklē caur ~3000+ audio/video ierakstiem
- **Daudzvalodu atbalsts**: Latviešu valoda ar diakritiskajām zīmēm un kirilica
- **Avotu filtrēšana**: Meklēšana pēc konkrētiem avotiem (@source)
- **Paginācija**: 10 rezultāti uz lapas
- **Reāllaika dati**: Tieša pieslēgšana Google Sheets

### 🎯 Meklēšanas sintakse
- `;` - atdala vairākus meklēšanas terminus
- `@avots` - filtrē pēc konkrēta avota
- `termins1 // termins2` - VAI (OR) meklēšana
- Automatiska transliterācija (latīņu ↔ kirilica)
- Diakritisko zīmju normalizēšana

### 📊 Atbalstītie avoti
- ChaitanyaAcademyLive
- ChaitanyaAcademy  
- BihariPrabhu
- soundcloud.com/ca108
- Un citi...

## Instalācija un palaišana

### 1. Priekšnosacījumi
```bash
python 3.8+
pip
```

### 2. Instalēšana
```bash
# Klonējiet vai lejupielādējiet failus
git clone <repository> # vai lejupielādējiet zip

# Instalējiet atkarības
pip install -r requirements.txt
```

### 3. Palaišana
```bash
streamlit run streamlit_app.py
```

Aplikācija būs pieejama: `http://localhost:8501`

## Failu struktūra

```
.
├── streamlit_app.py      # Galvenā aplikācija
├── requirements.txt      # Python bibliotēkas
├── .streamlit/
│   └── config.toml      # Streamlit konfigurācija
└── README.md            # Šis fails
```

## Konfigurācija

### Google Sheets integrācija
Aplikācija izmanto publisko CSV eksportu no Google Sheets:
- Sheet ID: `1O66GTEB2AfBWYEq0sDLusVkJk9gg1XpmZNJmmQkvtls`
- Kolumnas: Date, Type, Subtype, Nr., Original file name, Country, Lang., Links, Dwnld., Length, Source

### Datu kešošana
- Dati tiek kešoti 5 minūtes (`@st.cache_data(ttl=300)`)
- Automātiski atjaunojas katru 5. minūti

## Izmantošana

### Pamata meklēšana
```
guru  # Meklē "guru" visos laukos
```

### Avota filtrēšana
```
@chaitanyaacademylive  # Tikai ChaitanyaAcademyLive avots
```

### Kombinēta meklēšana
```
guru; @chaitanyaacademy  # "Guru" no ChaitanyaAcademy avota
```

### VAI meklēšana
```
guru // tattva  # "Guru" VAI "tattva"
```

### Kompleksa meklēšana
```
guru; tattva // philosophy; @chaitanyaacademy
# "Guru" UN ("tattva" VAI "philosophy") no ChaitanyaAcademy
```

## Oriģinālā Google Apps Script funkcionalitāte

Šī aplikācija reproducē šādas funkcijas:
- `searchData()` - galvenā meklēšanas funkcija
- `getSourcesList()` - avotu saraksts
- `testConnection()` - savienojuma pārbaude
- `highlightSearchTerms()` - terminu izcēlšana
- `transliterate()` - kirilicas transliterācija
- `removeDiacritics()` - diakritisko zīmju noņemšana

## Tehniskie detaļi

### Meklēšanas algoritms
1. Parsē meklēšanas terminus (`;` sadalītājs)
2. Izdala avotu terminus (`@prefix`)
3. Veic normalizāciju (diakritiskās zīmes, reģistrs)
4. Veic transliterāciju (latīņu ↔ kirilica)
5. Filtrē datus pēc visiem kritērijiem
6. Kārto pēc datuma (jaunākie vispirms)

### Kolonnu kartēšana
| Google Sheets | Streamlit |
|---------------|-----------|
| Date | Date |
| Type | Type |
| Subtype | Subtype |  
| Nr. | Nr. |
| Original file name | Original file name |
| Country | Country |
| Lang. | Lang. |
| Links | Links (klikšķināmas) |
| Dwnld. | Dwnld. (klikšķināmas) |
| Length | Length (formatēts) |
| Source | Source |

## Problēmu risināšana

### Dati neielādējas
1. Pārbaudiet interneta savienojumu
2. Pārbaudiet vai Google Sheets ir publisks
3. Notīriet cache: F5 vai restartējiet aplikāciju

### Meklēšana neatgriež rezultātus
1. Pārbaudiet meklēšanas sintaksi
2. Izmēģiniet vienkāršākus terminus
3. Pārbaudiet vai avots eksistē (@avots)

### Lēna veiktspēja
1. Dati tiek ielādēti pirmo reizi (5-10 sekundes)
2. Pēc tam tiek izmantots cache
3. Kompleksa meklēšana var aizņemt ilgāku laiku

## Atšķirības no oriģināla

### Ierobežojumi
- Nav YouTube/SoundCloud API integrācijas (tikai meklēšana)
- Nav failu sinhronizācijas ar Google Drive
- Nav atskaišu ģenerēšanas
- Nav administrātora funkciju

### Uzlabojumi
- Responsīvs dizains
- Labāka paginācija
- Real-time meklēšana
- Kešošana ātrākai veiktspējā

## Turpmākā attīstība

Iespējamie uzlabojumi:
- [ ] YouTube API integrācija
- [ ] SoundCloud API integrācija  
- [ ] Google Drive integrācija
- [ ] Atskaišu eksports
- [ ] Lietotāju autentifikācija
- [ ] Administrātora panelis

## Licences un autortiesības

Šī aplikācija reproducē oriģinālo Google Apps Script funkcionalitāti Chaitanya Academy vajadzībām.
