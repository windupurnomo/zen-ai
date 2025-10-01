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
├── test_sql_generator.py     # Unit tests
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

Project ini dilengkapi dengan comprehensive unit tests untuk memastikan kualitas extraction.

```bash
# Install pytest (jika belum)
pip install pytest

# Run all tests
pytest test_sql_generator.py -v

# Run specific test
pytest test_sql_generator.py::TestSQLGeneratorInsertTask::test_extract_task_name -v
```

**Test Coverage:**
- 40+ test cases untuk `extract_task_name()`
- Mencakup: basic cases, long descriptions, edge cases, mixed language, real-world examples
- SQL generation tests dengan SQL injection prevention

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
