# pentiq
PENTIQ: Interactive post-match reports and tactical visualizations for Europe's Big Five football leagues.
# Post-Match & Tactical Analysis App — Top 5 European Leagues

An interactive web application for exploring **post-match reports** and **tactical visualizations** across Europe's top 5 football leagues: La Liga, Premier League, Serie A, Bundesliga, and Ligue 1.

The app combines automated data scraping, a Supabase-backed database, and a Streamlit interface to deliver up-to-date match analysis, team performance breakdowns, and squad/venue information for each league.

## Features

- 📊 Post-match reports for the five major European leagues
- 🧠 Tactical visualizations (formations, stats, team of the week)
- 🔐 User authentication
- 🗄️ Persistent data storage via Supabase
- 🔄 Automated data collection from Fotmob

## Tech Stack

- **Frontend / App:** [Streamlit](https://streamlit.io/)
- **Database:** [Supabase](https://supabase.com/)
- **Data source:** Fotmob (scraped)
- **Language:** Python

## Repository Structure

| File / Folder | Description |
|---|---|
| `app.py` | Main entry point of the Streamlit application. Renders the UI, routes between views (post-match reports, tactical visualizations) and orchestrates calls to the database and auth modules. |
| `auth.py` | Handles user authentication logic — login, session state, and access control for the app. |
| `database.py` | Manages the connection to Supabase and contains the functions used to read/write match, team, and player data. |
| `Scrapping datos fotmob.ipynb` | Jupyter notebook used to scrape raw match, team, and player data from Fotmob for the five leagues. Source notebook for the data pipeline feeding the database. |
| `extraer equipo de la semana.ipynb` | Jupyter notebook that processes scraped data to compute and extract the **Team of the Week** for each league. |
| `pruebas.ipynb` | Sandbox notebook used for testing and experimentation (e.g. validating deployment on Streamlit Cloud) before promoting changes to production files. |
| `links_photos_stadia_5league.xlsx` | Spreadsheet containing reference links to team/player photos and stadium images for the five leagues, used as visual assets in the app. |
| `requirements.txt` | Python dependencies required to run the project. |
| `.gitignore` | Files and folders excluded from version control. |
| `LICENSE` | Repository license. |
| `README.md` | Project documentation (this file). |

## Getting Started

### Prerequisites

- Python 3.9+
- A Supabase project (URL + API key)

### Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

### Configuration

Create a `.env` file (or use Streamlit secrets) with your Supabase credentials:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Run the app

```bash
streamlit run app.py
```

## Data Pipeline

1. **`Scrapping datos fotmob.ipynb`** collects raw match/team/player data from Fotmob for the five leagues.
2. **`extraer equipo de la semana.ipynb`** processes that data to generate the weekly Team of the Week.
3. Processed data is stored in **Supabase** via `database.py`.
4. **`app.py`** reads from Supabase and renders post-match reports and tactical visualizations in the Streamlit UI.

## Roadmap

- [ ] Add more advanced tactical metrics (xG, pressing maps, heatmaps)
- [ ] Historical season comparison
- [ ] Mobile-friendly layout

## License

This project is licensed under the terms specified in the [LICENSE](./LICENSE) file.
