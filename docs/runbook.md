# Runbook

## Docker Compose (recommended)

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

The services are available at:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Streamlit UI: `http://localhost:8501`

In another terminal, download the configured Ollama models:

```bash
docker exec -it rag-ollama ollama pull nomic-embed-text
docker exec -it rag-ollama ollama pull gemma4:latest
```

If `gemma4:latest` is not available, set `OLLAMA_CHAT_MODEL=llama3.1` in `.env` and pull that model instead.

Check the API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Upload a book through the Streamlit sidebar, then ask a question in the chat. The first request may take time while the model loads.

## Local Python

Start Ollama on the host and make sure both models are available:

```bash
ollama serve
ollama pull nomic-embed-text
ollama pull llama3.1
```

Create a local `.env` from the template, then set:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.1
```

Start the API in one terminal:

```bash
./rag/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start the UI in another:

```bash
./rag/bin/streamlit run app/ui/streamlit_app.py
```

Open `http://localhost:8501`.

## Troubleshooting

- `env file .env not found`: run `cp .env.example .env`.
- `/ready` reports Ollama unavailable: start Ollama or inspect `OLLAMA_BASE_URL`.
- Model not found: pull the exact model name configured in `.env`.
- Chroma permission errors: ensure `/Users/macbook/Documents/GenAI/Projects/Data/DBs/chroma` exists and is writable.
- Docker cannot see books: confirm the host upload directory matches the bind mount in `docker-compose.yml`.
