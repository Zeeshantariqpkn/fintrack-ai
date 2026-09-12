# FinTrack AI — Agentic Financial Analytics for SMBs

FinTrack AI is an **agentic AI financial decision system** powered by **Groq (Llama 3.3 70B)**.

## Agentic pipeline

DATA → CATEGORIZE → ANALYTICS → RISK ┐
                                    ├→ DECISION → CRITIC → INSIGHT → COPILOT
                       OPPORTUNITY ─┘

## Setup

1. Get a free Groq API key: https://console.groq.com/keys
2. Locally:
   ```bash
   pip install -r requirements.txt
   export GROQ_API_KEY=gsk_xxxxxxxxxxxx
   streamlit run app.py
