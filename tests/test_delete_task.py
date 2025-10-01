"""
Unit tests for delete_task intent
Testing extract_task_id() method dan intent classification
"""

import pytest
from sql_generator import SQLGenerator


class TestDeleteTaskExtraction:
    """Test cases untuk delete_task intent - extraction dan false positive prevention"""

    @pytest.fixture
    def generator(self):
        """Fixture untuk SQLGenerator instance"""
        return SQLGenerator()

    @pytest.mark.parametrize("user_input,expected_id", [
        # === BASIC CASES ===
        # Simple delete commands dengan berbagai format
        ("hapus task nomor 3", 3),
        ("delete task id 5", 5),
        ("hapus tugas nomor 2", 2),
        ("remove task 1", 1),
        ("buang task nomor 4", 4),
        ("hapus task yang ke 6", 6),

        # === VARIOUS KEYWORDS ===
        # Different ways to express "delete"
        ("apus task 7", 7),
        ("hapusin task nomor 8", 8),
        ("delete tugas yang ke 9", 9),
        ("hilangkan task id 10", 10),
        ("buang tugas nomor 11", 11),

        # === INFORMAL / COLLOQUIAL ===
        # Casual expressions
        ("hapusin task 15", 15),
        ("buangin task nomor 20", 20),

        # === WITH EXTRA WORDS ===
        # Delete commands dengan kata tambahan
        ("hapus task nomor 3 yang sudah selesai", 3),
        ("delete task id 5 karena duplikat", 5),
        ("hapus tugas nomor 2 dong", 2),

        # === EDGE CASES ===
        # Uppercase and mixed case
        ("HAPUS TASK NOMOR 12", 12),
        ("Hapus Task ID 13", 13),

        # Multiple spaces
        ("hapus  task   nomor   14", 14),

        # Large ID numbers
        ("hapus task nomor 999", 999),
        ("delete task id 12345", 12345),
    ])
    def test_extract_task_id(self, generator, user_input, expected_id):
        """
        Test extract_task_id dengan berbagai format delete command

        Test mencakup:
        - Basic delete commands
        - Various delete keywords
        - Informal/colloquial expressions
        - Extra words after ID
        - Edge cases (uppercase, multiple spaces, large IDs)
        """
        result = generator.extract_task_id(user_input)
        assert result == expected_id, f"Input: '{user_input}' | Expected ID: {expected_id} | Got: {result}"

    @pytest.mark.parametrize("user_input", [
        # === FALSE POSITIVE PREVENTION ===
        # Kalimat yang mengandung angka tapi BUKAN delete intent

        # Insert task dengan angka dalam deskripsi
        "buat task review PR nomor 3",
        "tambah task meeting ruangan 5",
        "bikin task belajar chapter 2",
        "tambahkan task sprint 3 planning",

        # Update status dengan ID (ini update, bukan delete)
        "update status task 3 jadi done",
        "ubah status nomor 2 jadi selesai",

        # Show commands dengan filter
        "tampilkan task nomor 5",
        "lihat detail task 3",

        # General statements dengan angka
        "ada 5 task yang harus dikerjakan",
        "hari ini ada 3 meeting",
        "total 10 task pending",
    ])
    def test_extract_task_id_should_still_extract(self, generator, user_input):
        """
        Test bahwa extract_task_id tetap bisa extract ID meskipun dari non-delete intent

        Ini testing method extract_task_id() saja, bukan intent classification.
        Intent classifier yang akan menentukan apakah ini benar-benar delete atau bukan.
        """
        result = generator.extract_task_id(user_input)
        # Method ini akan extract ID jika ada, terlepas dari intent
        assert result is not None, f"Should extract ID from: '{user_input}'"
        assert isinstance(result, int), f"Should return integer ID"

    def test_extract_task_id_no_id(self, generator):
        """Test case dimana tidak ada ID dalam input"""
        result = generator.extract_task_id("hapus semua task")
        assert result is None, "Should return None when no ID found"

    @pytest.mark.parametrize("user_input,expected_sql", [
        # Test full SQL generation untuk delete_task
        ("hapus task nomor 3", "DELETE FROM todo WHERE id=3;"),
        ("delete task id 5", "DELETE FROM todo WHERE id=5;"),
        ("buang tugas nomor 10", "DELETE FROM todo WHERE id=10;"),

        # Large ID
        ("hapus task nomor 999", "DELETE FROM todo WHERE id=999;"),
    ])
    def test_generate_delete_task_sql(self, generator, user_input, expected_sql):
        """Test generate() method untuk intent delete_task"""
        result = generator.generate('delete_task', user_input)
        assert result == expected_sql, f"SQL mismatch for input: '{user_input}'"

    def test_generate_delete_task_no_id(self, generator):
        """Test generate() method ketika ID tidak ditemukan"""
        result = generator.generate('delete_task', "hapus semua task")
        assert result == "-- Error: ID task tidak ditemukan", "Should return error when no ID"


class TestDeleteTaskIntentClassification:
    """Test untuk memastikan intent delete_task tidak false positive"""

    @pytest.fixture
    def classifier(self):
        """Fixture untuk IntentClassifier instance"""
        from intent_classifier import IntentClassifier
        return IntentClassifier()

    @pytest.mark.parametrize("user_input,should_be_delete", [
        # === TRUE DELETE INTENTS ===
        ("hapus task nomor 3", True),
        ("delete task id 5", True),
        ("buang tugas nomor 2", True),
        ("hapusin task 7", True),
        ("remove task 10", True),
        ("hilangkan task nomor 15", True),

        # === FALSE POSITIVES - Should NOT be delete ===
        # Insert task dengan nomor dalam deskripsi
        ("buat task review PR nomor 3", False),
        ("tambah task meeting ruangan 5", False),
        ("bikin task belajar chapter 2", False),
        ("tambahkan task sprint 3 planning", False),

        # Update task
        ("update status task 3 jadi done", False),
        ("ubah task 2 jadi selesai", False),
        ("ganti status task 5 pending", False),

        # Show commands
        ("tampilkan task nomor 5", False),
        ("lihat detail task 3", False),
        ("lihat semua task", False),
        ("tampilkan task yang sudah selesai", False),

        # General statements
        ("ada task nomor 5 yang urgent", False),
        ("cek task 3", False),
    ])
    def test_delete_task_intent_classification(self, classifier, user_input, should_be_delete):
        """
        Test bahwa intent classifier dapat membedakan delete_task dari intent lain

        Ini adalah test krusial untuk mencegah false positive dimana:
        - "buat task review PR nomor 3" tidak terdeteksi sebagai delete
        - "tampilkan task nomor 5" tidak terdeteksi sebagai delete
        - Hanya perintah delete yang jelas yang terdeteksi sebagai delete_task
        """
        intent, score = classifier.classify(user_input)

        if should_be_delete:
            assert intent == 'delete_task', (
                f"Input: '{user_input}' should be classified as delete_task, "
                f"but got '{intent}' with score {score:.3f}"
            )
        else:
            assert intent != 'delete_task', (
                f"Input: '{user_input}' should NOT be classified as delete_task, "
                f"but got '{intent}' with score {score:.3f}"
            )


if __name__ == "__main__":
    # Untuk run test langsung dengan python
    pytest.main([__file__, "-v"])
