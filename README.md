# AI-Powered Business Entrepreneur Assistant

**Using Generative AI, RAG, NLP, and Machine Learning**

A final-year B.E./B.Tech AIML major project: a full-stack web application that
acts as a virtual business advisor for entrepreneurs and startup founders.

---

## Abstract

This project combines a Retrieval-Augmented Generation (RAG) pipeline over a
curated business knowledge base with a Large Language Model (LLM) to answer
natural-language business questions; an NLP layer to classify query intent; a
Machine Learning module (Random Forest) to predict business risk; K-Means
customer segmentation; and supporting tools for business-plan generation,
market analysis, and PDF/Excel report export — wrapped in a Flask web app
with authentication and a SQLite database. A built-in **Demo Mode** ensures
the entire application runs and is fully demonstrable even without a live
LLM API key.

---

## Features

### Decision Support modules (what differentiates this from a generic chatbot)
- **Business Analyzer**: structured Business Profile input → real Financial
  Feasibility Engine (revenue, cost, profit margin, ROI, break-even) → ML
  Risk Prediction → combined **Business Health Score** (0-100, five weighted
  sub-scores, formula fully transparent)
- **Risk Factor Explanation**: ranks which inputs drove the ML prediction
  using the trained model's real `feature_importances_`, tagged with
  direction (increases/reduces risk) for the user's specific values
- **What-If Simulator**: sliders (price, daily customers, rent, marketing)
  recalculate profit/ROI/break-even live in the browser, using the same
  formulas as the server-side engine
- **Business Idea Generator**: given a budget + interests, returns
  comparable business ideas, each scored with the real trained Random
  Forest model (not static text)
- **Competitor Analysis**: structured competitor comparison table with a
  differentiation-opportunity prompt
- **My Businesses**: every analysis is saved per-user and revisitable

### Core AI/ML
- AI chatbot with structured, section-based responses, connected to the
  user's saved Business Profile when one exists (references real numbers,
  not just generic advice) — and shows the actual RAG source documents
  retrieved for each answer as visible citations
- Real RAG retrieval (TF-IDF + cosine similarity) over a `.txt` knowledge base
- Rule-based NLP intent classifier (8 business categories)
- Random Forest **Business Risk Prediction** (Low / Medium / High)
- K-Means **Customer Segmentation** (Budget / Regular / Premium / High-Value)

### Supporting features
- User registration / login / logout with hashed passwords and sessions
- **Business Plan Generator** (10-section plan, savable)
- **Market Analysis** tool (target market, competition, opportunities, threats)
- Analytics dashboard with Chart.js visualizations
- Query history (view / delete past conversations)
- PDF and Excel report export (ReportLab, OpenPyXL)
- **Demo Mode**: app works fully with zero external API dependency

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js |
| Backend | Python 3.10+, Flask |
| Database | SQLite + SQLAlchemy (Flask-SQLAlchemy) |
| AI/NLP | Custom keyword-based intent classifier |
| RAG | scikit-learn TF-IDF + cosine similarity |
| LLM | Pluggable OpenAI-compatible API client, with Demo Mode fallback |
| ML | scikit-learn (Random Forest, K-Means) |
| Reports | ReportLab (PDF), OpenPyXL (Excel) |

---

## Architecture

```
User → Browser (Bootstrap UI)
     → Flask routes (auth / dashboard / chatbot / business / prediction / reports)
     → AI layer (nlp.py → rag.py → llm.py) for chat
     → ML layer (train_model.py / predict.py / segmentation.py) for risk & segments
     → SQLAlchemy models → SQLite (instance/app.db)
```

See `DIAGRAMS.md` for full Mermaid diagrams (architecture, data flow, use-case,
ER diagram, ML workflow, RAG workflow).

---

## Folder Structure

```
ai_business_assistant/
├── app.py                  Flask entry point
├── config.py                Central config (reads .env)
├── requirements.txt
├── .env.example
├── database/                 SQLAlchemy models + init
├── routes/                    Flask blueprints (auth, dashboard, chatbot, business, prediction, reports)
├── ai/                         NLP, RAG, LLM client, prompt templates
├── ml/                          Training, prediction, segmentation, preprocessing
├── data/                         business_dataset.csv, customer_dataset.csv (synthetic)
├── knowledge_base/                RAG source documents (.txt)
├── templates/                      Jinja2 / Bootstrap HTML
├── static/                          CSS / JS
├── reports/                          Generated PDF/Excel output
├── tests/                             pytest test suite
└── instance/                           app.db (created on first run)
```

---

## Installation (Windows + VS Code)

### 1. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
copy .env.example .env
```

Open `.env` and set `SECRET_KEY` to any random string. Leave `LLM_API_KEY`
blank to run in **Demo Mode** (recommended for viva/demo), or fill it in with
a real OpenAI-compatible API key to enable live LLM responses.

### 4. Train the Machine Learning model

```bash
python ml/train_model.py
```

This trains the Random Forest risk model on `data/business_dataset.csv` and
saves `ml/model.pkl` + `ml/encoders.pkl`. Prints accuracy, precision, recall,
F1-score, and a confusion matrix.

### 5. Run the application

```bash
python app.py
```

The database (`instance/app.db`) is created automatically on first run. Open
the printed URL, typically:

```
http://127.0.0.1:5000
```

### 6. (Optional) Run the test suite

```bash
pip install pytest
pytest tests/
```

---

## Demo Credentials

No demo account is pre-seeded — register a new account from the **Register**
page on first run (takes 10 seconds).

---

## Demo Mode

If `LLM_API_KEY` is empty in `.env` (default), the app automatically runs in
**Demo Mode**:
- The chatbot returns structured, template-based responses (still driven by
  real NLP intent classification and real RAG retrieval from the knowledge
  base — only the final LLM generation step is templated).
- Business Plan Generator and Market Analysis use built-in templates.
- ML Risk Prediction and Customer Segmentation are unaffected — they are
  genuine scikit-learn models regardless of Demo Mode.
- The Dashboard and Analytics pages work normally.

This means the entire project can be demonstrated in a viva with **zero
internet dependency** for the AI portions.

---

## API / Route Reference

| Method | Route | Description |
|---|---|---|
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | Logout |
| GET | `/dashboard` | Main dashboard |
| GET | `/chat` | Chatbot UI |
| POST | `/chat` | Send a chat message |
| POST | `/chat/new` | Start new conversation |
| GET | `/history` | List conversations |
| POST | `/history/<id>` | Delete a conversation |
| GET/POST | `/business-plan` | Generate business plan |
| POST | `/business-plan/save` | Save generated plan |
| GET/POST | `/market-analysis` | Market analysis tool |
| GET/POST | `/prediction` | ML risk prediction |
| GET/POST | `/business-analyzer` | Business Profile → Feasibility + Risk + Health Score |
| GET | `/business-analyzer/<id>` | View saved analysis + What-If simulator |
| GET | `/my-businesses` | Saved business profile history |
| POST | `/my-businesses/<id>/delete` | Delete a saved profile |
| GET/POST | `/idea-generator` | ML-scored Business Idea Generator |
| GET/POST | `/competitor-analysis` | Competitor comparison tool |
| GET | `/analytics` | Analytics dashboard |
| GET | `/reports` | Reports home |
| GET | `/reports/pdf` | Export PDF report |
| GET | `/reports/excel` | Export Excel report |

---

## Dataset Disclaimer

`data/business_dataset.csv` and `data/customer_dataset.csv` are **synthetic,
academically generated datasets** created for demonstration purposes. Model
accuracy figures reflect performance on this synthetic data only and are
**not** a claim of real-world predictive accuracy. This is stated explicitly
in the UI (Risk Prediction page) and in generated reports.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'flask_sqlalchemy'` | Run `pip install -r requirements.txt` inside the activated venv |
| "Model not found" error on Prediction page | Run `python ml/train_model.py` first |
| Chatbot always shows "[DEMO MODE]" | Expected if `LLM_API_KEY` is blank in `.env` — this is normal/by design |
| Port 5000 already in use | Edit the last line of `app.py` to use a different port, e.g. `port=5050` |
| `instance/app.db` seems out of date after model changes | Delete `instance/app.db` and restart `python app.py` to recreate tables |

---

## Future Enhancements

- Swap the local TF-IDF retriever for a vector database (e.g., FAISS, Chroma)
  for larger knowledge bases
- Add JWT-based API authentication for a separate mobile client
- Add XGBoost as a selectable advanced risk-prediction model
- Real market-data integration for the Market Analysis module
- Multi-language support for the chatbot

---

## Academic Project Documentation

See `ACADEMIC_DOCUMENTATION.md` for the full 18-chapter project report
(Introduction through Conclusion), `DIAGRAMS.md` for Mermaid architecture/
workflow diagrams, and `VIVA_QUESTIONS.md` for 30+ prepared viva Q&A.

---

## License / Data Notice

All knowledge-base content and datasets in this repository were written or
synthetically generated specifically for this academic project. No
copyrighted third-party datasets are included.
