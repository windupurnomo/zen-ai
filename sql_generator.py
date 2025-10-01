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

        Args:
            user_input: Input dari user

        Returns:
            str: Nama task yang di-extract
        """
        # Pattern untuk extract task name
        patterns = [
            r'tambah(?:kan)?\s+task\s+(.+)',
            r'buat\s+task\s+(?:baru\s+)?(.+)',
            r'bikin\s+task\s+(.+)',
            r'tambahin\s+task\s+(.+)',
            r'insert\s+task\s+(.+)',
            r'add\s+task\s+(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                return match.group(1).strip()

        return "new task"

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
