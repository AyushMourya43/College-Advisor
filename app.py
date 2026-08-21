import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

from config.settings import DATABASE_URL
from src.rag_pipeline import get_recommendations


st.set_page_config(page_title="College Advisor", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { font-weight: 700; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem;
    }
    div[data-testid="stMetric"] {
        background-color: #F1F5F9;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    div[data-testid="stMetricLabel"] { color: #475569 !important; }
    div[data-testid="stMetricValue"] { color: #0F172A !important; }
    .tech-badge {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #BFDBFE;
    }
    @media (max-width: 640px) {
        h1 { font-size: 1.6rem; }
    }
    </style>
""", unsafe_allow_html=True)


def connect_to_db():
    return psycopg2.connect(DATABASE_URL)


@st.cache_data(ttl=3600)
def load_overview_data():
    conn = connect_to_db()
    df = pd.read_sql("SELECT state, management, college_type, year_of_establishment FROM colleges;", conn)
    conn.close()
    return df


@st.cache_data(ttl=3600)
def get_states_list():
    conn = connect_to_db()
    df = pd.read_sql("SELECT DISTINCT state FROM colleges ORDER BY state;", conn)
    conn.close()
    return df["state"].dropna().tolist()


@st.cache_data(ttl=3600)
def get_districts_for_state(state):
    conn = connect_to_db()
    df = pd.read_sql(
        "SELECT DISTINCT district FROM colleges WHERE state = %(state)s ORDER BY district;",
        conn, params={"state": state}
    )
    conn.close()
    return df["district"].dropna().tolist()


def get_college_details(college_name):
    conn = connect_to_db()
    query = """
        SELECT name, state, district, college_type, management,
               university_name, reference_search_url
        FROM colleges
        WHERE name ILIKE %(name)s
        LIMIT 5;
    """
    df = pd.read_sql(query, conn, params={"name": f"%{college_name}%"})
    conn.close()
    return df


# ---- Header ----
st.title("🎓 College Advisor")
st.caption("Find the right college based on your location and preferences — powered by AISHE data")

df = load_overview_data()

# ---- Top metrics row ----
m1, m2, m3 = st.columns(3)
m1.metric("Total Colleges", f"{len(df):,}")
m2.metric("States Covered", df["state"].nunique())
m3.metric("Government Colleges", f"{df['management'].str.contains('Government', na=False).sum():,}")

st.markdown("""
    <div>
        <span class="tech-badge">📊 Data: AISHE / AIKosh</span>
        <span class="tech-badge">🔍 Search: RAG (Semantic + Vector)</span>
        <span class="tech-badge">🤖 AI: LLM (Groq)</span>
        <span class="tech-badge">🗄️ Database: PostgreSQL + pgvector</span>
    </div>
""", unsafe_allow_html=True)

st.write("")

# ---- Graphs: 2x2 grid ----
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    state_counts = df["state"].value_counts().reset_index()
    state_counts.columns = ["state", "count"]
    fig1 = px.bar(
        state_counts.head(15), x="state", y="count",
        title="Top 15 States by Number of Colleges",
        color_discrete_sequence=["#2563EB"]
    )
    fig1.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    mgmt_counts = df["management"].value_counts().reset_index()
    mgmt_counts.columns = ["management", "count"]
    fig2 = px.pie(
        mgmt_counts, names="management", values="count",
        title="Government vs Private Colleges",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig2.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    type_counts = df["college_type"].value_counts().reset_index()
    type_counts.columns = ["college_type", "count"]
    fig3 = px.bar(
        type_counts, x="college_type", y="count",
        title="Colleges by Type",
        color_discrete_sequence=["#2563EB"]
    )
    fig3.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    year_df = df.dropna(subset=["year_of_establishment"])
    year_df = year_df[year_df["year_of_establishment"] >= 1950]
    year_counts = year_df["year_of_establishment"].value_counts().reset_index()
    year_counts.columns = ["year", "count"]
    year_counts = year_counts.sort_values("year")
    fig4 = px.line(
        year_counts, x="year", y="count",
        title="Colleges Established Over Time (since 1950)",
        color_discrete_sequence=["#2563EB"]
    )
    fig4.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ---- Section: Look up a specific college by name ----
st.header("📌 Look Up a Specific College")
lookup_name = st.text_input("Enter college name", placeholder="e.g. Bharati Vidyapeeth")

if st.button("Look Up"):
    if lookup_name:
        results = get_college_details(lookup_name)
        if results.empty:
            st.warning("No matching college found.")
        else:
            for _, row in results.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['name']}**")
                    st.write(f"📍 {row['district']}, {row['state']}")
                    st.write(f"🏛️ {row['college_type']} — {row['management']}")
                    st.write(f"🎓 Affiliated to: {row['university_name']}")
                    if row['reference_search_url']:
                        st.markdown(f"[More Info]({row['reference_search_url']})")

st.divider()

# ---- Section: Natural language recommendation search ----
st.header("🔍 Find Your College")

states = get_states_list()

col1, col2 = st.columns(2)
with col1:
    selected_state = st.selectbox("State", ["Any"] + states)

with col2:
    if selected_state != "Any":
        districts = get_districts_for_state(selected_state)
        selected_district = st.selectbox("District", ["Any"] + districts)
    else:
        selected_district = "Any"
        st.selectbox("District", ["Select a state first"], disabled=True)

user_query = st.text_input(
    "What are you looking for?",
    placeholder="e.g. engineering college with good academics"
)

if st.button("Search", type="primary"):
    if not user_query:
        st.warning("Please enter what you're looking for.")
    else:
        state_filter = None if selected_state == "Any" else selected_state
        with st.spinner("Finding colleges for you..."):
            result = get_recommendations(user_query, state=state_filter)
        st.markdown(result)