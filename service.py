"""
NL2SQL Service Layer
Refactored business logic untuk digunakan oleh CLI dan API
"""

from typing import Tuple, Optional
from intent_classifier import IntentClassifier
from sql_generator import SQLGenerator
from db import DatabaseManager
import logging

logger = logging.getLogger(__name__)


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
        """Initialize classifier, generator, and database manager (only once)"""
        if not NL2SQLService._initialized:
            print("Initializing NL2SQL Service...")
            print("Loading sentence transformer model...")
            self.classifier = IntentClassifier()
            self.generator = SQLGenerator()
            self.db_manager = DatabaseManager()
            NL2SQLService._initialized = True
            print("Service ready!")

    def process(self, user_input: str) -> dict:
        """
        Process natural language input, generate SQL query, and execute on database

        Args:
            user_input: Kalimat dalam bahasa Indonesia

        Returns:
            dict: Result dictionary dengan format:
                {
                    'success': bool,
                    'intent': str | None,
                    'confidence': float,
                    'data': List[Dict] | None,
                    'rows_affected': int,
                    'input': str,
                    'error': str | None,
                    'error_type': str | None
                }
        """
        # Klasifikasi intent
        intent, score = self.classifier.classify(user_input)

        if intent is None:
            return {
                'success': False,
                'intent': None,
                'confidence': round(score, 3),
                'data': None,
                'rows_affected': 0,
                'input': user_input,
                'error': 'Intent tidak dapat diidentifikasi',
                'error_type': 'intent_error'
            }

        # Generate SQL query
        sql_query = self.generator.generate(intent, user_input)

        # Check if SQL generation has error
        is_error = sql_query.startswith('-- Error:')

        if is_error:
            return {
                'success': False,
                'intent': intent,
                'confidence': round(score, 3),
                'data': None,
                'rows_affected': 0,
                'input': user_input,
                'error': sql_query.replace('-- Error: ', ''),
                'error_type': 'intent_error'
            }

        # Execute query on database
        logger.info(f"Executing SQL: {sql_query}")
        db_result = self.db_manager.execute_query(sql_query)

        # Return combined result
        return {
            'success': db_result['success'],
            'intent': intent,
            'confidence': round(score, 3),
            'data': db_result['data'],
            'rows_affected': db_result['rows_affected'],
            'input': user_input,
            'error': db_result['error'],
            'error_type': db_result['error_type']
        }

    def get_supported_intents(self) -> list:
        """
        Get list of supported intents

        Returns:
            list: List of intent names
        """
        return list(self.classifier.intent_examples.keys())
