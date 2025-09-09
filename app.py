import streamlit as st
import pandas as pd

# --- Load Google Sheet ---
sheet_url = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/edit?usp=sharing"
csv_url = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/export?format=csv&gid=1030199938"
df = pd.read_csv(csv_url)
st.write("Columns in the sheet:", df.columns.tolist())

# --- Rename for convenience ---
df.rename(columns={
    "Movie/TV Show Name": "Title"
}, inplace=True)

# --- App Title ---
st.title("🎬 My Movie Rankings Database")

# --- Search Bar ---
search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()

# Autocomplete-like dropdown (based on current input)
suggestions = []
selected_suggestion = None
if search_term:
    suggestions = df[df["Title"].str.lower().str.contains(search_term, na=False)]["Title"].tolist()
    if suggestions:
        selected_suggestion = st.selectbox("Did you mean:", suggestions, index=0)

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Genre filter
all_genres = sorted(
    set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist)
)
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
filtered_df = df[df[selected_genre] > 0]
filtered_df = filtered_df.sort_values(by=selected_genre, ascending=False)
for _, row in filtered_df.iterrows():
    st.image(row["Poster"], width=200)
    st.subheader(row["Movie/TV Show Name"])
    st.write(f"Year: {row['Year']} | Language: {row['Language']}")
    st.write(f"⭐ Ultimate Score: {row['Ultimate Score']}")
    st.write(f"⭐ General Score: {row['General Score']}")
    st.write(f"🎭 {selected_genre}: {row[selected_genre]}")  # show the chosen genre score
    if "Description" in df.columns:
        st.write(row["Description"])

# Language filter
# Split languages into individual items
all_languages = (
    df["Language"]
    .dropna()
    .apply(lambda x: [lang.strip() for lang in str(x).split(",")])
    .sum()
)

# Get unique sorted list
unique_languages = sorted(set(all_languages))

# Sidebar filter
selected_language = st.sidebar.selectbox("🌍 Select Language", unique_languages)
if selected_language:
    filtered_df = df[df["Language"].str.contains(selected_language, na=False)]

# Year filter
years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years)

# Sorting options
score_columns = ["Ultimate Score", "General Score"] + [
    col for col in df.columns if col.endswith("Score") and col not in ["Ultimate Score", "General Score"]
]
sort_choice = st.sidebar.selectbox("Sort by", score_columns)
sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])

# --- Apply Filters ---
filtered_df = df.copy()

# Search filter (live typing OR chosen suggestion)
if search_term:
    if selected_suggestion:
        filtered_df = filtered_df[filtered_df["Title"].str.lower() == selected_suggestion.lower()]
    else:
        filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]

# Genre filter
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genres"].apply(
            lambda x: any(g in x for g in selected_genres if isinstance(x, str))
        )
    ]

# Language filter
if selected_languages:
    filtered_df = filtered_df[filtered_df["Language"].isin(selected_languages)]
language_flags = {
    # Europe
    "English": "🇬🇧",
    "French": "🇫🇷",
    "Spanish": "🇪🇸",
    "German": "🇩🇪",
    "Italian": "🇮🇹",
    "Portuguese": "🇵🇹",
    "Dutch": "🇳🇱",
    "Swedish": "🇸🇪",
    "Norwegian": "🇳🇴",
    "Danish": "🇩🇰",
    "Finnish": "🇫🇮",
    "Polish": "🇵🇱",
    "Czech": "🇨🇿",
    "Hungarian": "🇭🇺",
    "Greek": "🇬🇷",
    "Russian": "🇷🇺",
    "Turkish": "🇹🇷",
    "Ukrainian": "🇺🇦",

    # Middle East / Africa
    "Arabic": "🇸🇦",
    "Hebrew": "🇮🇱",
    "Persian": "🇮🇷",
    "Amharic": "🇪🇹",
    "Swahili": "🇰🇪",
    "Afrikaans": "🇿🇦",

    # Asia
    "Hindi": "🇮🇳",
    "Urdu": "🇵🇰",
    "Bengali": "🇧🇩",
    "Tamil": "🇮🇳",
    "Telugu": "🇮🇳",
    "Malayalam": "🇮🇳",
    "Kannada": "🇮🇳",
    "Punjabi": "🇮🇳",
    "Gujarati": "🇮🇳",
    "Marathi": "🇮🇳",
    "Nepali": "🇳🇵",
    "Sinhala": "🇱🇰",
    "Thai": "🇹🇭",
    "Vietnamese": "🇻🇳",
    "Khmer": "🇰🇭",
    "Lao": "🇱🇦",
    "Burmese": "🇲🇲",
    "Japanese": "🇯🇵",
    "Korean": "🇰🇷",
    "Chinese": "🇨🇳",
    "Mandarin": "🇨🇳",
    "Cantonese": "🇭🇰",
    "Malay": "🇲🇾",
    "Indonesian": "🇮🇩",
    "Filipino": "🇵🇭",
    "Tagalog": "🇵🇭",

    # Americas
    "Quechua": "🇵🇪",
    "Guarani": "🇵🇾",
    "Haitian Creole": "🇭🇹",

    # Default
    "Other": "🏳️"
}
def render_languages(language_str):
    if pd.isna(language_str):
        return ""
    langs = [lang.strip() for lang in language_str.split(",")]
    return ", ".join([f"{language_flags.get(lang, '🏳️')} {lang}" for lang in langs])

# Example usage inside your display loop
st.write(f"Language(s): {render_languages(row['Language'])}")
# Year filter
if selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

# --- Apply Sorting ---
ascending = True if sort_order == "Ascending" else False
filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

# --- Display Movies in a Grid ---
# --- Display Movies One Per Row ---
st.write("### Results")

if filtered_df.empty:
    st.warning("No movies found with the current filters/search.")
else:
    for idx, row in filtered_df.iterrows():
        # Create a row with 2 columns: poster (1/3) + info (2/3)
        col1, col2 = st.columns([1, 2])

        with col1:
            if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                st.image(row["Poster"], width='stretch')
            else:
                st.write("📌 No poster available")

        with col2:
            st.markdown(f"### {row['Title']} ({row['Year']})")
            st.write(f"🎭 Genres: {row['Genres']}")
            st.write(f"🌐 Language: {row['Language']}")
            st.write(f"⭐ Ultimate Score: {row['Ultimate Score']} | General Score: {row['General Score']}")
            
            # Description (new column in your Google Sheet)
            if "Description" in row and pd.notna(row["Description"]):
                st.markdown(f"**📝 Description:** {row['Description']}")
            
            # Personal Comment (new column in your Google Sheet)
            if "Comment" in row and pd.notna(row["Comment"]):
                st.markdown(f"**💭 My Comment:** {row['Comment']}")

        st.markdown("---")  # Divider between movies


