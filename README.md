# FastAPI LLM Assignment API

FastAPI service with 3 endpoints:

- `GET /health`
- `POST /summarize`
- `POST /analyze-sentiment`

Both LLM endpoints use OpenAI and include prompt variations (`A`, `B`, `C`) for experimentation.

## 1) Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set environment variables:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"  # optional
```

Run the API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open docs:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 2) Endpoint examples

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Summarize

```bash
curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FastAPI is a modern framework for building APIs quickly with type hints and validation.",
    "max_length": 50,
    "prompt_version": "A"
  }'
```

### Analyze sentiment

```bash
curl -X POST http://127.0.0.1:8000/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am very happy with this service.",
    "prompt_version": "B"
  }'
```

## 3) Prompt experiments

See `prompt_experiments.md` for:

- 3 prompt variations per endpoint
- example outputs
- best prompt choice and rationale

## 4) Deploy to Render (free tier)

1. Push this project to a GitHub repository.
2. In Render, create a new **Web Service** from that repo.
3. Use:
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable:
  - `OPENAI_API_KEY=<your_api_key>`
  - Optional: `OPENAI_MODEL=gpt-4o-mini`
5. Deploy and confirm endpoint health:

```bash
curl https://YOUR_RENDER_URL/health
```


