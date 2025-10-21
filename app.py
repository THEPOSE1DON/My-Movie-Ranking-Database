import streamlit as st
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config (wide mode) ---
st.set_page_config(layout="wide")
# --- Hide default Streamlit sidebar ---
st.markdown(
    """
    <style>
    /* Hide the default sidebar */
    .css-1d391kg {display:none;}
    .css-1v3fvcr {padding-left: 0px !important;}  /* remove sidebar padding on main content */

    /* Make the main content full width */
    .appview-container .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Optional: adjust spacing for horizontal filters */
    .stSelectbox, .stMultiselect, .stRadio {
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# --- Initialize Page State ---
if "page" not in st.session_state:
    st.session_state.page = "Results"

# --- CSS for buttons ---
st.markdown("""
    <style>
    .stButton>button {
        height: 3.2em !important;
        width: 85% !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        background-color: #f0f0f0;
        color: black;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .active-button>button {
        background-color: #4CAF50 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #d1d1d1;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .active-button>button:hover {
        background-color: #45a049 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.25);
    }
    .left-col {
        display: flex;
        justify-content: flex-end;
    }
    .right-col {
        display: flex;
        justify-content: flex-start;
    }
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

# --- Helper function for year parsing ---
def parse_year_range(year_str):
    if pd.isna(year_str):
        return None, None
    match = re.match(r"^\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*$", str(year_str))
    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        return start, end
    return None, None

# --- PAGE 1: RESULTS ---
if st.session_state.page == "Results":
    filtered_df = df.copy()

    # --- Prepare Filter Options ---
    all_languages = df["Language"].dropna().apply(lambda x: [lang.strip() for lang in str(x).split(",")]).sum()
    unique_languages = sorted(set(all_languages))
    language_options = ["Select Language"] + unique_languages

    all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))

    all_years = []
    for y in df["Year"].dropna():
        start, _ = parse_year_range(y)
        if start is not None:
            all_years.append(start)
    unique_years = sorted(set(all_years))

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

    # --- Search Bar ---
    st.markdown("### Search")
    search_term = st.text_input("🔎 Search by Movie/TV Show Name").lower()

    # --- Horizontal Filters (Below Search Bar) ---
    row1_cols = st.columns([1, 1, 1])
    row2_cols = st.columns([1, 1])

    # Row 1: Language, Genre(s), Year(s)
    with row1_cols[0]:
        selected_language = st.selectbox("🌍 Language", language_options)
    with row1_cols[1]:
        selected_genres = st.multiselect("🎭 Genre(s)", all_genres)
    with row1_cols[2]:
        selected_years = st.multiselect("📅 Year(s)", unique_years)

    # Row 2: Sort by, Order
    with row2_cols[0]:
        sort_choice_display = st.selectbox(
            "📌 Sort by",
            list(sort_options.keys()),
            index=list(sort_options.keys()).index(default_sort_display)
        )
    with row2_cols[1]:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

    sort_choice = sort_options[sort_choice_display]
    ascending = True if sort_order == "Ascending" else False

    # --- Apply Filters ---
    if search_term:
        filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(search_term, na=False)]
    if selected_genres:
        filtered_df = filtered_df[filtered_df["Genres"].apply(lambda x: all(g in x for g in selected_genres if isinstance(x, str)))]
    if selected_language != "Select Language":
        filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language, na=False)]
    if selected_years:
        def year_in_range(row_year, selected):
            start, end = parse_year_range(row_year)
            if start is None:
                return False
            return any(sel >= start and sel <= end for sel in selected)
        filtered_df = filtered_df[filtered_df["Year"].apply(lambda y: year_in_range(y, selected_years))]

    if sort_choice == "Timestamp":
        filtered_df["Timestamp"] = pd.to_datetime(filtered_df["Timestamp"], errors="coerce")

    filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

    # --- Display Results Header ---
    results_count = len(filtered_df)
    st.write(f"### Results ({sort_choice_display}) — {results_count} found")

    # --- Display Results ---
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
if st.session_state.page == "Stats":
    st.header("📊 Statistics")

# --- Total movies and shows watched ---
total_movies = len(df)
st.markdown(
    f"""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 40px;'>
        <span style='font-size: 60px; font-weight: bold; color: white;'>{total_movies}</span><br>
        <span style='font-size: 20px; color: white;'>Movies and Shows watched</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Language Bar Graph ---
# --- Prepare data ---
language_counts = (
    df["Language"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
)

# Sort by count (descending), then alphabetically for ties
language_counts = (
    language_counts.sort_index(ascending=True)  # alphabetical first
    .sort_values(ascending=False, kind="mergesort")  # then by count, stable sort
)

languages = language_counts.index.tolist()
counts = language_counts.values.tolist()

# --- Create figure ---
fig_lang = go.Figure()

# Add bars with white numbers above (textposition='outside')
fig_lang.add_trace(
    go.Bar(
        x=languages,
        y=counts,
        marker=dict(
            color=counts,
            colorscale='Viridis',
            line=dict(width=0)
        ),
        text=counts,
        textposition='outside',
        textfont=dict(color='white', size=12),
        hovertemplate='%{x}: %{y}<extra></extra>'
    )
)

# --- Style (dark, clean, white text) ---
fig_lang.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=False,
        showline=False,
        tickangle=-45,
        tickfont=dict(color='white')
    ),
    yaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=False
    ),
    margin=dict(l=80, r=80, t=60, b=60),  # <-- balanced margins to center graph
    title=dict(
        text="Movies/TV Shows by Language",
        x=0.5,
        xanchor='center',
        font=dict(color='white', size=22)
    )
)

# Center align the graph
st.plotly_chart(fig_lang, use_container_width=True)

# --- Genre Bar Graph ---
genre_counts = (
    df["Genres"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
    .sort_values(ascending=True)
)

import plotly.express as px

# Dynamically adjust figure height based on number of genres
fig_height = max(400, len(genre_counts) * 30)

fig_genre = px.bar(
    genre_counts,
    x=genre_counts.values,
    y=genre_counts.index,
    orientation='h',
    labels={'x': 'Number of Movies/TV Shows', 'y': 'Genre'},
    text=genre_counts.values,
    color=genre_counts.values,
    color_continuous_scale='Cividis'
)

fig_genre.update_layout(
    title=dict(
        text="Movies/TV Shows by Genre",
        x=0.5,
        xanchor='center',
        font=dict(color='white', size=22)
    ),
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=120, r=40, t=60, b=40),
    height=fig_height,
    xaxis=dict(
        showgrid=False,
        showline=False,
        tickfont=dict(color='white')
    ),
    yaxis=dict(
        showgrid=False,
        showline=False,
        tickfont=dict(color='white')
    ),
)

# White text labels on bars
fig_genre.update_traces(
    textfont=dict(color='white', size=12),
    textposition='outside'
)

st.plotly_chart(fig_genre, use_container_width=True)

# --- Year Line Graph ---
# --- Prepare data: extract first year ---
def extract_first_year(year_str):
    if pd.isna(year_str):
        return None
    match = re.match(r"^\s*(\d{4})", str(year_str))
    if match:
        return int(match.group(1))
    return None

df['First Year'] = df['Year'].apply(extract_first_year)

# --- Aggregate number of movies per year ---
movies_per_year = df['First Year'].value_counts().sort_index()
years = movies_per_year.index.tolist()
counts = movies_per_year.values.tolist()

# --- Create line chart ---
fig_year = px.line(
    x=years,
    y=counts,
    markers=True,
    labels={'x': 'Year', 'y': 'Number of Movies/TV Shows'}
)

# --- Style chart ---
fig_year.update_traces(line=dict(color='cyan', width=3), marker=dict(size=8, color='cyan'))
fig_year.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=False,
        showline=True,
        linecolor='white',
        tickfont=dict(color='white'),
        dtick=1,
        tickvals=years,  # only show years with data
        ticktext=[str(y) for y in years],  # ensure labels match
        tickangle=90  # rotate labels vertically
    ),
    yaxis=dict(
        showgrid=False,
        showline=True,
        linecolor='white',
        tickfont=dict(color='white')
    ),
    title=dict(
        text="Movies/TV Shows by Year",
        x=0.5,
        xanchor='center',
        font=dict(color='white', size=22)
    ),
    margin=dict(l=40, r=40, t=60, b=80)  # extra bottom margin for vertical labels
)

# --- Display chart in Streamlit ---
st.plotly_chart(fig_year, use_container_width=True)

