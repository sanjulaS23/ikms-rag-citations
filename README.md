# IKMS RAG

IKMS RAG is an evidence-aware document Q&A application for PDF files. It ingests uploaded documents, splits them into chunks, retrieves the most relevant evidence, and answers questions with inline citations and source snippets.

## Architecture

React/Vite
    ↓
Vercel
    ↓
FastAPI
    ↓
Cloud LLM API
    ↓
Vector Database

## Features

- PDF upload and validation
- PDF text extraction and chunking
- semantic retrieval
- RAG question answering
- citation-aware answer generation
- source evidence display with page references

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Optional: Ollama installed locally for dev-only mode

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### Backend

```bash
cd D:\Projects\IKMS_RAG
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir backend/src --host 0.0.0.0 --port 8000 --reload
```

### Optional local Ollama mode

```env
LOCAL_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
OLLAMA_EMBEDDING_MODEL=all-minilm
```

If Ollama is not available, set `LOCAL_OLLAMA=false` and configure a cloud LLM API key.

## Environment Variables

Copy [.env.example](.env.example) to `.env` and fill in the values for your environment.

Required variables:

- `VITE_API_BASE_URL`: public backend URL used by the frontend in production
- `FRONTEND_ORIGIN`: exact frontend origin allowed by FastAPI CORS
- `LOCAL_OLLAMA`: `true` for local dev with Ollama, `false` for cloud mode
- `CLOUD_LLM`: LLM provider (`openai` is the current default)
- `LLM_API_KEY`: cloud LLM provider API key
- `LLM_MODEL`: cloud chat model, e.g. `gpt-4o-mini`
- `LLM_EMBEDDING_MODEL`: cloud embedding model, e.g. `text-embedding-3-small`
- `VECTOR_DB`: `pinecone` for the managed vector store
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_INDEX`: Pinecone index name
- `PINECONE_NAMESPACE`: optional vector namespace

## Backend Deployment

This project is designed for a public cloud backend such as Render or Railway.

Recommended steps:

1. Create a FastAPI service on Render.
2. Add the environment variables from [.env.example](.env.example).
3. Set `LOCAL_OLLAMA=false`.
4. Add `LLM_API_KEY` and `PINECONE_API_KEY`.
5. Deploy the backend from the repository.
6. Confirm `/health` responds successfully.

## Frontend Deployment

Deploy the frontend to Vercel with:

```env
VITE_API_BASE_URL=https://your-render-backend-url
```

The frontend should not hard-code `localhost`, `127.0.0.1`, or `ngrok` in production.

## Production Deployment

The final public architecture is:

- Vercel for the React UI
- Render/Railway for the FastAPI service
- OpenAI or another cloud LLM provider for generation
- Pinecone for persistent vector retrieval

This removes the dependency on your local Windows PC, local Ollama, and ngrok tunnels.

## Troubleshooting

### CORS errors

- Confirm `FRONTEND_ORIGIN` matches the exact Vercel URL
- Ensure the backend is not using wildcard origins with credentials enabled

### Backend unavailable

- Check the deployed health endpoint: `/health`
- Verify the backend service is running and the port is exposed

### LLM API errors

- Confirm `LLM_API_KEY` is set
- Confirm `LLM_MODEL` is valid for the selected cloud provider
- Ensure `LOCAL_OLLAMA=false` if using the cloud mode

### Vector database errors

- Check `PINECONE_API_KEY`
- Confirm the `PINECONE_INDEX` exists
- Confirm the backend has network access to the vector database

### PDF upload errors

- Verify the uploaded file is a valid PDF
- Check file size is below the backend limit
- Inspect backend logs for indexing failures

## License

This project is licensed under the MIT License.
