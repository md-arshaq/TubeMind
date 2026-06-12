# 🧠 TubeMind — YouTube Video Intelligence Platform

<div align="center">

**Chat with any YouTube video using AI-powered RAG**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![Gemini](https://img.shields.io/badge/Gemini_AI-Free-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white)](https://langchain.com)

</div>

---

## 📖 What is TubeMind?

TubeMind is a full-stack AI application that lets you **paste any YouTube URL** and have an **intelligent conversation** with the video's content. It uses **Retrieval-Augmented Generation (RAG)** to fetch relevant transcript segments and generate accurate, context-aware answers.

### ✨ Key Features

- 🎬 **Paste & Analyze** — Submit any YouTube URL → transcript is fetched, chunked, and embedded
- 💬 **Chat with Videos** — Ask questions and get AI-powered answers with source citations
- 📝 **Instant Summaries** — One-click comprehensive video summaries
- 🏷️ **Topic Extraction** — Automatically identified key topics
- 📚 **Video Library** — Build your personal collection of analyzed videos
- ⏱️ **Timestamp Citations** — Answers reference specific video timestamps
- 💾 **Chat History** — Conversations are persisted for future reference

---

## 🏗️ Architecture

```
┌──────────────────┐     HTTP/REST      ┌──────────────────┐
│   Next.js 15     │ ◄──────────────── │   FastAPI         │
│   React Frontend │                    │   Python Backend  │
│   (Vercel)       │                    │   (Railway)       │
└──────────────────┘                    └──────┬───────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                    ┌─────────▼──┐   ┌────────▼──────┐  ┌─────▼──────┐
                    │ ChromaDB   │   │ Google Gemini  │  │ SQLite/    │
                    │ Vector     │   │ LLM +          │  │ PostgreSQL │
                    │ Store      │   │ Embeddings     │  │ Database   │
                    └────────────┘   └───────────────┘  └────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15, React, TypeScript, Tailwind CSS | Premium UI with dark mode |
| **Backend** | FastAPI, Python 3.12, LangChain | REST API + RAG pipeline |
| **LLM** | Google Gemini 2.0 Flash (Free) | Text generation |
| **Embeddings** | Gemini text-embedding-004 (Free) | Vector representations |
| **Vector DB** | ChromaDB | Semantic search over transcripts |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Metadata + chat history |
| **Deployment** | Vercel + Railway | Cloud hosting |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- A free [Google Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/md-arshaq/TubeMind.git
cd TubeMind
```

### 2. Set up the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`.

### 3. Set up the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/videos` | Analyze a YouTube video |
| `GET` | `/api/videos` | List all analyzed videos |
| `GET` | `/api/videos/{id}` | Get video details |
| `DELETE` | `/api/videos/{id}` | Delete a video |
| `POST` | `/api/videos/{id}/chat` | Ask a question (RAG) |
| `GET` | `/api/videos/{id}/chat/history` | Get chat history |
| `POST` | `/api/videos/{id}/summary` | Generate summary |
| `GET` | `/health` | Health check |

---

## 🐳 Docker

```bash
# Set your API key
export GEMINI_API_KEY=your-key-here

# Run with Docker Compose
docker-compose up --build
```

---

## 📁 Project Structure

```
TubeMind/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Environment settings
│   │   ├── api/routes/       # REST API endpoints
│   │   ├── core/             # RAG pipeline, transcript, vectorstore
│   │   ├── models/           # Pydantic schemas + SQLAlchemy models
│   │   └── db/               # Database session management
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (landing, chat, library)
│   │   └── lib/              # API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🧪 How the RAG Pipeline Works

1. **Ingestion** — YouTube transcript is fetched and split into overlapping chunks
2. **Embedding** — Each chunk is embedded using Gemini's text-embedding-004 model
3. **Storage** — Embeddings are stored in ChromaDB with timestamp metadata
4. **Retrieval** — User's question is embedded and similar chunks are retrieved
5. **Generation** — Retrieved context + question are sent to Gemini for answer generation

---

## 📄 License

MIT License — feel free to use this for your portfolio!

---

<div align="center">

Built with ❤️ using **Google Gemini AI** (completely free!)

</div>
