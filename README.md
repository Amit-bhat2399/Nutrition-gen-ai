**AI‑Powered Nutrition Tracker**
*Python · Lightweight web app · Calories & Macros · Trends & Insights*

A simple, portfolio‑friendly nutrition tracker that lets you **log foods**, see **calorie & macro totals** for the day, and review **weekly trends**. The app is designed to be easily runnable from a single file and extendable with AI‑assisted insights.

> Repo includes a runnable app (`app.py`), a `requirements.txt`, and a short PDF read‑me. See “Project Structure” below.

---

## ✨ Features (at a glance)
- **Quick food logging** — add name, portion, calories, protein, carbs, fat
- **Daily totals & goals** — track progress toward calorie/macro goals
- **Trend views** — weekly summaries for calories, protein, carbs, fat
- **CSV export** — take your log into Excel / pandas for deeper analysis

---

## 🚀 Quickstart

### 1) Set up Python & install deps
```bash
git clone https://github.com/Amit-bhat2399/AI-Powered-Nutrition-Tracker
cd AI-Powered-Nutrition-Tracker

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Run the app

Depending on the framework used inside app.py, use one of the following:
```bash

# If Streamlit (common for simple data apps)
streamlit run app.py

# If Flask/FastAPI or a plain script
python app.py
# or
export FLASK_APP=app.py && flask run
```
Usage

Set your daily goals — e.g., 2200 kcal, 150 g protein, 250 g carbs, 70 g fat.

Add a food — enter name, portion/serving size, and macros (or calories).

Review your day — see totals vs. goals and macro split for the day.

Switch to Trends — view 7‑day summaries to spot patterns (e.g., low‑protein days).

Export — save your log to CSV for further analysis in pandas/Excel/BI.


🧱 How it Works

A lightweight UI collects food entries and stores them in memory or a simple file (e.g., CSV).

Daily aggregates (calories, P/C/F totals) are computed from entries.

Weekly trends are computed with rolling windows and summarized charts/tables.
