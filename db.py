"""
Database Manager with AWS SSM Integration
Handles PostgreSQL connection and query execution with credentials from AWS SSM
"""

import os
import logging
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import psycopg2
from psycopg2 import pool, Error as PostgresError
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages PostgreSQL database connections with AWS SSM credential management

    Uses connection pooling for better performance and handles automatic
    credential fetching from AWS Systems Manager Parameter Store.
    """

    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize database manager with connection pool"""
        if DatabaseManager._connection_pool is None:
            logger.info("Initializing Database Manager...")
            self._initialize_pool()

    def _get_credentials_from_ssm(self) -> Dict[str, str]:
        """
        Fetch database credentials from AWS SSM Parameter Store

        Returns:
            Dict with db_host, db_port, db_name, db_user, db_password

        Raises:
            Exception: If SSM fetch fails or parameters not found
        """
        try:
            aws_region = os.getenv('AWS_REGION', 'ap-southeast-1')

            # SSM parameter names from environment
            param_names = {
                'db_host': os.getenv('DB_HOST_PARAM', '/todo-api/db/host'),
                'db_port': os.getenv('DB_PORT_PARAM', '/todo-api/db/port'),
                'db_name': os.getenv('DB_NAME_PARAM', '/todo-api/db/name'),
                'db_user': os.getenv('DB_USER_PARAM', '/todo-api/db/user'),
                'db_password': os.getenv('DB_PASSWORD_PARAM', '/todo-api/db/password'),
            }

            logger.info(f"Fetching credentials from AWS SSM in region {aws_region}")

            # Create SSM client
            ssm = boto3.client('ssm', region_name=aws_region)

            # Fetch all parameters
            response = ssm.get_parameters(
                Names=list(param_names.values()),
                WithDecryption=True
            )

            if not response['Parameters']:
                raise ValueError("No parameters found in SSM")

            # Map parameters to credentials
            params_dict = {p['Name']: p['Value'] for p in response['Parameters']}

            credentials = {
                'db_host': params_dict.get(param_names['db_host']),
                'db_port': params_dict.get(param_names['db_port'], '5432'),
                'db_name': params_dict.get(param_names['db_name']),
                'db_user': params_dict.get(param_names['db_user']),
                'db_password': params_dict.get(param_names['db_password']),
            }

            # Validate all credentials exist
            missing = [k for k, v in credentials.items() if not v]
            if missing:
                raise ValueError(f"Missing SSM parameters: {', '.join(missing)}")

            logger.info("Successfully fetched credentials from AWS SSM")
            return credentials

        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS SSM error: {str(e)}")
            raise Exception(f"Failed to fetch credentials from AWS SSM: {str(e)}")

    def _get_credentials_from_env(self) -> Dict[str, str]:
        """
        Fallback: Get database credentials from environment variables
        Used for local development without AWS SSM

        Returns:
            Dict with db_host, db_port, db_name, db_user, db_password
        """
        credentials = {
            'db_host': os.getenv('DB_HOST'),
            'db_port': os.getenv('DB_PORT', '5432'),
            'db_name': os.getenv('DB_NAME'),
            'db_user': os.getenv('DB_USER'),
            'db_password': os.getenv('DB_PASSWORD'),
        }

        missing = [k for k, v in credentials.items() if not v]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

        logger.info("Using credentials from environment variables")
        return credentials

    def _initialize_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            # Try AWS SSM first, fallback to env vars
            use_ssm = os.getenv('USE_AWS_SSM', 'true').lower() == 'true'

            if use_ssm:
                try:
                    creds = self._get_credentials_from_ssm()
                except Exception as e:
                    logger.warning(f"SSM fetch failed, falling back to env vars: {str(e)}")
                    creds = self._get_credentials_from_env()
            else:
                creds = self._get_credentials_from_env()

            # Create connection pool
            DatabaseManager._connection_pool = pool.SimpleConnectionPool(
                minconn=2,
                maxconn=10,
                host=creds['db_host'],
                port=creds['db_port'],
                database=creds['db_name'],
                user=creds['db_user'],
                password=creds['db_password'],
                connect_timeout=30
            )

            logger.info("Database connection pool initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database pool: {str(e)}")
            raise

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute SQL query on PostgreSQL database

        Args:
            sql_query: SQL query string to execute

        Returns:
            Dict with:
                - success: bool
                - data: List[Dict] for SELECT, None for others
                - rows_affected: int
                - error: str if failed, None if success
                - error_type: str ('database_error', 'connection_error')
        """
        connection = None
        cursor = None

        try:
            # Get connection from pool
            connection = DatabaseManager._connection_pool.getconn()

            if connection is None:
                raise Exception("Failed to get connection from pool")

            # Create cursor with dictionary output
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Execute query
            cursor.execute(sql_query)

            # Determine if SELECT query
            is_select = sql_query.strip().upper().startswith('SELECT')

            if is_select:
                # Fetch results for SELECT
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                rows_affected = len(data)
            else:
                # For INSERT/UPDATE/DELETE
                rows_affected = cursor.rowcount
                data = None
                connection.commit()

            logger.info(f"Query executed successfully. Rows affected: {rows_affected}")

            return {
                'success': True,
                'data': data,
                'rows_affected': rows_affected,
                'error': None,
                'error_type': None
            }

        except PostgresError as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            if connection:
                connection.rollback()

            return {
                'success': False,
                'data': None,
                'rows_affected': 0,
                'error': str(e),
                'error_type': 'database_error'
            }

        except Exception as e:
            logger.error(f"Unexpected error during query execution: {str(e)}")
            if connection:
                connection.rollback()

            return {
                'success': False,
                'data': None,
                'rows_affected': 0,
                'error': str(e),
                'error_type': 'connection_error'
            }

        finally:
            # Close cursor
            if cursor:
                cursor.close()

            # Return connection to pool
            if connection:
                DatabaseManager._connection_pool.putconn(connection)

    def close_all_connections(self):
        """Close all connections in the pool (for cleanup)"""
        if DatabaseManager._connection_pool:
            DatabaseManager._connection_pool.closeall()
            DatabaseManager._connection_pool = None
            logger.info("All database connections closed")
