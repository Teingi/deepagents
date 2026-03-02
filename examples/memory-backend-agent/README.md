# Memory Backend Agent

A minimal Deep Agent that uses **MemoryBackend** for file storage instead of the filesystem. All paths (e.g. `/notes/idea.txt`) are stored as path-keyed records in a `PathMemoryStore`.

## What this demonstrates

- **MemoryBackend** – file operations (ls, read_file, write_file, edit_file, etc.) are backed by a path-keyed store, not disk.
- **PathMemoryStore** – this example uses an in-memory implementation (`store.InMemoryPathStore`). For production you can plug in:
  - **PowerMemPathStore** from `deepagents.backends` with a PowerMem `Memory` instance for persistent, multi-tenant storage.
  - Any custom store that implements the `PathMemoryStore` protocol.

## Quick start

### Prerequisites

- Python 3.11+
- **Model API key**: Anthropic (Claude) **or** OpenAI-compatible (e.g. Qwen / 通义千问 via DashScope)

### Setup

```bash
cd deepagents/examples/memory-backend-agent
uv venv --python 3.11
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e .
cp .env.example .env
# Edit .env: set OPENAI_API_BASE + OPENAI_API_KEY + OPENAI_MODEL for Qwen,
# or leave OPENAI_API_BASE unset and set ANTHROPIC_API_KEY for Claude
```

### Run

```bash
# Default: list root and describe
python agent.py

# Save a note
python agent.py "Save to /notes/ideas.txt: 1. Learn MemoryBackend 2. Try PowerMem"

# List and read
python agent.py "List files under /notes/ and read /notes/ideas.txt"
```

## Using PowerMem (optional)

PowerMem runs **in-process** (same process as the agent). There is no separate “PowerMem server” to deploy unless you use PowerMem’s own server mode elsewhere.

### 1. Install PowerMem

```bash
cd deepagents/examples/memory-backend-agent
uv pip install powermem
# or: pip install powermem
```

### 2. Configure PowerMem

PowerMem reads configuration from a **.env** in the current working directory (or from a config object). Minimum for path-keyed storage:

- **vector_store**: e.g. SQLite (default) or pgvector / OceanBase
- **embedder**: embedding model for the vector store (required by PowerMem)

Add to your `.env` (see `.env.powermem.example` for a full template):

```bash
# PowerMem: vector store (SQLite for local dev)
DATABASE_PROVIDER=sqlite
# If using sqlite, optional: DATABASE_PATH=./data/powermem.db

# PowerMem: embedder (e.g. DashScope/Qwen)
EMBEDDING_PROVIDER=qwen
EMBEDDING_API_KEY=your_dashscope_key
EMBEDDING_MODEL=text-embedding-v3
```

PowerMem’s `create_memory()` will load these via `auto_config()`. For PathMemoryStore we call `add(..., infer=False)`, so no LLM is required for plain path-keyed writes; you may still set LLM in .env if PowerMem uses it for other features.

### 3. Wire PowerMem into the agent

Use **PowerMemPathStore** with a PowerMem **Memory** instance:

```python
from deepagents.backends import MemoryBackend, PowerMemPathStore
from powermem import create_memory

memory = create_memory()  # loads from .env
store = PowerMemPathStore(memory)

def backend_factory(runtime):
    return MemoryBackend(store, runtime)

agent = create_deep_agent(..., backend=backend_factory)
```

### 4. Run with PowerMem

We provide an optional script that uses PowerMem when installed:

```bash
uv pip install powermem
cp .env.powermem.example .env   # then edit .env with your keys
python agent_powermem.py "Save to /notes/idea.txt: hello PowerMem"
```

If `powermem` is not installed, `agent_powermem.py` falls back to the in-memory store and prints a short note.

## Project structure

```
memory-backend-agent/
├── agent.py              # Deep Agent with MemoryBackend (in-memory store)
├── agent_powermem.py     # Optional: same agent with PowerMem (or fallback to in-memory)
├── store.py              # InMemoryPathStore for demo (no PowerMem)
├── AGENTS.md             # Agent instructions
├── README.md
├── pyproject.toml
├── .env.example          # Model API keys (Qwen / Claude)
├── .env.powermem.example # PowerMem config (vector_store, embedder)
└── .gitignore
```

## Requirements

- deepagents >= 0.3.5
- langchain-anthropic >= 1.3.1
- langgraph >= 1.0.6
- python-dotenv >= 1.0.0
- rich >= 13.0.0
