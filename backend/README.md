# Contradiction Finder — backend

Run from `backend/`:

```bash
pip install -r requirements.txt
cp .env.example .env   # optional; works with no keys (mock NLI mode)
python3 -m uvicorn app.main:app --port 8003
```

Tests: `python3 -m pytest tests/ -v` (9 tests).
