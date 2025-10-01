"""
SQL Query Generator Module
Menghasilkan query SQL berdasarkan intent dan parameter yang di-extract dari input user
"""

import re


class SQLGenerator:
    def __init__(self):
        pass

    def extract_task_name(self, user_input: str) -> str:
        """
        Extract nama task dari kalimat input untuk intent insert_task

        Menggunakan keyword-based extraction: remove semua intent keywords
        dan filler words, sisanya adalah task description.

        Args:
            user_input: Input dari user

        Returns:
            str: Nama task yang di-extract

        Examples:
            "buat task perbaiki error login" -> "perbaiki error login"
            "tambahkan task baru review code" -> "review code"
            "bikin task diskusi dengan team" -> "diskusi dengan team"
        """
        # Daftar intent keywords yang harus di-remove
        intent_keywords = [
            'tambah', 'tambahkan', 'buat', 'bikin', 'tambahin',
            'insert', 'add', 'task', 'tugas', 'baru', 'new'
        ]

        # Convert ke lowercase untuk processing
        text = user_input.lower()

        # Remove semua intent keywords
        for keyword in intent_keywords:
            # Remove keyword dengan word boundary untuk avoid partial match
            # Contoh: "tambah" tidak akan remove "tambahan"
            text = re.sub(r'\b' + re.escape(keyword) + r'\b', '', text, flags=re.IGNORECASE)

        # Clean up: remove extra whitespace dan strip
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove filler words (di awal atau standalone)
        filler_words = ['untuk', 'yang', 'yaitu', 'adalah']
        for filler in filler_words:
            # Remove di awal kalimat dengan spasi setelahnya
            if text.startswith(filler + ' '):
                text = text[len(filler):].strip()
            # Remove jika hanya filler word saja (standalone)
            elif text == filler:
                text = ''

        # Jika hasilnya kosong atau terlalu pendek, return default
        if not text or len(text) < 2:
            return "new task"

        return text

    def extract_task_id(self, user_input: str) -> int:
        """
        Extract ID task dari kalimat input

        Args:
            user_input: Input dari user

        Returns:
            int: ID task yang di-extract (atau None jika tidak ditemukan)
        """
        # Pattern untuk extract ID
        patterns = [
            r'nomor\s+(\d+)',
            r'id\s+(\d+)',
            r'task\s+(\d+)',
            r'ke\s+(\d+)',
            r'yang\s+(\d+)',
            r'\s(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                return int(match.group(1))

        return None

    def extract_status(self, user_input: str) -> str:
        """
        Extract status dari kalimat input untuk intent update_status

        Args:
            user_input: Input dari user

        Returns:
            str: Status ('done' atau 'pending')
        """
        user_input_lower = user_input.lower()

        # Check untuk status 'done'
        done_keywords = ['done', 'selesai', 'sudah selesai', 'finish', 'completed']
        for keyword in done_keywords:
            if keyword in user_input_lower:
                return 'done'

        # Check untuk status 'pending'
        pending_keywords = ['pending', 'belum selesai', 'belum', 'not done']
        for keyword in pending_keywords:
            if keyword in user_input_lower:
                return 'pending'

        return 'pending'  # Default

    def generate(self, intent: str, user_input: str) -> str:
        """
        Generate SQL query berdasarkan intent dan user input

        Args:
            intent: Intent yang terdeteksi
            user_input: Input asli dari user

        Returns:
            str: SQL query
        """
        if intent == 'show_all':
            return "SELECT * FROM todo;"

        elif intent == 'show_done':
            return "SELECT * FROM todo WHERE status='done';"

        elif intent == 'show_pending':
            return "SELECT * FROM todo WHERE status='pending';"

        elif intent == 'insert_task':
            task_name = self.extract_task_name(user_input)
            # Escape single quotes untuk SQL
            task_name = task_name.replace("'", "''")
            return f"INSERT INTO todo (task, status) VALUES ('{task_name}', 'pending');"

        elif intent == 'delete_task':
            task_id = self.extract_task_id(user_input)
            if task_id is not None:
                return f"DELETE FROM todo WHERE id={task_id};"
            else:
                return "-- Error: ID task tidak ditemukan"

        elif intent == 'update_status':
            task_id = self.extract_task_id(user_input)
            status = self.extract_status(user_input)
            if task_id is not None:
                return f"UPDATE todo SET status='{status}' WHERE id={task_id};"
            else:
                return "-- Error: ID task tidak ditemukan"

        else:
            return "-- Error: Intent tidak dikenali"
