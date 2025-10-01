"""
NL2SQL Service Layer
Refactored business logic untuk digunakan oleh CLI dan API
"""

from typing import Tuple, Optional
from intent_classifier import IntentClassifier
from sql_generator import SQLGenerator


class NL2SQLService:
    """
    Service class untuk Natural Language to SQL conversion

    Singleton pattern untuk menghindari multiple model loading
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NL2SQLService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize classifier and generator (only once)"""
        if not NL2SQLService._initialized:
            print("Initializing NL2SQL Service...")
            print("Loading sentence transformer model...")
            self.classifier = IntentClassifier()
            self.generator = SQLGenerator()
            NL2SQLService._initialized = True
            print("Service ready!")

    def process(self, user_input: str) -> dict:
        """
        Process natural language input dan generate SQL query

        Args:
            user_input: Kalimat dalam bahasa Indonesia

        Returns:
            dict: Result dictionary dengan format:
                {
                    'success': bool,
                    'intent': str | None,
                    'confidence': float,
                    'sql_query': str | None,
                    'input': str,
                    'error': str | None
                }
        """
        # Klasifikasi intent
        intent, score = self.classifier.classify(user_input)

        if intent is None:
            return {
                'success': False,
                'intent': None,
                'confidence': round(score, 3),
                'sql_query': None,
                'input': user_input,
                'error': 'Intent tidak dapat diidentifikasi'
            }

        # Generate SQL query
        sql_query = self.generator.generate(intent, user_input)

        # Check if SQL generation has error
        is_error = sql_query.startswith('-- Error:')

        return {
            'success': not is_error,
            'intent': intent,
            'confidence': round(score, 3),
            'sql_query': sql_query if not is_error else None,
            'input': user_input,
            'error': sql_query.replace('-- Error: ', '') if is_error else None
        }

    def get_supported_intents(self) -> list:
        """
        Get list of supported intents

        Returns:
            list: List of intent names
        """
        return list(self.classifier.intent_examples.keys())
