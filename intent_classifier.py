"""
Intent Classifier Module
Menggunakan sentence embeddings untuk mencocokkan input user dengan intent yang tersedia
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import os


class IntentClassifier:
    def __init__(self, knowledge_base_path='knowledge_base.json'):
        # Load pre-trained Indonesian sentence transformer model
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

        # Load knowledge base dari file JSON
        self.intent_examples = self._load_knowledge_base(knowledge_base_path)

        # Pre-compute embeddings untuk semua contoh kalimat
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            embeddings = self.model.encode(examples)
            self.intent_embeddings[intent] = embeddings

    def _load_knowledge_base(self, kb_path: str) -> dict:
        """
        Load knowledge base dari file JSON

        Args:
            kb_path: Path ke file knowledge base JSON

        Returns:
            dict: Dictionary berisi intent dan contoh kalimat
        """
        if not os.path.exists(kb_path):
            raise FileNotFoundError(f"Knowledge base file not found: {kb_path}")

        with open(kb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract examples dari struktur JSON
        intent_examples = {}
        for intent_name, intent_data in data['intents'].items():
            intent_examples[intent_name] = intent_data['examples']

        return intent_examples

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
