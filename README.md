# 🎓 College Advisor

A RAG-powered college recommendation system built on India's official AISHE
(All India Survey on Higher Education) government dataset — helping 12th-passed
students find colleges based on their location and preferences, since income
levels and access vary widely across India.

## 🔗 Live Demo
https://college-advisor-izt2krlv49h8cboiuozmdj.streamlit.app/

## 📊 What it does

- Covers **52,509 colleges** across India, sourced from the AISHE government dataset (via AIKosh)
- Lets users filter by **state** and **district**
- Semantic search — describe what you're looking for in plain language, and the
  system finds the closest-matching colleges using vector similarity
- An LLM (via Groq) turns the matches into a clear, natural-language recommendation
- **Honest by design**: the system does not have fee, placement, or ranking data.
  Instead of guessing, it explicitly says so and shares a reference link so
  students can verify details themselves
- Interactive dashboard with state-wise, management-type, and establishment-year visualizations

## 🏗️ Tech Stack

| Layer | Tool |
|---|---|
| Data source | AISHE dataset via AIKosh API |
| Data processing | Python, Pandas |
| Database | Supabase (PostgreSQL + pgvector) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM | Groq (`openai/gpt-oss-120b`) |
| UI | Streamlit |
| Automation | GitHub Actions (scheduled data refresh) |

## 🔄 Data Pipeline

Run the full pipeline:
```bash
python run.py
```

Run individual steps:
```bash
python -m src.scrape_colleges       # fetch latest AISHE dataset
python -m src.clean_data            # clean & normalize
python -m src.load_to_db            # load into Supabase
python -m src.generate_embeddings   # generate & store vector embeddings
python -m src.scrape_fees           # generate reference search links
```

## 🖥️ Running the Dashboard

```bash
streamlit run app.py
```

## 📁 Project Structure
college-advisor/
├── config/ # settings, environment config
├── data/ # raw and processed data
├── src/ # pipeline scripts (scrape, clean, load, embed, RAG)
├── sql/ # schema and reference queries
├── app.py # Streamlit dashboard
├── run.py # orchestrates the full data pipeline
└── requirements.txt


## ⚠️ Known Data Limitations

- Fee, placement, and ranking data are **not available** in the AISHE dataset —
  the system explicitly discloses this rather than guessing
- A small number of newer private universities (established post-2013) may be
  missing from this particular AISHE snapshot, a known gap in the source data
- Reference links point students to search results (not scraped fee data) for
  further details, keeping the system free of scraping/ToS risk

## 🚀 Setup

1. Clone the repo and create a virtual environment
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in:
   - `AIKOSH_API_KEY`, `AIKOSH_API_BASE_URL`, `AIKOSH_DATASET_ID`, `AIKOSH_VERSION`
   - `DATABASE_URL` (Supabase connection string)
   - `GROQ_API_KEY`
4. Run `python run.py` to populate the database
5. Run `streamlit run app.py` to launch the dashboard

## 👤 Author

Built by Ayush as part of a self-directed Data Engineering learning roadmap.
