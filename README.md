# FinTrack AI

**Agentic Financial Analytics for SMBs — Your AI Financial Decision Engine**

FinTrack AI is an agentic AI system that turns raw financial statements into strategic decisions. Upload a bank or credit-card statement (CSV, TSV, or Excel), and a pipeline of **eight specialized AI agents** cleans, categorizes, analyzes, detects risks and opportunities, makes a decision, **verifies that decision with an independent Critic Agent**, and produces an executive briefing — plus a RAG-powered chat copilot for follow-up questions.

Built with **Python · Pandas · NumPy · Plotly · Groq (Llama 3.3 70B) · Streamlit**.

---

## ✨ What Makes It Different

Most financial tools stop at charts. FinTrack AI makes a **decision** and shows the evidence behind it.

- **Not a dashboard.** Charts are the input, not the output.
- **Independent Critic Agent.** The Decision Agent's output is verified — and sent back for revision if the reasoning is weak.
- **Real RAG.** The Copilot retrieves the most relevant financial evidence from a vector index before answering — no hallucinated numbers.
- **Works with or without an API key.** Every agent has a deterministic fallback, so the app never breaks.

---

## 🧠 The Agentic Pipeline
RAW FINANCIAL DATA
│
▼
┌─────────────┐
│ DATA AGENT │ cleans, validates, normalizes
└──────┬──────┘
▼
┌─────────────────────┐
│ CATEGORIZATION AGENT│ LLM-based tagging (8 categories)
└─────────┬───────────┘
▼
┌─────────────────────┐
│ ANALYTICS AGENT │ 13+ metrics + evidence
└─────────┬───────────┘
│
┌──────┴──────┐
▼ ▼
┌────────────┐ ┌──────────────┐
│ RISK AGENT │ │ OPPORTUNITY │
│ │ │ AGENT │
└─────┬──────┘ └──────┬───────┘
└───────┬───────┘
▼
┌────────────────┐
│ DECISION AGENT │◄──┐
└───────┬────────┘ │
▼ │
┌────────────────┐ │
│ CRITIC AGENT │───┘ (revision loop, capped at 3)
└───────┬────────┘
│ APPROVED
▼
┌────────────────┐
│ INSIGHT AGENT │
└───────┬────────┘
▼
┌────────────────┐
│ VECTOR STORE │
└───────┬────────┘
▼
┌────────────────┐
│ AI COPILOT │ RAG-grounded Q&A
└────────────────┘

text

**Every agent has a single responsibility. Every output is structured. Every claim is evidence-backed.**

---

## 🚀 Quick Start

### 1. Get a free Groq API key
Sign up at **https://console.groq.com/keys** and copy your key (starts with `gsk_...`).

### 2. Install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/fintrack-ai.git
cd fintrack-ai
pip install -r requirements.txt
3. Set the API key
macOS / Linux:

bash
export GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
Windows PowerShell:

powershell
$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxx"
Windows cmd:

cmd
set GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
Or create .streamlit/secrets.toml:

toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
4. Run the app
bash
streamlit run app.py
Open http://localhost:8501 in your browser.

No API key? No problem. The app runs fully in deterministic fallback mode — all 8 agents still work, just without LLM-generated reasoning text.

☁️ Deploy on Streamlit Cloud
Push this repo to GitHub (without .streamlit/secrets.toml)

Go to https://share.streamlit.io → New app → select your repo → app.py

Click Manage app → Settings → Secrets

Paste:

toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
# Optional — only for real vector embeddings:
# HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxx"
Click Save → the app reboots automatically

Done. Your app is live at https://YOUR-APP-NAME.streamlit.app.

📊 How to Use
1. Upload a statement
Click Browse files → select a CSV, TSV, or Excel file

Or click Try sample data for an instant demo

Supported file types: .csv, .tsv, .txt, .xlsx, .xls

Any column names work. The loader auto-detects:

Date column: date, transaction_date, txn_date, posted_date, Date, etc.

Description column: description, memo, payee, merchant, narration, etc.

Amount column: amount, value, total, amt, Debit/Credit split, or Amount + Type

Formats handled:

Comma, semicolon, pipe, tab separators

Currency symbols ($, €, £)

Thousands separators (1,234.56)

Parentheses negatives ((1234.56))

European decimal commas (18400,50)

Multiple date formats

2. Watch the agents work
The agent timeline fills in real time. The full pipeline takes ~5–10 seconds with Groq.

3. Explore the results
Overview — KPIs, health score, AI decision card, cash-flow chart

Agent Center — every agent's reasoning and evidence

Analytics — trends, categories, top vendors, recurring costs

Risks & Opportunities — evidence-backed findings and recommended actions

AI Copilot — ask questions in plain English

Transactions — search and filter every row

Settings — API status, vector DB, analysis toggles

4. Start over
Click Upload new file in the sidebar — no browser refresh needed.

📁 CSV Format
The absolute minimum is a date column and an amount column. Everything else is optional.

Standard example:

csv
date,description,amount
2024-01-03,Stripe Customer Payouts,18400.00
2024-01-05,ACME Payroll Services,-12500.00
2024-01-07,AWS Cloud Hosting,-820.45
Conventions:

Positive amount → income

Negative amount → expense

Also accepts:

Different column order: Amount, Date, Description

Different casing: Date, DATE, date

Currency symbols: "$18,400.00", "($12,500.00)"

Debit/credit split: Date, Payee, Debit, Credit

Amount + type column: txn_date, memo, value, type (type = debit/credit)

The Data Agent reports exactly which columns it detected on the Agent Center page.

🤖 The 8 Agents
#	Agent	Responsibility
1	Data Agent	Loads file, normalizes columns, parses dates/amounts, drops invalid rows, reports quality
2	Categorization Agent	Assigns each transaction to one of 8 categories: Payroll, Vendors, Utilities, Marketing, Subscriptions, Rent, Income, Other
3	Analytics Agent	Computes 13+ financial metrics with structured evidence
4	Risk Agent	Detects 7 risk types, each with severity and evidence
5	Opportunity Agent	Detects 6 opportunity types with estimated impact
6	Decision Agent	Weighs risks + opportunities and picks the single most important action
7	Critic Agent	Independently verifies the decision — approves or sends back for revision
8	Insight Agent	Writes the executive briefing
🛠️ Tech Stack
Layer	Technology
Language	Python 3.10+
UI	Streamlit
Data	Pandas, NumPy
Charts	Plotly
LLM	Groq API — llama-3.3-70b-versatile
Embeddings	Hugging Face (optional) or deterministic hash fallback
Vector DB	Custom in-memory NumPy cosine-similarity index
State	Streamlit session state (no database)
Deployment	Streamlit Cloud
📂 Project Structure
text
fintrack-ai/
├── app.py                              # Main entry point
├── pages/
│   ├── 1_🤖_Agent_Center.py            # Visual agent pipeline
│   ├── 2_📊_Analytics.py               # Plotly charts
│   ├── 3_⚠️_Risks_&_Opportunities.py   # Detailed risk/opportunity panels
│   ├── 4_💬_AI_Copilot.py              # RAG-powered Q&A
│   ├── 5_📁_Transactions.py            # Filterable table
│   └── 6_⚙️_Settings.py                # Groq + Vector DB config
├── agents/
│   ├── categorize.py                   # Categorization Agent
│   ├── decision.py                     # Decision → Critic loop
│   ├── insights.py                     # Insight Agent
│   └── strategic_agents.py             # Groq client + Analytics/Risk/Opp/Decision/Critic
├── utils/
│   ├── data_processing.py              # Dynamic CSV loader (Data Agent)
│   ├── financial_state.py              # Shared state dataclass
│   ├── ui.py                           # Shared sidebar + CSS
│   └── vector_store.py                 # RAG vector database
├── sample_data/
│   └── sample_transactions.csv         # 41-row demo dataset
├── requirements.txt
└── README.md
⚙️ Configuration
Environment variables / Streamlit secrets
Variable	Required	Purpose
GROQ_API_KEY	Optional	Enables LLM reasoning. Without it, deterministic fallback is used.
HF_TOKEN	Optional	Enables real sentence embeddings for the vector DB. Without it, hash-based embeddings are used.
In-app settings
On the Settings page you can:

Check Groq connection status and run a test

Toggle AI categorization

Toggle AI insight generation

Enable / disable the vector database

Rebuild or clear the vector index

Clear the current analysis

🔒 Security
API keys are never displayed in the UI — only their presence is checked

.streamlit/secrets.toml is gitignored — never commit it

Financial data lives only in session state — nothing persists beyond the browser session

No third-party analytics or tracking

If you accidentally commit a key, revoke it immediately at https://console.groq.com/keys and create a new one.

🧪 Sample Data
Two included datasets:

sample_data/sample_transactions.csv — 41 transactions over 3 months (quick demo)

For a 5,000-row dataset, run the generator in the project root:

bash
python generate_data.py
It creates sample_data/sample_transactions_5000.csv with 3 years of realistic data (seasonality, growth, recurring costs).

🐛 Troubleshooting
Issue	Fix
GROQ_API_KEY not configured	Add the key to env vars or Streamlit secrets
HTTP 404 model does not exist	Run curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer gsk_..." and use an available model ID
Sample data button does nothing	Verify sample_data/sample_transactions.csv is committed to the repo
Data shows as a single column	Check separator — the loader auto-detects ,, ;, \t, |
Could not find a date column	Verify your file has a header row with a recognizable date column
Stale data after upload	Click Upload new file in the sidebar to fully reset
Vector DB shows "0 documents"	Run an analysis first; index builds automatically on first Copilot question
🗺️ Roadmap
Phase 2 — Near-term

PDF statement parsing

Multi-month comparison view

Budget tracking and alerts

Export briefings to PDF / email

Phase 3 — Product

User accounts and multi-tenancy

Client / entity switching for agencies

Bank integrations (Plaid / Teller)

Scenario planning ("what if I cut X by 20%?")

Phase 4 — Scale

Time-series anomaly detection

Cash-flow forecasting

Industry benchmarks

Public API

🤝 Contributing

