# The Digital Duck Ecosystem

*SPL is the conductor. The digital-duck libraries are the orchestra.*

When you run an SPL workflow, you are not just running SPL. The runtime delegates to a set of purpose-built, open-source Python libraries — each one a clean abstraction over a class of infrastructure concern. This appendix introduces them.

The goal of each `dd-*` library is the same: **one consistent API, many swappable backends**. Just as SPL lets you swap `--adapter ollama` for `--adapter anthropic` without changing your `.spl` file, the `dd-*` libraries let you swap SQLite for DuckDB, FAISS for ChromaDB, or sentence-transformers for OpenAI embeddings — without changing the SPL layer above them.

This is the same principle at every level of the stack: declarative at the top, swappable at the bottom.

---

## The Stack at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                      SPL workflows (.spl)                    │
│              GENERATE · CALL · EVALUATE · STORE             │
└───────────────────────┬─────────────────────────────────────┘
                        │  SPL runtime (spl/)
          ┌─────────────┼──────────────┐
          │             │              │
    dd-logging    dd-config       dd-db / dd-vectordb / dd-embed
    dd-llm        dd-cache        dd-extract / dd-format / dd-dogic
```

The SPL runtime calls into `dd-*` libraries for infrastructure concerns. Your `.spl` code never sees the library — it sees only the SPL primitive (`GENERATE`, `CALL`, `@memory[...]`). The library swap happens in configuration, not in code.

---

## The Libraries

### `dd-config` — Configuration Management

**Purpose:** Load, merge, and validate configuration from any format — YAML, JSON, TOML, INI, or `.env` — with dot-path access and environment variable interpolation.

**Key API:**
```python
from dd_config import Config

cfg = Config.load("~/.spl/config.yaml")
adapter = cfg.get("adapter", default="ollama")
cfg.validate(schema)
```

**SPL use:** The `~/.spl/config.yaml` file that drives `spl run` defaults — adapter, model, log level, storage path — is loaded via `dd-config`. Change the format of your config file without touching SPL.

---

### `dd-logging` — Shared Logging

**Purpose:** Consistent, timestamped-file logging for CLI and long-running applications. Hierarchical logger support with automatic handler management.

**Key API:**
```python
from dd_logging import setup_logging, get_logger

setup_logging(log_dir="~/.spl/logs", log_level="INFO")
log = get_logger("memory_chat")
log.info("Response ready")
```

**SPL use:** Every `LOGGING ... LEVEL INFO` statement in a workflow maps to a `dd-logging` call. Log files in `~/.spl/logs/` are created and managed by this library.

---

### `dd-db` — Relational Database Abstraction

**Purpose:** Unified SQL interface over nine relational backends — SQLite, DuckDB, PostgreSQL, MySQL, Snowflake, BigQuery, ClickHouse, SQL Server, Oracle — returning results as pandas DataFrames.

**Key API:**
```python
from dd_db import SQLiteDB, DuckDB, PostgresDB

db = SQLiteDB("~/.spl/memory.db")
db.connect()
df = db.run_query("SELECT value FROM spl_kv WHERE key = :k", {"k": "chat_user_profile"})
db.disconnect()
```

**SPL use:** The `STORAGE`-typed workflow input (`@memory STORAGE(sqlite, '~/.spl/memory.db')`) is backed by `dd-db`. The `spl memory` CLI commands (list, get, set, delete) use the same library. Swap `sqlite` for `duckdb` or `postgres` in the STORAGE declaration and the SPL code is unchanged.

---

### `dd-embed` — Embedding Abstraction

**Purpose:** Shared embedding model adapter layer with seven built-in backends — sentence-transformers, HuggingFace, Ollama, OpenAI, OpenRouter, Gemini, Voyage — plus a disk-persistent embedding cache.

**Key API:**
```python
from dd_embed import get_adapter

adapter = get_adapter("sentence_transformers", model_name="all-MiniLM-L6-v2")
result = adapter.embed(["Who is Wen?", "What is SPL?"])
vectors = result.embeddings   # numpy array, shape (2, 384)
```

**SPL use:** `spl doc-rag add` and `spl code-rag import` use `dd-embed` to convert text into vectors before storing them. The embedding model is locked in `vector_config.json` at index creation time — swap it by deleting the index and re-importing with a different provider.

---

### `dd-vectordb` — Vector Database Abstraction

**Purpose:** Unified semantic search interface over four vector backends — in-memory NumPy, FAISS, ChromaDB, and Qdrant — with consistent add/search/delete API and metadata filtering.

**Key API:**
```python
from dd_vectordb import FAISSVectorDB, Document, SearchResult

db = FAISSVectorDB(dimension=384)
db.add_documents([Document(id="p1", text="SPL is declarative", vector=vec)])
results: list[SearchResult] = db.search(query_vector, k=3)
db.save("~/.spl/vectors.faiss")
```

**SPL use:** `spl doc-rag` uses `FAISSVectorDB` for document retrieval. `spl code-rag` uses `ChromaVectorDB` for SPL example lookup. The `rag.query(context.question, top_k=3)` call in a `PROMPT` statement routes through this library. Swap FAISS for Qdrant in configuration without touching any `.spl` files.

---

### `dd-llm` — LLM Abstraction

**Purpose:** Shared LLM adapter layer with six built-in backends — Claude CLI, Anthropic API, OpenAI, Gemini, OpenRouter, Ollama — with multi-provider retry, exponential backoff, and automatic fallback.

**Key API:**
```python
from dd_llm import get_adapter, LLMResponse

adapter = get_adapter("ollama", model="phi4")
response: LLMResponse = adapter.call("Explain quantum computing in one sentence.")
print(response.text, response.tokens_used)
```

**SPL use:** Currently, SPL has its own adapter layer (`spl/adapters/`). Migrating to `dd-llm` is on the roadmap — it would consolidate 13 SPL adapters into the shared library, giving all `dd-*` tools and SPL a unified LLM backend.

---

### `dd-cache` — Caching Abstraction

**Purpose:** Backend-swappable caching with TTL support — in-memory, SQLite disk cache, and Redis — with a `get_or_set()` pattern for lazy population and automatic cache statistics.

**Key API:**
```python
from dd_cache import DiskCache

cache = DiskCache("~/.spl/cache.db", ttl=3600)
result = cache.get_or_set("embed:Who is Wen?", lambda: adapter.embed(["Who is Wen?"]))
```

**SPL use:** `spl run --cache` enables response caching for `GENERATE` calls. The backing store will migrate to `dd-cache` — letting users choose in-memory caching for development or Redis for production without changing the SPL layer.

---

### `dd-extract` — Document Extraction

**Purpose:** Abstraction layer for extracting structured text from PDFs and other document formats, returning clean Markdown.

**Key API:**
```python
from dd_extract import PDFExtractor

extractor = PDFExtractor()
markdown = extractor.extract("report.pdf")
```

**SPL use:** section 3.2 (Chat Over PDF) and future document-processing recipes will use `dd-extract` to pull text out of PDFs before indexing them with `spl doc-rag add`.

---

### `dd-format` — Document Formatting

**Purpose:** Convert Markdown to PDF, DOCX, and HTML output formats.

**Key API:**
```python
from dd_format import markdown_to_pdf, markdown_to_docx

markdown_to_pdf("# Report\nSPL is great.", "output.pdf")
markdown_to_docx(text, "output.docx")
```

**SPL use:** Planned for report-generation recipes — workflows that produce structured Markdown outputs and need to render them as polished documents.

---

### `dd-dogic` — Document Conversion Pipeline

**Purpose:** Orchestrates document conversion pipelines using a PocoFlow (Extract → Transform → Format) pattern — converting between PDF, Markdown, HTML, and DOCX.

**Key API:**
```python
from dd_dogic import convert

convert("report.pdf", output_format="markdown")
```

**SPL use:** High-level document processing pipelines that span extraction, transformation, and formatting. `dd-dogic` composes `dd-extract` and `dd-format` into a single orchestrated flow — the same "composition layer" philosophy that SPL applies to LLM workflows.

---

## Integration Status

| Library | Status in SPL |
|---------|--------------|
| `dd-config` | Integrated — drives `~/.spl/config.yaml` |
| `dd-logging` | Integrated — backs all `LOGGING` statements |
| `dd-db` | Integrated — backs `STORAGE`-typed inputs and `spl memory` CLI |
| `dd-embed` | Integrated — backs `spl doc-rag` and `spl code-rag` |
| `dd-vectordb` | Integrated — backs semantic search in RAG recipes |
| `dd-llm` | Roadmap — will consolidate 13 SPL LLM adapters |
| `dd-cache` | Roadmap — will back `spl run --cache` |
| `dd-extract` | Roadmap — will back PDF ingestion in document recipes |
| `dd-format` | Roadmap — will back Markdown-to-document output recipes |
| `dd-dogic` | Roadmap — will back multi-format document pipelines |

---

## Where to Find Them

All `dd-*` libraries are developed by the Digital Duck team and hosted at:

```
https://github.com/digital-duck/
```

Each library follows the same conventions: clean abstract base class, multiple concrete adapters, consistent `get_adapter()` factory, zero mandatory dependencies (extras install what you need). The same philosophy that makes SPL portable makes every library in the stack portable.

If you build tools on top of SPL — custom adapters, new storage backends, domain-specific RAG pipelines — the `dd-*` libraries are the natural foundation. The stack is open, documented, and designed to be extended.
