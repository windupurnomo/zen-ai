# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NL2SQL API - Converts Indonesian natural language commands into SQL queries for a todo table. The system uses sentence transformers for intent classification and rule-based extraction for parameters.

## Architecture

**Layered Architecture:**
- **API Layer** (`api.py`): FastAPI REST endpoints
- **Service Layer** (`service.py`): Singleton business logic orchestrator
- **Core Logic**: Intent classification + SQL generation + Database execution
  - `intent_classifier.py`: Sentence embeddings + cosine similarity (threshold: 0.45)
  - `sql_generator.py`: Keyword-based extraction + SQL generation
  - `db.py`: PostgreSQL connection pooling + AWS SSM credential fetching
  - `knowledge_base.json`: Intent training examples (10-15 per intent)

**Key Design Patterns:**
- Singleton pattern for `NL2SQLService` and `DatabaseManager` (avoids reloading heavy ML model and connection pool)
- Connection pooling for PostgreSQL (2-10 connections)
- AWS SSM Parameter Store for secure credential management
- Multi-stage Dockerfile for optimized image size
- Pydantic schemas for request/response validation

## Development Commands

### Setup

```bash
# Environment setup
cp .env.example .env

# Edit .env for local development:
# USE_AWS_SSM=false
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=todo_db
# DB_USER=postgres
# DB_PASSWORD=your_password

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# API server (development)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# CLI mode (deprecated - no database execution)
python cli.py

# Docker
docker-compose up -d
docker-compose logs -f
```

### Testing

```bash
# All tests
pytest tests/ -v

# Intent-specific tests
pytest tests/test_insert_task.py -v
pytest tests/test_delete_task.py -v

# Filter by test type
pytest tests/ -k "Extraction" -v      # Extraction only
pytest tests/ -k "IntentClassification" -v  # Classification only

# Specific test
pytest tests/test_insert_task.py::TestInsertTaskExtraction::test_extract_task_name -v
```

## Critical Implementation Details

### Intent System (6 intents)
- `show_all`, `show_done`, `show_pending`: Display queries
- `insert_task`: Extract task name via keyword removal (removes: tambah, buat, bikin, task, tugas, baru)
- `delete_task`: Extract ID via regex patterns
- `update_status`: Extract ID + status (done/pending)

**Intent Classification:**
- Uses `paraphrase-multilingual-MiniLM-L12-v2` model
- Pre-computes embeddings at initialization
- Cosine similarity with 0.45 threshold
- Returns `(intent, confidence_score)` tuple

### Parameter Extraction (sql_generator.py)

**Task Name Extraction (`insert_task`):**
- Keyword-based: removes intent keywords + filler words (untuk, yang, yaitu, adalah)
- Word boundary regex to avoid partial matches
- Returns "new task" if result is empty/too short

**Task ID Extraction (`delete_task`, `update_status`):**
- Regex patterns: `nomor \d+`, `id \d+`, `task \d+`, `ke \d+`
- Returns `None` if no ID found (triggers SQL error comment)

**SQL Injection Prevention:**
- Single quote escaping: `'` → `''`

### Knowledge Base Management

**Adding/Modifying Intents:**
1. Edit `knowledge_base.json` with new examples
2. Add SQL generation handler in `sql_generator.py`
3. Restart service (no code recompile needed)

**Example structure:**
```json
{
  "intents": {
    "intent_name": {
      "description": "What it does",
      "examples": ["example 1", "example 2", ...]
    }
  }
}
```

## Testing Philosophy

**Test Structure (per intent):**
- Extraction tests: Verify parameter extraction accuracy
- Classification tests: Verify intent detection + prevent false positives
- SQL generation tests: Verify query correctness + injection prevention

**Critical: False Positive Detection**
Intent classification tests deliberately include negative cases to catch false positives:
- "buat task review PR nomor 3" should be `insert_task`, NOT `delete_task`
- "tampilkan task nomor 5" should be `show_*`, NOT `delete_task`

When tests fail on classification, check:
1. Knowledge base needs more diverse examples
2. Threshold adjustment (default: 0.45)
3. Intent overlap in training examples

## Database Integration

**PostgreSQL Execution:**
- Generated SQL queries are automatically executed on PostgreSQL database
- Response returns actual query results, NOT the SQL query text
- Auto-commit transactions
- Connection pooling (2-10 connections) via psycopg2

**Credential Management:**
1. **Production (AWS SSM)**: Set `USE_AWS_SSM=true`
   - Fetches from AWS SSM Parameter Store: `/todo-api/db/{host,port,name,user,password}`
   - Requires IAM permissions: `ssm:GetParameters`
   - Region: configurable via `AWS_REGION` (default: ap-southeast-1)

2. **Local Development**: Set `USE_AWS_SSM=false`
   - Reads from environment variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - Template available in `.env.example`

**Error Handling:**
- `intent_error`: Intent not recognized or parameter extraction failed
- `database_error`: PostgreSQL query execution error
- `connection_error`: Database connection issues

## API Response Format

**Success Response (SELECT query):**
```json
{
  "success": true,
  "intent": "show_all",
  "confidence": 0.923,
  "data": [
    {"id": 1, "task": "belajar python", "status": "pending"},
    {"id": 2, "task": "review PR", "status": "done"}
  ],
  "rows_affected": 2,
  "input": "tampilkan semua task",
  "error": null,
  "error_type": null
}
```

**Success Response (INSERT/UPDATE/DELETE):**
```json
{
  "success": true,
  "intent": "insert_task",
  "confidence": 0.856,
  "data": null,
  "rows_affected": 1,
  "input": "buat task belajar Python",
  "error": null,
  "error_type": null
}
```

**Error Response:**
```json
{
  "success": false,
  "intent": null,
  "confidence": 0.432,
  "data": null,
  "rows_affected": 0,
  "input": "kalimat tidak jelas",
  "error": "Intent tidak dapat diidentifikasi",
  "error_type": "intent_error"
}
```

## Deployment Notes

**Docker Multi-stage Build:**
- Stage 1: Build dependencies with build-essential
- Stage 2: Copy dependencies, minimal runtime image
- Health check: `curl http://localhost:8000/health`

**Environment Variables:**
- `PYTHONUNBUFFERED=1`: Required for proper logging
- `WORKERS=1`: Single worker (heavy model in singleton)

**Resource Recommendations:**
- Memory: 2GB minimum (sentence-transformers model)
- CPU: 1.0 core minimum

## Common Pitfalls

1. **Model Loading**: Service uses Singleton pattern. Multiple instances will reload the model (memory intensive).
2. **Threshold Tuning**: 0.45 is optimized for current knowledge base. Adjust if adding significantly different intents.
3. **Word Boundaries**: Extraction uses `\b` regex. Important for avoiding "tambah" matching "tambahan".
4. **Case Sensitivity**: All extraction is case-insensitive (`.lower()` everywhere).
5. **Knowledge Base Format**: Must have `"intents"` key at root level. Service crashes on malformed JSON.
6. **Database Connection**: `DatabaseManager` also uses Singleton. Connection pool initialized once on first instantiation.
7. **AWS SSM Fallback**: If SSM fetch fails, automatically falls back to environment variables (useful for development).
8. **CLI Mode Limitation**: `cli.py` does NOT execute queries on database - only generates SQL. Use API mode for full functionality.
9. **Connection Pooling**: Pool size 2-10 connections. Don't forget to call `db_manager.close_all_connections()` on shutdown if needed.
10. **Environment Variables**: `.env` file must exist for local development. Copy from `.env.example` first.
