import streamlit as st
import pandas as pd

# --- Load Google Sheet ---
csv_url = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/export?format=csv&gid=1030199938"
df = pd.read_csv(csv_url, quotechar='"', engine='python')

# --- Clean column names ---
df.columns = df.columns.str.strip()
df.rename(columns={"Movie/TV Show Name": "Title"}, inplace=True)

# --- App Title ---
st.title("🎬 My Movie Rankings Database")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# --- Language Filter ---
# Split languages into individual items
all_languages = (
    df["Language"].dropna()
    .apply(lambda x: [lang.strip() for lang in str(x).split(",")])
    .sum()
)
unique_languages = sorted(set(all_languages))

# Map languages to emoji flags
language_flags = {
    "English": "🇬🇧", "French": "🇫🇷", "Spanish": "🇪🇸", "German": "🇩🇪",
    "Italian": "🇮🇹", "Portuguese": "🇵🇹", "Dutch": "🇳🇱", "Swedish": "🇸🇪",
    "Norwegian": "🇳🇴", "Danish": "🇩🇰", "Finnish": "🇫🇮", "Polish": "🇵🇱",
    "Czech": "🇨🇿", "Hungarian": "🇭🇺", "Greek": "🇬🇷", "Russian": "🇷🇺",
    "Turkish": "🇹🇷", "Ukrainian": "🇺🇦", "Arabic": "🇸🇦", "Hebrew": "🇮🇱",
    "Persian": "🇮🇷", "Amharic": "🇪🇹", "Swahili": "🇰🇪", "Afrikaans": "🇿🇦",
    "Hindi": "🇮🇳", "Urdu": "🇵🇰", "Bengali": "🇧🇩", "Tamil": "🇮🇳",
    "Telugu": "🇮🇳", "Malayalam": "🇮🇳", "Kannada": "🇮🇳", "Punjabi": "🇮🇳",
    "Gujarati": "🇮🇳", "Marathi": "🇮🇳", "Nepali": "🇳🇵", "Sinhala": "🇱🇰",
    "Thai": "🇹🇭", "Vietnamese": "🇻🇳", "Khmer": "🇰🇭", "Lao": "🇱🇦",
    "Burmese": "🇲🇲", "Japanese": "🇯🇵", "Korean": "🇰🇷", "Chinese": "🇨🇳",
    "Mandarin": "🇨🇳", "Cantonese": "🇭🇰", "Malay": "🇲🇾", "Indonesian": "🇮🇩",
    "Filipino": "🇵🇭", "Tagalog": "🇵🇭", "Quechua": "🇵🇪", "Guarani": "🇵🇾",
    "Haitian Creole": "🇭🇹", "Other": "🏳️"
}

def render_languages(language_str):
    if pd.isna(language_str):
        return ""
    langs = [lang.strip() for lang in language_str.split(",")]
    return ", ".join([f"{language_flags.get(lang,'🏳️')} {lang}" for lang in langs])

selected_language = st.sidebar.selectbox(
    "🌍 Select Language",
    [f"{language_flags.get(lang,'🏳️')} {lang}" for lang in unique_languages]
)
selected_language_plain = selected_language.split(" ", 1)[1]  # Extract plain language

# --- Genre Filter ---
all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))
selected_genres = st.sidebar.multiselect("Select Genre(s)", all_genres)

# List of all genre score columns
genre_columns = [
    "Action Score", "Adventure Score", "Animation Score", "Biography Score",
    "Comedy Score", "Crime Score", "Documentary Score", "Drama Score", "Erotic Score",
    "Family Score", "Fantasy Score", "Feel-Good Score", "Fiction Score", "Heist Score",
    "History Score", "Horror Score", "Musical Score", "Mystery Score", "Mythology Score",
    "Romance Score", "Satire Score", "Science Fiction Score", "Sports Score",
    "Superhero Score", "Survival Score", "Thriller Score", "War Score"
]
selected_genre = st.sidebar.selectbox("🎭 Filter by Genre", genre_columns)

# --- Year Filter ---
years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years)

# --- Search Bar ---
search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()
suggestions = []
selected_suggestion = None
if search_term:
    suggestions = df[df["Title"].str.lower().str.contains(search_term, na=False)]["Title"].tolist()
    if suggestions:
        selected_suggestion = st.selectbox("Did you mean:", suggestions, index=0)

# --- Apply Filters ---
filtered_df = df.copy()

# Search filter
if search_term:
    if selected_suggestion:
        filtered_df = filtered_df[filtered_df["Title"].str.lower() == selected_suggestion.lower()]
    else:
        filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]

# Genre filter (show only movies with selected genre score > 0)
if selected_genre:
    filtered_df = filtered_df[filtered_df[selected_genre] > 0]

# Language filter
if selected_language_plain:
    filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language_plain, na=False)]

# Genre selection filter (if multiple genres selected)
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genres"].apply(lambda x: any(g in x for g in selected_genres if isinstance(x, str)))
    ]

# Year filter
if selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

# --- Sorting ---
score_columns = ["Ultimate Score", "General Score"] + genre_columns
sort_choice = st.sidebar.selectbox("Sort by", score_columns)
sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])
ascending = True if sort_order == "Ascending" else False
filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

# --- Display Movies One Per Row ---
st.write("### Results")
if filtered_df.empty:
    st.warning("No movies found with the current filters/search.")
else:
    for _, row in filtered_df.iterrows():
        col1, col2 = st.columns([1, 2])

        with col1:
            if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                st.image(row["Poster"], width=200)
            else:
                st.write("📌 No poster available")

        with col2:
            st.markdown(f"### {row['Title']} ({row['Year']})")
            st.write(f"🎭 Genres: {row['Genres']}")
            st.write(f"🌐 Language(s): {render_languages(row['Language'])}")
            st.write(f"⭐ Ultimate Score: {row['Ultimate Score']} | General Score: {row['General Score']}")
            st.write(f"🎯 {selected_genre}: {row[selected_genre]}")  # show the chosen genre score
            if "Description" in row and pd.notna(row["Description"]):
                st.markdown(f"**📝 Description:** {row['Description']}")
            if "Comment" in row and pd.notna(row["Comment"]):
                st.markdown(f"**💭 My Comment:** {row['Comment']}")

        st.markdown("---")

