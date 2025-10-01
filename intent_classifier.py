"""
Intent Classifier Module
Menggunakan sentence embeddings untuk mencocokkan input user dengan intent yang tersedia
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class IntentClassifier:
    def __init__(self):
        # Load pre-trained Indonesian sentence transformer model
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

        # Definisi intent dan contoh kalimat untuk setiap intent
        self.intent_examples = {
            'show_all': [
                'Tampilkan semua task',
                'Lihat semua tugas',
                'Show semua todo',
                'Tampilkan seluruh daftar',
                'Mau lihat semua',
                'Tampilkan list todo'
            ],
            'show_done': [
                'Tampilkan task yang sudah selesai',
                'Lihat tugas yang done',
                'Show task selesai',
                'Tampilkan yang sudah dikerjakan',
                'Mau lihat yang sudah selesai',
                'Task apa saja yang sudah done'
            ],
            'show_pending': [
                'Tampilkan task yang belum selesai',
                'Lihat tugas pending',
                'Show task yang belum dikerjakan',
                'Tampilkan yang belum selesai',
                'Mau lihat yang pending',
                'Task apa yang masih pending'
            ],
            'insert_task': [
                'Tambah task belajar',
                'Buat task baru coding',
                'Tambahkan tugas meeting',
                'Insert task shopping',
                'Bikin task olahraga',
                'Tambahin task makan'
            ],
            'delete_task': [
                'Hapus task nomor 3',
                'Delete task id 5',
                'Hapus tugas nomor 2',
                'Remove task 1',
                'Buang task nomor 4',
                'Hapus task yang ke 6'
            ],
            'update_status': [
                'Update status task 3 jadi done',
                'Ubah status nomor 2 jadi selesai',
                'Ganti status task 5 pending',
                'Set status task 1 done',
                'Tandai task 4 sudah selesai',
                'Update task 2 jadi pending'
            ]
        }

        # Pre-compute embeddings untuk semua contoh kalimat
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            embeddings = self.model.encode(examples)
            self.intent_embeddings[intent] = embeddings

    def classify(self, user_input: str, threshold: float = 0.5):
        """
        Klasifikasi intent dari input user

        Args:
            user_input: Kalimat input dari user
            threshold: Threshold similarity (default 0.5)

        Returns:
            tuple: (intent_name, similarity_score)
        """
        # Encode user input
        user_embedding = self.model.encode([user_input])

        # Hitung similarity dengan semua intent
        best_intent = None
        best_score = 0.0

        for intent, intent_embs in self.intent_embeddings.items():
            # Hitung cosine similarity dengan semua contoh dari intent ini
            similarities = cosine_similarity(user_embedding, intent_embs)[0]

            # Ambil similarity tertinggi
            max_similarity = np.max(similarities)

            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent

        # Return intent jika score di atas threshold
        if best_score >= threshold:
            return best_intent, best_score
        else:
            return None, best_score
