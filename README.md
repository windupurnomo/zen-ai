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

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
python main.py
```

## Cara Penggunaan

### Mode Demo
Saat pertama kali dijalankan, aplikasi akan menampilkan demo dengan beberapa contoh query.

### Mode Interaktif
Setelah demo, Anda bisa memasukkan perintah sendiri. Contoh:

```
Masukkan perintah: Tampilkan semua task
Masukkan perintah: Tambah task belajar Python
Masukkan perintah: Hapus task nomor 3
Masukkan perintah: Update status task 2 jadi done
```

Ketik `exit`, `quit`, atau `keluar` untuk keluar dari mode interaktif.

## Teknologi

- **sentence-transformers**: Untuk embedding kalimat (model: paraphrase-multilingual-MiniLM-L12-v2)
- **scikit-learn**: Untuk menghitung cosine similarity
- **pytest**: Untuk unit testing
- **Regular Expression**: Untuk extract parameter (task name, ID, status)

## Struktur Project

```
todo/
├── main.py                   # Aplikasi utama
├── intent_classifier.py      # Modul klasifikasi intent
├── sql_generator.py          # Modul generator SQL query
├── knowledge_base.json       # Database intent dan contoh kalimat
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_insert_task.py   # Tests untuk insert_task intent
│   └── test_delete_task.py   # Tests untuk delete_task intent
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore file
└── README.md                # Dokumentasi
```

## Arsitektur

1. **Intent Classification**:
   - Menggunakan sentence embeddings dan cosine similarity untuk mencocokkan input user dengan intent yang tersedia
   - Knowledge base disimpan dalam `knowledge_base.json` untuk kemudahan maintenance
   - Threshold similarity default: 0.45
   - Setiap intent memiliki 10-15 contoh kalimat untuk training

2. **Parameter Extraction**:
   - **Task Name**: Keyword-based extraction yang menghapus intent keywords dan filler words
   - **Task ID**: Regex pattern matching untuk extract angka ID
   - **Status**: Keyword matching untuk 'done' atau 'pending'

3. **SQL Generation**:
   - Generate query SQL berdasarkan intent dan parameter yang telah di-extract
   - SQL injection prevention dengan escaping single quotes

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
