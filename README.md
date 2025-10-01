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
- **Regular Expression**: Untuk extract parameter (task name, ID, status)

## Struktur Project

```
todo/
├── main.py                 # Aplikasi utama
├── intent_classifier.py    # Modul klasifikasi intent
├── sql_generator.py        # Modul generator SQL query
├── requirements.txt        # Dependencies
└── README.md              # Dokumentasi
```

## Arsitektur

1. **Intent Classification**: Menggunakan sentence embeddings dan cosine similarity untuk mencocokkan input user dengan intent yang tersedia
2. **Parameter Extraction**: Menggunakan regular expression untuk extract parameter seperti task name, ID, dan status
3. **SQL Generation**: Generate query SQL berdasarkan intent dan parameter yang telah di-extract
