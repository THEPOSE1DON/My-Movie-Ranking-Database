import streamlit as st
import pandas as pd
import re

# --- Page Config (wide mode) ---
st.set_page_config(layout="wide")

# --- Load Google Sheet ---
csv_url = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/export?format=csv&gid=1030199938"
df = pd.read_csv(csv_url, quotechar='"', engine='python')

# --- Clean column names ---
df.columns = df.columns.str.strip()
df.rename(columns={"Movie/TV Show Name": "Title"}, inplace=True)

# --- Compute Ultimate Ranking ---
df["Ultimate Ranking"] = df["Ultimate Score"].rank(method="min", ascending=False).astype(int)

# --- Custom Title ---
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0.3rem;'>🎬 Noel's Movie Rankings Database</h1>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# --- Initialize Page State ---
if "page" not in st.session_state:
    st.session_state.page = "Results"

# --- CSS for buttons and hover effects ---
st.markdown(f"""
    <style>
    /* All buttons: large, wide, smooth hover */
    .stButton>button {{
        height: 3.2em !important;
        width: 85% !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        background-color: #f0f0f0;
        color: black;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* Active page button */
    .active-button>button {{
        background-color: #4CAF50 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}

    /* Hover effect for all buttons */
    .stButton>button:hover {{
        background-color: #d1d1d1;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }}

    /* Hover effect for active button */
    .active-button>button:hover {{
        background-color: #45a049 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.25);
    }}

    /* Align Results (right inward) and Stats (left inward) */
    .left-col {{
        display: flex;
        justify-content: flex-end;
    }}
    .right-col {{
        display: flex;
        justify-content: flex-start;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Two inward-facing buttons ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f'<div class="left-col {"active-button" if st.session_state.page=="Results" else ""}">', unsafe_allow_html=True)
    results_clicked = st.button("📋 Results", key="results_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown(f'<div class="right-col {"active-button" if st.session_state.page=="Stats" else ""}">', unsafe_allow_html=True)
    stats_clicked = st.button("📊 Stats", key="stats_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Handle page navigation ---
if results_clicked:
    st.session_state.page = "Results"
elif stats_clicked:
    st.session_state.page = "Stats"

# --- PAGE 1: RESULTS ---
if st.session_state.page == "Results":
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

    # --- Genre Filter ---
    all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))
    selected_genres = st.sidebar.multiselect("🎭 Filter by Genre(s)", all_genres)

    # --- Year Filter ---
    def parse_year_range(year_str):
        if pd.isna(year_str):
            return None, None
        match = re.match(r"^\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*$", str(year_str))
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            return start, end
        return None, None

    all_years = []
    for y in df["Year"].dropna():
        start, end = parse_year_range(y)
        if start is not None:
            all_years.append(start)

    unique_years = sorted(set(all_years))
    selected_years = st.sidebar.multiselect("📅 Filter by Year(s)", unique_years)

    # --- Search Bar ---
    st.markdown("### Search")
    search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()

    # --- Apply Filters ---
    if search_term:
        filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]

    if selected_genres:
        filtered_df = filtered_df[
            filtered_df["Genres"].apply(lambda x: all(g in x for g in selected_genres if isinstance(x, str)))
        ]

    if selected_language != "Select Language":
        filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language, na=False)]

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

    sort_options = {"Ultimate Score": "Ultimate Score", "General Score": "General Score", "Last Watched": "Timestamp"}
    for g in genre_columns:
        sort_options[g] = g

    default_sort_display = "Ultimate Score"
    sort_choice_display = st.sidebar.selectbox(
        "📌 Sort by",
        list(sort_options.keys()),
        index=list(sort_options.keys()).index(default_sort_display)
    )
    sort_choice = sort_options[sort_choice_display]

    sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"])
    ascending = True if sort_order == "Ascending" else False

    if sort_choice == "Timestamp":
        filtered_df["Timestamp"] = pd.to_datetime(filtered_df["Timestamp"], errors="coerce")

    filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

    # --- Display Results ---
    results_count = len(filtered_df)
    st.write(f"### Results ({sort_choice_display}) — {results_count} found")

    if filtered_df.empty:
        st.warning("No movies found with the current filters/search.")
    else:
        left_space, main_area, right_space = st.columns([1, 3, 1])
        with main_area:
            for i, (_, row) in enumerate(filtered_df.iterrows(), start=1):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                        st.image(row["Poster"], width=200)
                    else:
                        st.write("📌 No poster available")
                with col2:
                    st.markdown(f"### #{i}. {row['Title']} ({row['Year']})")
                    st.write(f"🏆 Ultimate Ranking: #{row['Ultimate Ranking']}")
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

# --- PAGE 2: STATS ---
elif st.session_state.page == "Stats":
    st.header("📊 Stats Page")
    st.info("This section will display movie statistics soon. Stay tuned!")
