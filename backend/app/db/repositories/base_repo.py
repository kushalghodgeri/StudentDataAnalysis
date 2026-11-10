"""Base repository with parameterized query execution, DataFrame fetching, and executemany."""

import re
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from app.db.connection import DatabaseConnection, get_db
from app.utils.exceptions import DataValidationError, DBConnectionError
from app.utils.logger import logger


class BaseRepository:
    """Base class providing safe parameterized SQL operations and DataFrame extraction."""

    # Disallow naked SELECT * in adherence to SQL optimization rules
    _SELECT_STAR_PATTERN = re.compile(r"SELECT\s+\*\s+FROM", re.IGNORECASE)

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db()

    def _validate_query(self, query: str) -> None:
        """Enforce strict query rules: no 'SELECT *' allowed."""
        if self._SELECT_STAR_PATTERN.search(query):
            err_msg = (
                "SQL Anti-pattern detected: 'SELECT *' is strictly prohibited. "
                "Explicitly name required columns to optimize I/O and cache usage."
            )
            logger.error(err_msg)
            raise DataValidationError(err_msg)

    def fetch_df(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> pd.DataFrame:
        """Fetch query results directly into a Pandas DataFrame using parameterized query.
        
        Uses DB connection cursor or SQLAlchemy engine safely.
        """
        self._validate_query(query)
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
                if not rows:
                    cols = [col[0] for col in cursor.description] if cursor.description else []
                    return pd.DataFrame(columns=cols)
                return pd.DataFrame(rows)
        except Exception as e:
            logger.error(f"Error fetching DataFrame for query [{query[:60]}...]: {e}")
            raise DBConnectionError(f"DataFrame fetch failed: {str(e)}") from e

    def fetch_all(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> List[Dict[str, Any]]:
        """Execute parameterized query and return all matching rows as dictionaries."""
        self._validate_query(query)
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing fetch_all [{query[:60]}...]: {e}")
            raise DBConnectionError(f"fetch_all failed: {str(e)}") from e

    def fetch_one(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute parameterized query and return the first matching row or None."""
        self._validate_query(query)
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error executing fetch_one [{query[:60]}...]: {e}")
            raise DBConnectionError(f"fetch_one failed: {str(e)}") from e

    def execute(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return lastrowid or affected rowcount."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(query, params or ())
                    row_id = cursor.lastrowid
                    row_count = cursor.rowcount
                    return row_id if row_id else row_count
                finally:
                    cursor.close()
        except Exception as e:
            logger.error(f"Error executing query [{query[:60]}...]: {e}")
            raise DBConnectionError(f"Execution failed: {str(e)}") from e

    def execute_many(
        self, query: str, seq_params: List[Tuple[Any, ...]]
    ) -> int:
        """Perform high-performance bulk operations using cursor.executemany."""
        if not seq_params:
            return 0
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.executemany(query, seq_params)
                    affected = cursor.rowcount
                    logger.debug(f"executemany inserted/updated {affected} rows.")
                    return affected
                finally:
                    cursor.close()
        except Exception as e:
            logger.error(f"Error in execute_many [{query[:60]}...]: {e}")
            raise DBConnectionError(f"execute_many failed: {str(e)}") from e

    def explain(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> List[Dict[str, Any]]:
        """Return the EXPLAIN execution plan for performance inspection."""
        self._validate_query(query)
        return self.db.explain_query(query, params)
