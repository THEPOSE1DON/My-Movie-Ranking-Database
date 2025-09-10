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

# Start with full dataframe
filtered_df = df.copy()

# --- Language Filter ---
all_languages = (
    df["Language"].dropna()
    .apply(lambda x: [lang.strip() for lang in str(x).split(",")])
    .sum()
)
unique_languages = sorted(set(all_languages))
language_options = ["Select Language"] + unique_languages
selected_language = st.sidebar.selectbox("🌍 Select Language", language_options)

if selected_language != "Select Language":
    filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language, na=False)]

# --- Genre Filter ---
all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))
selected_genres = st.sidebar.multiselect("Select Genre(s)", all_genres)

genre_columns = [
    "Action Score", "Adventure Score", "Animation Score", "Biography Score",
    "Comedy Score", "Crime Score", "Documentary Score", "Drama Score", "Erotic Score",
    "Family Score", "Fantasy Score", "Feel-Good Score", "Fiction Score", "Heist Score",
    "History Score", "Horror Score", "Musical Score", "Mystery Score", "Mythology Score",
    "Romance Score", "Satire Score", "Science Fiction Score", "Sports Score",
    "Superhero Score", "Survival Score", "Thriller Score", "War Score"
]
selected_genre = st.sidebar.selectbox("🎭 Filter by Genre", ["Select Genre"] + genre_columns)

# --- Year Filter ---
years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years)

# --- Search Bar ---
search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()

# --- Apply Filters ---
filtered_df = df.copy()

# Search filter (show ALL partial matches)
if search_term:
    filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]

# Genre filter (multi-select: must include ALL chosen genres)
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genres"].apply(
            lambda x: all(g in x for g in selected_genres if isinstance(x, str))
        )
    ]

# Single-genre score filter (only if real genre selected)
if selected_genre != "Select Genre":
    filtered_df = filtered_df[filtered_df[selected_genre] > 0]

# Language filter
if selected_language != "Select Language":
    filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language, na=False)]

# Year filter
if selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

# --- Sorting ---
score_columns = ["Ultimate Score", "General Score", "Timestamp"] + genre_columns
sort_choice = st.sidebar.selectbox("Sort by", score_columns)
sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])
ascending = True if sort_order == "Ascending" else False
filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

# --- Display Movies One Per Row ---
st.write("### Results")
if filtered_df.empty:
    st.warning("No movies found with the current filters/search.")
else:
    for i, (_, row) in enumerate(filtered_df.iterrows(), start=1):
        col1, col2 = st.columns([1, 2])

        with col1:
            if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                st.image(row["Poster"], width=200)
            else:
                st.write("📌 No poster available")

        with col2:
            st.markdown(f"### #{i}. - {row['Title']} ({row['Year']})")
            st.write(f"🎭 Genres: {row['Genres']}")
            st.write(f"🌐 Language(s): {row['Language']}")
            st.write(f"⭐ Ultimate Score: {row['Ultimate Score']} | General Score: {row['General Score']}")

            # Show genre-specific score if relevant
            if selected_genre != "Select Genre":
                st.write(f"🎯 {selected_genre}: {row[selected_genre]}")

            if "Description" in row and pd.notna(row["Description"]):
                st.markdown(f"**📝 Description:** {row['Description']}")
            if "Comment" in row and pd.notna(row["Comment"]):
                st.markdown(f"**💭 My Comment:** {row['Comment']}")

        st.markdown("---")
