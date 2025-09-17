import streamlit as st
import pandas as pd
import re

# --- Page Config (keep wide for title centering) ---
st.set_page_config(layout="wide")

# --- Load Google Sheet ---
csv_url = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/export?format=csv&gid=1030199938"
df = pd.read_csv(csv_url, quotechar='"', engine='python')

# --- Clean column names ---
df.columns = df.columns.str.strip()
df.rename(columns={"Movie/TV Show Name": "Title"}, inplace=True)

# --- App Title (keep large + wide) ---
st.markdown("<h1 style='text-align: center; font-size: 42px;'>🎬 Noel's Movie Rankings</h1>", unsafe_allow_html=True)

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
selected_language = st.sidebar.selectbox("🌍 Filter by Language", language_options)

# --- Genre Tag Filter ---
all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))
selected_genres = st.sidebar.multiselect("🎭 Filter by Genre(s)", all_genres)

# --- Year Filter (supports ranges like 2005-2020) ---
def parse_year_range(year_str):
    """Return (start, end) years from a string, e.g. '2005-2020' -> (2005, 2020)."""
    if pd.isna(year_str):
        return None, None
    match = re.match(r"^\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*$", str(year_str))
    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        return start, end
    return None, None

# Collect only start years for dropdown
all_years = []
for y in df["Year"].dropna():
    start, _ = parse_year_range(y)
    if start is not None:
        all_years.append(start)

unique_years = sorted(set(all_years))
selected_years = st.sidebar.multiselect("📅 Filter by Year(s)", unique_years)

# --- Search Bar ---
search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()

# --- Apply Filters ---
filtered_df = df.copy()

# Search filter (show ALL partial matches)
if search_term:
    filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]

# Genre tag filter (must include ALL chosen tags)
if selected_genres:
    filtered_df = filtered_df[
        filtered_df["Genres"].apply(
            lambda x: all(g in x for g in selected_genres if isinstance(x, str))
        )
    ]

# Language filter
if selected_language != "Select Language":
    filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language, na=False)]

# Year filter (works with ranges)
if selected_years:
    def year_in_range(row_year, selected):
        start, end = parse_year_range(row_year)
        if start is None:
            return False
        return any(sel >= start and sel <= end for sel in selected)

    filtered_df = filtered_df[filtered_df["Year"].apply(lambda y: year_in_range(y, selected_years))]

# --- Sorting ---
genre_columns = [
    "Action Score", "Adventure Score", "Animation Score", "Biography Score",
    "Comedy Score", "Crime Score", "Documentary Score", "Drama Score", "Erotic Score",
    "Family Score", "Fantasy Score", "Feel-Good Score", "Fiction Score", "Heist Score",
    "History Score", "Horror Score", "Musical Score", "Mystery Score", "Mythology Score",
    "Romance Score", "Satire Score", "Science Fiction Score", "Sports Score",
    "Superhero Score", "Survival Score", "Thriller Score", "War Score"
]

sort_options = {
    "Ultimate Score": "Ultimate Score",
    "General Score": "General Score",
    "Last Watched": "Timestamp"
}
for g in genre_columns:
    sort_options[g] = g

# Default sort: Ultimate Score
default_sort_display = "Ultimate Score"
sort_choice_display = st.sidebar.selectbox("📌 Sort by", list(sort_options.keys()), index=list(sort_options.keys()).index(default_sort_display))
sort_choice = sort_options[sort_choice_display]

sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])
ascending = True if sort_order == "Ascending" else False

# Handle Last Watched properly
if sort_choice == "Timestamp":
    filtered_df["Timestamp"] = pd.to_datetime(filtered_df["Timestamp"], errors="coerce")

filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

# --- Display Movies One Per Row (back to original width) ---
st.write(f"### Results ({sort_choice_display})")
if filtered_df.empty:
    st.warning("No movies found with the current filters/search.")
else:
    for i, (_, row) in enumerate(filtered_df.iterrows(), start=1):
        col1, col2 = st.columns([1, 2])  # reverted to original width

        with col1:
            if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                st.image(row["Poster"], width=200)
            else:
                st.write("📌 No poster available")

        with col2:
            st.markdown(f"### #{i}. {row['Title']} ({row['Year']})")
            st.write(f"🎭 Genres: {row['Genres']}")
            st.write(f"🌐 Language(s): {row['Language']}")
            st.write(f"⭐ Ultimate Score: {row['Ultimate Score']} | General Score: {row['General Score']}")

            if selected_genres:
                for genre in selected_genres:
                    score_col = f"{genre} Score"
                    if score_col in row and pd.notna(row[score_col]):
                        st.write(f"🎯 {genre} Score: {row[score_col]}")

            if sort_choice in genre_columns and sort_choice in row and pd.notna(row[sort_choice]):
                st.write(f"📊 Sorted by {sort_choice_display}: {row[sort_choice]}")

            if "Description" in row and pd.notna(row["Description"]):
                st.markdown(f"**📝 Description:** {row['Description']}")
            if "Comment" in row and pd.notna(row["Comment"]):
                st.markdown(f"**💭 My Comment:** {row['Comment']}")

        st.markdown("---")
