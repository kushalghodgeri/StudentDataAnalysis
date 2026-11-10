"""Database connection manager: Singleton pattern with MySQL connection pool and SQLAlchemy engine."""

import threading
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple
import mysql.connector
from mysql.connector import pooling
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.config.settings import Settings, get_settings
from app.utils.exceptions import DBConnectionError
from app.utils.logger import logger


class DatabaseConnection:
    """Thread-safe Singleton managing MySQL connection pool and SQLAlchemy engine."""

    _instance: Optional["DatabaseConnection"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "DatabaseConnection":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings: Optional[Settings] = None):
        if self._initialized:
            return
        self.settings = settings or get_settings()
        self._pool: Optional[pooling.MySQLConnectionPool] = None
        self._engine: Optional[Engine] = None
        self._pool_lock = threading.Lock()
        self._initialized = True

    def _init_pool(self) -> None:
        """Initialize the MySQL connection pool."""
        if getattr(self.settings, "APP_ENV", "").lower() == "testing":
            logger.info("Testing environment detected: Skipping live MySQL pool initialization.")
            self._pool = None
            return

        try:
            # First perform a single probe connection with 1s timeout to fail fast if offline
            probe_conn = mysql.connector.connect(
                host=self.settings.DB_HOST,
                port=self.settings.DB_PORT,
                user=self.settings.DB_USER,
                password=self.settings.DB_PASSWORD,
                database=self.settings.DB_NAME,
                connection_timeout=1,
            )
            probe_conn.close()

            dbconfig = {
                "host": self.settings.DB_HOST,
                "port": self.settings.DB_PORT,
                "user": self.settings.DB_USER,
                "password": self.settings.DB_PASSWORD,
                "database": self.settings.DB_NAME,
                "pool_name": self.settings.DB_POOL_NAME,
                "pool_size": self.settings.DB_POOL_SIZE,
                "pool_reset_session": True,
                "autocommit": False,
                "charset": "utf8mb4",
                "connection_timeout": 1,
            }
            logger.info(
                f"Initializing MySQL connection pool '{self.settings.DB_POOL_NAME}' "
                f"to {self.settings.DB_HOST}:{self.settings.DB_PORT}/{self.settings.DB_NAME}"
            )
            self._pool = pooling.MySQLConnectionPool(**dbconfig)
            logger.info("MySQL connection pool successfully initialized.")
        except Exception as e:
            logger.warning(f"Could not initialize MySQL connection pool: {e}")
            self._pool = None

    @property
    def pool(self) -> pooling.MySQLConnectionPool:
        """Get or reinitialize connection pool."""
        if self._pool is None:
            with self._pool_lock:
                if self._pool is None:
                    self._init_pool()
                    if self._pool is None:
                        raise DBConnectionError("MySQL connection pool is not available.")
        return self._pool

    @property
    def engine(self) -> Engine:
        """Get or lazily initialize SQLAlchemy Engine (used by pandas read_sql)."""
        if self._engine is None:
            with self._pool_lock:
                if self._engine is None:
                    url = self.settings.sqlalchemy_url
                    self._engine = create_engine(
                        url,
                        pool_size=self.settings.DB_POOL_SIZE,
                        max_overflow=5,
                        pool_pre_ping=True,
                    )
        return self._engine

    @contextmanager
    def get_connection(self) -> Generator[mysql.connector.connection.MySQLConnection, None, None]:
        """Context manager yielding a pooled connection with auto commit/rollback."""
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except mysql.connector.Error as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.error(f"Database error during transaction: {e}")
            raise DBConnectionError(f"Database transaction error: {str(e)}") from e
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    @contextmanager
    def get_cursor(
        self, dictionary: bool = True
    ) -> Generator[mysql.connector.cursor.MySQLCursor, None, None]:
        """Context manager yielding a cursor from a pooled connection."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()

    def ping(self) -> bool:
        """Check if MySQL connection is healthy."""
        if self._pool is None:
            return False
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1 AS alive;")
                row = cursor.fetchone()
                return bool(row and (row.get("alive") == 1 or row.get(0) == 1))
        except Exception as e:
            logger.debug(f"DB Ping failed: {e}")
            return False

    def explain_query(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> List[Dict[str, Any]]:
        """Run EXPLAIN query on a given parameterized statement to inspect index usage and cost."""
        explain_sql = f"EXPLAIN {query}"
        try:
            with self.get_cursor(dictionary=True) as cursor:
                cursor.execute(explain_sql, params or ())
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to execute EXPLAIN query: {e}")
            raise DBConnectionError(f"EXPLAIN execution failed: {e}") from e


def get_db() -> DatabaseConnection:
    """Dependency helper returning the DatabaseConnection singleton."""
    return DatabaseConnection()
