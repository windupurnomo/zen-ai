# Natural Language to SQL Query (Bahasa Indonesia)

Project Python untuk mengubah perintah Natural Language dalam bahasa Indonesia menjadi query SQL untuk tabel todo.

## Struktur Tabel

```sql
CREATE TABLE todo (
    id INTEGER PRIMARY KEY,
    task TEXT NOT NULL,
    status TEXT NOT NULL
);
```

## Fitur

Project ini mendukung 6 intent utama:

1. **show_all** - Menampilkan semua task
2. **show_done** - Menampilkan task yang sudah selesai
3. **show_pending** - Menampilkan task yang belum selesai
4. **insert_task** - Menambah task baru
5. **delete_task** - Menghapus task berdasarkan ID
6. **update_status** - Mengubah status task

## Instalasi & Deployment

### Prerequisites

**Database Setup:**
- PostgreSQL database (remote atau local)
- AWS account dengan AWS SSM Parameter Store (untuk production)
- AWS credentials configured (via AWS CLI atau environment variables)

**Environment Configuration:**
```bash
# Copy template environment file
cp .env.example .env

# Edit .env dan sesuaikan dengan konfigurasi Anda
# - Untuk production: Set USE_AWS_SSM=true dan configure AWS SSM parameter names
# - Untuk local dev: Set USE_AWS_SSM=false dan isi DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
```

### Option 1: Docker (Recommended for Production)

**Prerequisites:**
- Docker & Docker Compose installed
- PostgreSQL database sudah running
- AWS SSM parameters sudah configured (jika USE_AWS_SSM=true)

**Quick Start:**
```bash
# Build dan run dengan docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop container
docker-compose down
```

**Manual Docker Commands:**
```bash
# Build image
docker build -t nl2sql-api .

# Run container
docker run -d \
  --name nl2sql-api \
  -p 8000:8000 \
  nl2sql-api

# Check health
docker ps
curl http://localhost:8000/health
```

**Production Deployment:**
```bash
# Build untuk production
docker build -t nl2sql-api:latest .

# Run dengan custom configuration
docker run -d \
  --name nl2sql-api \
  -p 8000:8000 \
  --restart unless-stopped \
  --memory="2g" \
  --cpus="1.0" \
  nl2sql-api:latest
```

### Option 2: Local Development

**Prerequisites:**
- Python 3.11+
- PostgreSQL database running (local atau remote)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Setup environment:**
```bash
# Copy dan edit environment file
cp .env.example .env

# Edit .env untuk local development:
# USE_AWS_SSM=false
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=todo_db
# DB_USER=postgres
# DB_PASSWORD=your_password
```

## Cara Penggunaan

Project ini dapat dijalankan dalam 3 mode:

### 1. REST API Mode (Recommended)

**Menjalankan API Server:**
```bash
# Jalankan dengan uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Atau jalankan langsung
python api.py
```

**Akses API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Test API dengan curl:**
```bash
# POST request untuk convert NL to SQL
curl -X POST http://localhost:8000/api/v1/nl2sql \
  -H "Content-Type: application/json" \
  -d '{"message": "buat task belajar Python"}'

# GET health check
curl http://localhost:8000/health

# GET supported intents
curl http://localhost:8000/api/v1/intents
```

**Contoh Response:**

**SELECT Query (show_all, show_done, show_pending):**
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

**INSERT/UPDATE/DELETE Query:**
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

### 2. CLI Mode (Command Line Interface)

**Jalankan CLI:**
```bash
python cli.py
```

**Mode Demo:**
Saat pertama kali dijalankan, aplikasi akan menampilkan demo dengan beberapa contoh query.

**Mode Interaktif:**
Setelah demo, Anda bisa memasukkan perintah sendiri. Contoh:

```
Masukkan perintah: Tampilkan semua task
Masukkan perintah: Tambah task belajar Python
Masukkan perintah: Hapus task nomor 3
Masukkan perintah: Update status task 2 jadi done
```

Ketik `exit`, `quit`, atau `keluar` untuk keluar dari mode interaktif.

## Teknologi

- **FastAPI**: Modern, fast web framework untuk building APIs
- **Uvicorn**: ASGI server untuk production-ready deployment
- **Pydantic**: Data validation dan settings management
- **sentence-transformers**: Untuk embedding kalimat (model: paraphrase-multilingual-MiniLM-L12-v2)
- **scikit-learn**: Untuk menghitung cosine similarity
- **pytest**: Untuk unit testing
- **Regular Expression**: Untuk extract parameter (task name, ID, status)
- **PostgreSQL**: Database untuk menyimpan todo tasks
- **psycopg2**: PostgreSQL adapter untuk Python
- **boto3**: AWS SDK untuk Python (AWS SSM integration)
- **python-dotenv**: Environment variable management

## Struktur Project

```
todo/
├── api.py                    # FastAPI application (REST API)
├── cli.py                    # Command Line Interface
├── service.py                # Business logic service layer
├── schemas.py                # Pydantic models untuk request/response
├── intent_classifier.py      # Modul klasifikasi intent
├── sql_generator.py          # Modul generator SQL query
├── db.py                     # Database manager dengan AWS SSM integration
├── knowledge_base.json       # Database intent dan contoh kalimat
├── .env.example              # Template environment variables
├── Dockerfile                # Docker container configuration
├── docker-compose.yml        # Docker Compose setup
├── .dockerignore            # Docker ignore file
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_insert_task.py   # Tests untuk insert_task intent
│   └── test_delete_task.py   # Tests untuk delete_task intent
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore file
└── README.md                # Dokumentasi
```

## Arsitektur

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         API Layer (api.py)              │  <- FastAPI endpoints
│  - POST /api/v1/nl2sql                  │
│  - GET  /health                         │
│  - GET  /api/v1/intents                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Service Layer (service.py)         │  <- Business logic
│  - NL2SQLService (Singleton)            │
│  - process() method                     │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┬──────────────┐
        │                   │              │
┌───────▼──────┐   ┌────────▼────────┐   ┌▼───────────────┐
│ IntentClass  │   │  SQLGenerator   │   │ DatabaseMgr    │
│ ifier        │   │                 │   │ (Singleton)    │
└──────────────┘   └─────────────────┘   └────────┬───────┘
                                                   │
                                         ┌─────────▼─────────┐
                                         │   PostgreSQL DB   │
                                         │   (Remote/Local)  │
                                         └───────────────────┘
```

### Komponen:

1. **API Layer** (`api.py`):
   - FastAPI application dengan REST endpoints
   - Request/response validation dengan Pydantic
   - CORS middleware untuk frontend integration
   - Error handling dan logging

2. **Service Layer** (`service.py`):
   - Business logic layer (Singleton pattern)
   - Orchestrates intent classification dan SQL generation
   - Returns structured response dict

3. **Intent Classification** (`intent_classifier.py`):
   - Sentence embeddings dan cosine similarity
   - Knowledge base dari `knowledge_base.json`
   - Threshold similarity default: 0.45
   - 10-15 contoh kalimat per intent

4. **Parameter Extraction & SQL Generation** (`sql_generator.py`):
   - **Task Name**: Keyword-based extraction
   - **Task ID**: Regex pattern matching
   - **Status**: Keyword matching
   - SQL injection prevention

5. **Database Manager** (`db.py`):
   - PostgreSQL connection pooling (2-10 connections)
   - AWS SSM Parameter Store integration
   - Fallback to environment variables
   - Query execution dengan error handling
   - Auto-commit transactions
   - Returns structured response: `{'success', 'data', 'rows_affected', 'error', 'error_type'}`

6. **Data Models** (`schemas.py`):
   - Pydantic models untuk type safety
   - Auto-generated API documentation

## Testing

Project ini dilengkapi dengan comprehensive unit tests untuk memastikan kualitas extraction dan mencegah false positive pada intent classification.

### Instalasi Testing Tools

```bash
pip install pytest
```

### Cara Menjalankan Tests

**1. Run All Tests**
```bash
pytest tests/ -v
```

**2. Test Per Intent**

**Insert Task Intent:**
```bash
# Run semua tests insert_task
pytest tests/test_insert_task.py -v

# Test extraction task name saja
pytest tests/test_insert_task.py::TestInsertTaskExtraction -v

# Test intent classification saja
pytest tests/test_insert_task.py::TestInsertTaskIntentClassification -v

# Test specific case
pytest tests/test_insert_task.py::TestInsertTaskExtraction::test_extract_task_name -v
```

**Delete Task Intent:**
```bash
# Run semua tests delete_task
pytest tests/test_delete_task.py -v

# Test extraction task ID saja
pytest tests/test_delete_task.py::TestDeleteTaskExtraction -v

# Test intent classification saja (mencegah false positive)
pytest tests/test_delete_task.py::TestDeleteTaskIntentClassification -v

# Test specific case
pytest tests/test_delete_task.py::TestDeleteTaskExtraction::test_extract_task_id -v
```

**3. Run Tests dengan Filter**
```bash
# Run hanya extraction tests (tanpa intent classification)
pytest tests/ -k "Extraction" -v

# Run hanya intent classification tests
pytest tests/ -k "IntentClassification" -v

# Run tests dengan quiet mode
pytest tests/ -q

# Run dengan summary
pytest tests/ --tb=short
```

### Test Coverage

**test_insert_task.py** (57 tests):
- ✅ **Extraction Tests (49 tests)**:
  - 46 tests `extract_task_name()` dengan berbagai skenario:
    - Basic cases (task name pendek)
    - Long descriptions (deskripsi kompleks)
    - Various keywords (tambah, buat, bikin, insert, add)
    - Filler words (untuk, yang, yaitu)
    - Edge cases (uppercase, multiple spaces, multiple keywords)
    - Mixed language (Indonesian + English)
    - Real-world examples
  - 2 tests edge cases (empty result, only filler words)
  - 3 tests SQL generation dengan SQL injection prevention

- ✅ **Intent Classification Tests (6 tests)**:
  - Memastikan input insert terdeteksi dengan benar
  - Mencegah false positive (hapus/update tidak terdeteksi sebagai insert)

**test_delete_task.py** (57 tests):
- ✅ **Extraction Tests (38 tests)**:
  - 21 tests `extract_task_id()` dari berbagai format:
    - Basic delete commands
    - Various delete keywords (hapus, delete, remove, buang, hilangkan)
    - Informal expressions (hapusin, buangin)
    - Extra words after ID
    - Edge cases (uppercase, spaces, large IDs)
  - 11 tests false positive awareness (masih extract ID dari non-delete intent)
  - 1 test no ID found
  - 5 tests SQL generation dan error handling

- ✅ **Intent Classification Tests (19 tests)**:
  - Memastikan delete commands terdeteksi dengan benar
  - **Krusial**: Mencegah false positives seperti:
    - "buat task review PR nomor 3" → BUKAN delete
    - "tampilkan task nomor 5" → BUKAN delete
    - "update status task 3 jadi done" → BUKAN delete

### Interpretasi Hasil Test

**✅ All Passed**: Extraction dan classification berjalan sempurna

**❌ Failed pada Intent Classification**: Kemungkinan causes:
- Knowledge base perlu diperkaya dengan lebih banyak contoh
- Ada overlap similarity antar intent
- Threshold perlu disesuaikan

**Contoh Output:**
```
FAILED test_delete_task.py::...::test_delete_task_intent_classification[buat task review PR nomor 3-False]
AssertionError: Input: 'buat task review PR nomor 3' should NOT be classified as delete_task,
but got 'delete_task' with score 0.782
```

Ini menandakan ada **false positive** yang perlu diperbaiki di knowledge base.

## AWS SSM Parameter Store Setup

Untuk production deployment dengan AWS SSM:

**1. Create SSM Parameters di AWS Console atau AWS CLI:**

```bash
# Host
aws ssm put-parameter \
    --name "/todo-api/db/host" \
    --value "your-db-host.amazonaws.com" \
    --type "String"

# Port
aws ssm put-parameter \
    --name "/todo-api/db/port" \
    --value "5432" \
    --type "String"

# Database Name
aws ssm put-parameter \
    --name "/todo-api/db/name" \
    --value "todo_db" \
    --type "String"

# Username
aws ssm put-parameter \
    --name "/todo-api/db/user" \
    --value "postgres" \
    --type "String"

# Password (encrypted)
aws ssm put-parameter \
    --name "/todo-api/db/password" \
    --value "your-secure-password" \
    --type "SecureString"
```

**2. Configure IAM Permissions:**

Pastikan IAM role atau user yang digunakan memiliki permission:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters",
        "ssm:GetParameter"
      ],
      "Resource": "arn:aws:ssm:ap-southeast-1:*:parameter/todo-api/db/*"
    }
  ]
}
```

**3. Set Environment Variables:**

```bash
USE_AWS_SSM=true
AWS_REGION=ap-southeast-1
DB_HOST_PARAM=/todo-api/db/host
DB_PORT_PARAM=/todo-api/db/port
DB_NAME_PARAM=/todo-api/db/name
DB_USER_PARAM=/todo-api/db/user
DB_PASSWORD_PARAM=/todo-api/db/password
```

## Menambah/Mengubah Intent

Untuk menambah atau mengubah intent, cukup edit file `knowledge_base.json`:

```json
{
  "intents": {
    "new_intent": {
      "description": "Deskripsi intent baru",
      "examples": [
        "Contoh kalimat 1",
        "Contoh kalimat 2",
        ...
      ]
    }
  }
}
```

Kemudian tambahkan handler di `sql_generator.py` untuk intent baru tersebut. Restart aplikasi untuk memuat perubahan.
