import streamlit as st
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Noel's Movie Rankings")

# --- Load Google Sheet ---
csv_url = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/export?format=csv&gid=1030199938"
df = pd.read_csv(csv_url, quotechar='"', engine='python')

# --- Clean columns ---
df.columns = df.columns.str.strip()
df.rename(columns={"Movie/TV Show Name": "Title"}, inplace=True)
df["Ultimate Ranking"] = df["Ultimate Score"].rank(method="min", ascending=False).astype(int)

# --- Page state ---
if "page" not in st.session_state:
    st.session_state.page = "Results"

# --- Page Heading ---
st.markdown("<h1 style='text-align: center;'>🎬 Noel's Movie Rankings Database</h1>", unsafe_allow_html=True)

# --- Page Switch Buttons (above search bar) ---
st.markdown("""
    <style>
    /* Create a clean two-button layout that hugs the center line */
    .button-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 1.5em;
    }
    .left-button, .right-button {
        flex: 0 0 42%;              /* make both wide but not too wide */
        height: 3.2em;              /* roughly search bar height */
        font-size: 1.1em;
        font-weight: 600;
        border-radius: 10px;
    }
    .left-button {
        display: flex;
        justify-content: flex-end;  /* push Results toward center */
    }
    .right-button {
        display: flex;
        justify-content: flex-start; /* push Stats toward center */
    }
    </style>
""", unsafe_allow_html=True)

# Two side-by-side buttons aligned toward the center
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="left-button">', unsafe_allow_html=True)
    results_clicked = st.button("📋 Results", key="results_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="right-button">', unsafe_allow_html=True)
    stats_clicked = st.button("📊 Stats", key="stats_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Handle navigation ---
if results_clicked:
    st.session_state.page = "Results"
elif stats_clicked:
    st.session_state.page = "Stats"
    
# --- Helper function ---
def parse_year_range(year_str):
    if pd.isna(year_str):
        return None, None
    match = re.match(r"^\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*$", str(year_str))
    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        return start, end
    return None, None

# --- Sidebar Filters ---
if st.session_state.page == "Results":
    st.sidebar.header("Filters & Search")

    # --- Search ---
    search_term = st.sidebar.text_input("🔎 Search by Title")

    # --- Languages ---
    all_languages = df["Language"].dropna().apply(lambda x: [lang.strip() for lang in str(x).split(",")]).sum()
    unique_languages = sorted(set(all_languages))
    language_options = ["All"] + unique_languages
    # If user clicked from Stats, preselect that language
    if "selected_language" in st.session_state and st.session_state.selected_language in language_options:
        default_lang_index = language_options.index(st.session_state.selected_language)
    else:
        default_lang_index = 0
    selected_language = st.selectbox("🌍 Language", language_options, index=default_lang_index)

    # --- Genres ---
    all_genres = sorted(set(g.strip() for sublist in df["Genres"].dropna().str.split(",") for g in sublist))
    # If user clicked a genre from Stats page, preselect it
    if "selected_genres" in st.session_state and all(g in all_genres for g in st.session_state.selected_genres):
        default_genres = st.session_state.selected_genres
    else:
        default_genres = []

    selected_genres = st.multiselect("🎭 Genre(s)", all_genres, default=default_genres)

    # --- Years ---
    all_years = []
    for y in df["Year"].dropna():
        start, _ = parse_year_range(y)
        if start:
            all_years.append(start)
    unique_years = sorted(set(all_years))
    selected_years = st.sidebar.multiselect("📅 Year(s)", unique_years)

    # --- Sort ---
    genre_columns = [col for col in df.columns if "Score" in col]
    sort_options = {"Ultimate Score": "Ultimate Score", "General Score": "General Score", "Last Watched": "Timestamp"}
    for g in genre_columns:
        sort_options[g] = g
    default_sort_display = "Ultimate Score"
    sort_choice_display = st.sidebar.selectbox("📌 Sort by", list(sort_options.keys()), index=list(sort_options.keys()).index(default_sort_display))
    sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"], index=0)

    sort_choice = sort_options[sort_choice_display]
    ascending = sort_order == "Ascending"

    # --- Apply filters ---
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[filtered_df["Title"].str.contains(search_term, case=False, na=False)]

    if selected_genres:
        filtered_df = filtered_df[filtered_df["Genres"].apply(lambda x: all(g in x for g in selected_genres if isinstance(x,str)))]

    if selected_language != "All":
        filtered_df = filtered_df[filtered_df["Language"].str.contains(selected_language, na=False)]

    if selected_years:
        def year_in_range(row_year, selected):
            start, end = parse_year_range(row_year)
            if start is None: return False
            return any(sel >= start and sel <= end for sel in selected)
        filtered_df = filtered_df[filtered_df["Year"].apply(lambda y: year_in_range(y, selected_years))]

    if sort_choice == "Timestamp":
        filtered_df["Timestamp"] = pd.to_datetime(filtered_df["Timestamp"], errors="coerce")

    filtered_df = filtered_df.sort_values(by=sort_choice, ascending=ascending)

    # --- Display results ---
    st.write(f"### Results ({sort_choice_display}) — {len(filtered_df)} found")
    if filtered_df.empty:
        st.warning("No movies found with the current filters/search.")
    else:
        _, main, _ = st.columns([1, 3, 1])
        with main:
            for i, (_, row) in enumerate(filtered_df.iterrows(), start=1):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if isinstance(row["Poster"], str) and row["Poster"].startswith("http"):
                        st.image(row["Poster"], width=200)
                    else:
                        st.write("📌 No poster available")
                with c2:
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

# --- PAGE: STATS ---
if st.session_state.page == "Stats":
    st.header("📊 Statistics")
    total_movies = len(df)
    st.markdown(f"<div style='text-align:center;'><span style='font-size:60px; font-weight:bold; color:white'>{total_movies}</span><br><span style='font-size:20px; color:white'>Movies and TV Shows watched</span></div>", unsafe_allow_html=True)

    # --- Language bar graph ---
lang_counts = df["Language"].dropna().str.split(",").explode().str.strip().value_counts()
lang_counts = lang_counts.sort_index(ascending=True).sort_values(ascending=False, kind="mergesort")

fig_lang = go.Figure(go.Bar(
    x=lang_counts.index,
    y=lang_counts.values,
    text=lang_counts.values,
    textposition='outside',
    textfont=dict(color='white', size=12),
    marker=dict(color=lang_counts.values, colorscale='Viridis', line=dict(width=0))
))

fig_lang.update_layout(
    margin=dict(l=40, r=40, t=80, b=40),
    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(color='white')),
    yaxis=dict(showgrid=False, showticklabels=False),
    title=dict(text="Movies/TV Shows by Language", x=0.5, font=dict(color='white', size=22))
)

# Ensure numbers are not clipped
fig_lang.update_traces(textposition='outside', cliponaxis=False)

# --- Make graph clickable ---
clicked_lang = plotly_events(fig_lang, click_event=True, hover_event=False, select_event=False, override_height=None, key="lang_click")

# --- Handle click: redirect to Results page filtered by that language ---
if clicked_lang and len(clicked_lang) > 0:
    selected_language = clicked_lang[0]['x']  # get the clicked language name
    st.session_state.page = "Results"
    st.session_state.selected_language = selected_language  # custom session key for your filters
    st.rerun()

# --- Display chart normally ---
st.plotly_chart(fig_lang, use_container_width=True)

    # --- Genre bar graph ---
genre_counts = df["Genres"].dropna().str.split(",").explode().str.strip().value_counts().sort_values(ascending=True)
fig_height = max(400, len(genre_counts)*30)

fig_genre = px.bar(
    genre_counts,
    x=genre_counts.values,
    y=genre_counts.index,
    orientation='h',
    text=genre_counts.values,
    color=genre_counts.values,
    color_continuous_scale='Cividis'
)

fig_genre.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    margin=dict(l=120, r=40, t=60, b=40),
    height=fig_height,
    title=dict(text="Movies/TV Shows by Genre", x=0.5, font=dict(color='white', size=22)),
    xaxis=dict(showgrid=False, showline=False, tickfont=dict(color='white')),
    yaxis=dict(showgrid=False, showline=False, tickfont=dict(color='white'))
)

fig_genre.update_traces(textposition='outside', textfont=dict(color='white', size=12))

# --- Make the bar graph clickable ---
clicked_genre = plotly_events(
    fig_genre,
    click_event=True,
    hover_event=False,
    select_event=False,
    override_height=None,
    key="genre_click"
)

# --- Handle click: redirect to Results page filtered by that genre ---
if clicked_genre and len(clicked_genre) > 0:
    selected_genre = clicked_genre[0]['y']  # 'y' holds the genre name (since it's a horizontal bar)
    st.session_state.page = "Results"
    st.session_state.selected_genres = [selected_genre]  # pass as list for multiselect compatibility
    st.experimental_rerun()

# --- Display normally ---
st.plotly_chart(fig_genre, use_container_width=True)

# Year line graph
def extract_first_year(y):
    if pd.isna(y): return None
    match = re.match(r"^\s*(\d{4})", str(y))
    return int(match.group(1)) if match else None

df['First Year'] = df['Year'].apply(extract_first_year)
movies_per_year = df['First Year'].value_counts().sort_index()
fig_year = px.line(x=movies_per_year.index, y=movies_per_year.values, markers=True,
                    labels={'x':'Year','y':'Number of Movies/TV Shows'})
fig_year.update_traces(line=dict(color='cyan', width=3), marker=dict(size=8, color='cyan'))
fig_year.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        title=dict(text="Movies/TV Shows by Year", x=0.5, font=dict(color='white', size=22)),
                        margin=dict(l=40,r=40,t=60,b=80),
                        xaxis=dict(showgrid=False, showline=True, linecolor='white', tickfont=dict(color='white')),
                        yaxis=dict(showgrid=False, showline=True, linecolor='white', tickfont=dict(color='white')))
st.plotly_chart(fig_year, use_container_width=True)

