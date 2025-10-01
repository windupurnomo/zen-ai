"""
Unit tests for SQLGenerator - insert_task intent
Testing extract_task_name() method dengan berbagai skenario
"""

import pytest
from sql_generator import SQLGenerator


class TestSQLGeneratorInsertTask:
    """Test cases untuk intent insert_task, khususnya extract_task_name()"""

    @pytest.fixture
    def generator(self):
        """Fixture untuk SQLGenerator instance"""
        return SQLGenerator()

    @pytest.mark.parametrize("user_input,expected_task", [
        # === BASIC CASES ===
        # Simple short task names
        ("buat task belajar", "belajar"),
        ("tambah task coding", "coding"),
        ("bikin task meeting", "meeting"),
        ("tambahkan task shopping", "shopping"),
        ("insert task olahraga", "olahraga"),
        ("add task makan", "makan"),

        # === LONG DESCRIPTIONS ===
        # Complex multi-word task descriptions
        ("buat task perbaiki error pada halaman login", "perbaiki error pada halaman login"),
        ("tambah task review code untuk fitur payment", "review code untuk fitur payment"),
        ("bikin task diskusi dengan team tentang timeline project", "diskusi dengan team tentang timeline project"),
        ("tambahkan task baca dokumentasi API", "baca dokumentasi api"),
        ("buat task implementasi fitur search dengan elasticsearch", "implementasi fitur search dengan elasticsearch"),

        # === VARIOUS INTENT KEYWORDS ===
        # Different ways to express "create task"
        ("buat task baru refactoring", "refactoring"),
        ("tambahin task debugging", "debugging"),
        ("bikin task deployment", "deployment"),
        ("insert task testing", "testing"),
        ("add task migration", "migration"),
        ("tambahkan tugas presentation", "presentation"),

        # === WITH FILLER WORDS ===
        # Task descriptions dengan kata penghubung
        ("buat task untuk perbaiki bug", "perbaiki bug"),
        ("tambah task yang urgent", "urgent"),
        ("bikin task baru untuk meeting client", "meeting client"),
        ("tambahkan task adalah review PR", "review pr"),

        # === EDGE CASES ===
        # Uppercase and mixed case
        ("BUAT TASK UPDATE DATABASE", "update database"),
        ("Tambah Task Deploy Production", "deploy production"),

        # Multiple intent keywords in sequence
        ("buat task baru tambah fitur notification", "fitur notification"),

        # Intent keyword as part of task description (should be preserved)
        ("buat task review tambahan requirements", "review tambahan requirements"),
        ("tambah task buat laporan bulanan", "laporan bulanan"),

        # Very long description
        ("buat task perbaiki error timeout pada API endpoint user authentication dengan menambahkan retry logic",
         "perbaiki error timeout pada api endpoint user authentication dengan menambahkan retry logic"),

        # === MIXED LANGUAGE ===
        # Indonesian + English mix
        ("buat task fixing bug in login page", "fixing bug in login page"),
        ("tambah task update documentation", "update documentation"),
        ("bikin task create unit test", "create unit test"),

        # === REAL-WORLD EXAMPLES ===
        # Actual user input examples
        ("buat task meeting dengan client jam 2 siang", "meeting dengan client jam 2 siang"),
        ("tambah task review code PR #123", "review code pr #123"),
        ("bikin task setup environment untuk development", "setup environment untuk development"),
        ("tambahkan task update dependencies ke versi terbaru", "update dependencies ke versi terbaru"),
        ("buat task refactor database schema users table", "refactor database schema users table"),

        # === INFORMAL / COLLOQUIAL ===
        # Casual Indonesian expressions
        ("tambahin task benerin bug login", "benerin bug login"),
        ("bikin task ngecek performa aplikasi", "ngecek performa aplikasi"),

        # === WITH TASK vs TUGAS ===
        # Using "tugas" instead of "task"
        ("buat tugas belajar python", "belajar python"),
        ("tambah tugas meeting", "meeting"),

        # === MULTIPLE SPACES / FORMATTING ISSUES ===
        # Extra whitespace
        ("buat  task   coding", "coding"),
        ("tambah task  review  code", "review code"),
    ])
    def test_extract_task_name(self, generator, user_input, expected_task):
        """
        Test extract_task_name dengan berbagai input user

        Test mencakup:
        - Basic cases dengan task name pendek
        - Long descriptions dengan banyak kata
        - Variasi intent keywords
        - Filler words di awal/tengah
        - Edge cases (uppercase, multiple keywords)
        - Mixed language (ID/EN)
        - Real-world examples
        """
        result = generator.extract_task_name(user_input)
        assert result == expected_task, f"Input: '{user_input}' | Expected: '{expected_task}' | Got: '{result}'"

    def test_extract_task_name_empty_after_removal(self, generator):
        """Test case dimana semua kata adalah intent keywords"""
        # Setelah remove semua keywords, tidak ada task name tersisa
        result = generator.extract_task_name("buat task baru")
        assert result == "new task", "Should return default when no task description remains"

    def test_extract_task_name_only_filler_words(self, generator):
        """Test case dimana hanya ada filler words setelah intent removal"""
        result = generator.extract_task_name("buat task untuk")
        assert result == "new task", "Should return default when only filler words remain"

    @pytest.mark.parametrize("user_input,expected_sql", [
        # Test full SQL generation untuk insert_task
        ("buat task belajar", "INSERT INTO todo (task, status) VALUES ('belajar', 'pending');"),
        ("tambah task review code", "INSERT INTO todo (task, status) VALUES ('review code', 'pending');"),

        # Test SQL injection prevention (single quotes)
        ("buat task review John's code", "INSERT INTO todo (task, status) VALUES ('review john''s code', 'pending');"),
    ])
    def test_generate_insert_task_sql(self, generator, user_input, expected_sql):
        """Test generate() method untuk intent insert_task"""
        result = generator.generate('insert_task', user_input)
        assert result == expected_sql, f"SQL mismatch for input: '{user_input}'"


if __name__ == "__main__":
    # Untuk run test langsung dengan python
    pytest.main([__file__, "-v"])
