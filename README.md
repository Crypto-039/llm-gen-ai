# llm-gen-ai
# 🤖 Self-Fixing Generative AI System

> **NOVEL ARCHITECTURE**: Combines RAG + Tree-of-Thought + Sandbox execution with forward-looking CVE scanning and shadow production traffic evaluation.

## 🚀 60-Second Quick Start

1. **Clone & Setup**
   ```bash
   git clone <repo-url>
   cd self-fixing-ai
   cp .env.example .env  # Add your API keys
   pip install -r requirements.txt

Start the System
bashuvicorn app.main:app --reload

Test Core Features
bash# Tree-of-Thought chat
curl -X POST http://localhost:8000/chat-tot \
  -H "Content-Type: application/json" \
  -d '{"message": "Fix this SQL injection vulnerability"}'

# Explainability
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"query": "How does the fix work?", "include_reasoning": true}'

Run Forward Scanner (Weekly)
bashpython scripts/forward_scanner.py --feeds cve pypi --severity critical high

Test Shadow Traffic (Nightly)
bashpython scripts/shadow_traffic.py \
  --source-logs sample_traffic.json \
  --shadow-endpoint http://localhost:8000 \
  --mirror-percentage 0.1 \
  --output shadow# Self-Fixing Generative AI System Repository
