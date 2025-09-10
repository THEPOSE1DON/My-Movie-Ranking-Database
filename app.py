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

# --- Genre Tag Filter (any match) ---
all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))
selected_genres = st.sidebar.multiselect("Select Genre(s)", all_genres)
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genres"].apply(
            lambda x: all(g in x for g in selected_genres if isinstance(x, str))
        )
    ]

# --- Genre Score Filter (multi-select) ---
genre_columns = [
    "Action Score", "Adventure Score", "Animation Score", "Biography Score",
    "Comedy Score", "Crime Score", "Documentary Score", "Drama Score", "Erotic Score",
    "Family Score", "Fantasy Score", "Feel-Good Score", "Fiction Score", "Heist Score",
    "History Score", "Horror Score", "Musical Score", "Mystery Score", "Mythology Score",
    "Romance Score", "Satire Score", "Science Fiction Score", "Sports Score",
    "Superhero Score", "Survival Score", "Thriller Score", "War Score"
]
selected_genrescore = st.sidebar.multiselect("🎭 Filter by Genre Score", genre_columns)

if selected_genrescore:
    for g in selected_genrescore:
        filtered_df = filtered_df[filtered_df[g] > 0]

# --- Year Filter ---
years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years)
if selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]

# --- Search Bar ---
search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()
suggestions = []
selected_suggestion = None
if search_term:
    suggestions = df[df["Title"].str.lower().str.contains(search_term, na=False)]["Title"].tolist()
    if suggestions:
        selected_suggestion = st.selectbox("Did you mean:", suggestions, index=0)

# Apply search filter
if search_term:
    if selected_suggestion:
        filtered_df = filtered_df[filtered_df["Title"].str.lower() == selected_suggestion.lower()]
    else:
        filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]

# --- Sorting ---
score_columns = ["Ultimate Score", "General Score", "Last Watched"] + genre_columns
sort_choice = st.sidebar.selectbox("Sort by", score_columns, index=0)
sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"], index=0)
ascending = True if sort_order == "Ascending" else False

if sort_choice == "Last Watched":
    if "Timestamp" in df.columns:
        filtered_df = filtered_df.sort_values(by="Timestamp", ascending=ascending).reset_index(drop=True)
else:
    filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending).reset_index(drop=True)

# --- Display Movies One Per Row ---
st.write("### Results")
if filtered_df.empty:
    st.warning("No movies found with the current filters/search.")
else:
    for rank, (_, row) in enumerate(filtered_df.iterrows(), start=1):
        col1, col2 = st.columns([1, 2])

        with col1:
            if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                st.image(row["Poster"], width=200)
            else:
                st.write("📌 No poster available")

        with col2:
            st.markdown(f"### #{rank}. {row['Title']} ({row['Year']})")
            st.write(f"🎭 Genres: {row['Genres']}")
            st.write(f"🌐 Language(s): {row['Language']}")
            st.write(f"⭐ Ultimate Score: {row['Ultimate Score']} | General Score: {row['General Score']}")

            # Show selected genre scores
            for g in selected_genrescore:
                st.write(f"🎯 {g}: {row[g]}")

            # Always show the score used for sorting (if it’s a genre score)
            if sort_choice in genre_columns and sort_choice not in selected_genrescore:
                st.write(f"🎯 {sort_choice}: {row[sort_choice]}")

            # Description and Comment
            if "Description" in row and pd.notna(row["Description"]):
                st.markdown(f"**📝 Description:** {row['Description']}")
            if "Comment" in row and pd.notna(row["Comment"]):
                st.markdown(f"**💭 My Comment:** {row['Comment']}")

        st.markdown("---")

