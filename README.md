<p align="center">
  <h1 align="center">Quick Insights</h1>
  <p align="center">AI-Powered Data Analytics Platform</p>
  <p align="center">
    <a href="https://dataanalyzer-1-4jz9.onrender.com/">Live Demo</a> &middot;
    <a href="#features">Features</a> &middot;
    <a href="#tech-stack">Tech Stack</a> &middot;
    <a href="#architecture">Architecture</a> &middot;
    <a href="#getting-started">Getting Started</a>
  </p>
</p>

---

**Quick Insights** turns raw CSV and Excel files into actionable intelligence. Upload a dataset, ask questions in plain English, and get accurate answers powered by an AI Data Agent that writes and executes real pandas code against your actual data — no hallucinated numbers, no guesswork.

> **Try it now:** [https://dataanalyzer-1-4jz9.onrender.com/](https://dataanalyzer-1-4jz9.onrender.com/)

---

## Features

### AI Data Agent
Ask any question about your data in natural language. The AI agent generates pandas code, executes it in a secure sandbox against your full dataset, and returns precise, computed answers — not approximations from sample rows.

- Real-time code generation and execution
- Self-healing: if generated code fails, the agent auto-corrects and retries
- Inline interactive charts rendered with ECharts when visual answers help

### AI-Generated Reports
One-click comprehensive reports with:
- Statistical summaries (distributions, correlations, outliers)
- Key insights and patterns discovered in your data
- Interactive visualizations embedded throughout
- Download as formatted content

### Smart Chart Suggestions
The AI analyzes your columns and data types to recommend the most effective visualizations — bar charts, scatter plots, line graphs, heatmaps — rendered as interactive ECharts.

### Dataset Management
- Upload CSV and Excel files (`.csv`, `.xlsx`, `.xls`)
- Automatic column type detection and metadata extraction
- View statistics, preview data, and manage multiple datasets
- Per-user dataset isolation with JWT authentication

### Interactive Dashboards
Create and save custom dashboards with multiple chart panels arranged to tell your data's story.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5, Django REST Framework |
| **AI Engine** | OpenAI GPT-4o-mini, Pandas code execution |
| **Frontend** | Alpine.js, Tailwind CSS, ECharts |
| **Auth** | JWT (SimpleJWT) — register, login, token refresh |
| **Database** | SQLite (dev) / PostgreSQL (production-ready) |
| **Caching** | Django Redis (optional) |
| **Deployment** | Docker, Gunicorn, WhiteNoise, Render |
| **Data Processing** | Pandas, NumPy, OpenPyXL |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│          Alpine.js SPA  ·  Tailwind CSS  ·  ECharts             │
└──────────────────────────────┬──────────────────────────────────┘
                               │  REST API (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DJANGO REST FRAMEWORK                       │
│                                                                 │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌─────────────┐  │
│  │ Accounts │  │ Datasets  │  │ AI Insights│  │ Dashboards  │  │
│  │          │  │           │  │            │  │             │  │
│  │ Register │  │ Upload    │  │ Ask (NL)   │  │ Create      │  │
│  │ Login    │  │ Preview   │  │ Insights   │  │ Save        │  │
│  │ JWT Auth │  │ Stats     │  │ Reports    │  │ Charts      │  │
│  │ Profile  │  │ Charts    │  │ Suggest    │  │ Layout      │  │
│  └──────────┘  └───────────┘  └─────┬──────┘  └─────────────┘  │
│                                     │                           │
└─────────────────────────────────────┼───────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                  ▼
           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
           │  OpenAI API  │  │  Pandas      │  │  Sandboxed   │
           │  GPT-4o-mini │  │  DataFrame   │  │  exec()      │
           │              │  │  (Full Data) │  │  Environment │
           │  Code Gen +  │  │              │  │              │
           │  Interpret   │  │  Real Stats  │  │  Safe Exec   │
           └──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow: AI Question Answering

```
User Question (natural language)
        │
        ▼
┌─────────────────────┐
│  1. CODE GENERATION  │  AI receives: question + column schema + dataset stats
│     (GPT-4o-mini)    │  AI produces: pandas code with `result` variable
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  2. SANDBOX EXECUTE  │  Forbidden tokens blocked (exec, eval, os, sys, etc.)
│     (Restricted env) │  Code runs against full DataFrame copy
└──────────┬──────────┘  On error → AI gets traceback → auto-fixes → retry
           ▼
┌─────────────────────┐
│  3. INTERPRET        │  AI receives: original question + computed results
│     (GPT-4o-mini)    │  AI produces: human-readable answer + optional chart
└──────────┬──────────┘
           ▼
   Accurate, computed answer
   delivered to the user
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register/` | Create account |
| `POST` | `/api/auth/login/` | Get JWT tokens |
| `POST` | `/api/auth/refresh/` | Refresh access token |
| `GET` | `/api/auth/profile/` | User profile |
| `GET/POST` | `/api/datasets/` | List / upload datasets |
| `GET/DELETE` | `/api/datasets/{id}/` | Dataset detail |
| `GET` | `/api/datasets/{id}/preview/` | Data preview |
| `GET` | `/api/datasets/{id}/stats/` | Column statistics |
| `POST` | `/api/datasets/{id}/batch_charts/` | Generate charts |
| `POST` | `/api/ai/ask/` | Ask a question (AI Agent) |
| `POST` | `/api/ai/insights/` | Generate insights |
| `POST` | `/api/ai/suggest-charts/` | AI chart suggestions |
| `POST` | `/api/ai/report/` | Full AI report |

---

## Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API key

### Local Setup

```bash
# Clone the repository
git clone https://github.com/AtharvThakur7/DataAnalyzer.git
cd DataAnalyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### Docker

```bash
docker build -t quick-insights .
docker run -p 8000:8000 --env-file .env quick-insights
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `DEBUG` | No | `True` for development (default: `True`) |
| `ALLOWED_HOSTS` | No | Comma-separated hostnames |
| `DATABASE_URL` | No | PostgreSQL URL (defaults to SQLite) |
| `REDIS_URL` | No | Redis cache URL |

---

## Project Structure

```
DataAnalyzer/
├── apps/
│   ├── accounts/       # User registration, JWT auth, profiles
│   ├── datasets/       # File upload, parsing, statistics, charts
│   ├── ai_insights/    # AI agent, insights, reports, chart suggestions
│   ├── dashboards/     # Custom dashboard creation and management
│   └── core/           # Health check, shared utilities
├── templates/
│   ├── landing.html    # Public landing page
│   └── app.html        # Main SPA (Alpine.js)
├── DataAnalyzer/       # Django project settings, URLs, WSGI
├── Dockerfile          # Production Docker image
├── Procfile            # Render deployment commands
└── requirements.txt    # Python dependencies
```

---

## Security

- All AI code execution runs in a **sandboxed environment** with restricted builtins
- Forbidden operations: `exec()`, `eval()`, `__import__`, `open()`, `os`, `sys`, `subprocess`
- DataFrames are copied before execution — originals are never modified
- JWT-based authentication with token refresh
- Per-user dataset isolation
- CORS and CSRF protection in production

---

## Roadmap

- [ ] Database connectors (PostgreSQL, MySQL, MongoDB)
- [ ] Data warehouse integration (BigQuery, Snowflake)
- [ ] Scheduled automated reports
- [ ] Team collaboration and shared dashboards
- [ ] Persistent cloud storage for uploads
- [ ] Export dashboards as PDF

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is open source and available under the [MIT License](LICENSE).
