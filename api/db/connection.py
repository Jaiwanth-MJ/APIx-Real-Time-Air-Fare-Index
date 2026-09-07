"""
api/db/connection.py
Flexible asynchronous database connection manager supporting PostgreSQL (asyncpg)
and local SQLite (aiosqlite) with automatic fallback.
"""

import os
import logging
from typing import Any, List, Optional, Dict

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connection pool with automatic backend detection."""
    def __init__(self):
        self.db_url = os.environ.get("DATABASE_URL", "sqlite:///./apix.db")
        self.is_postgres = "postgres" in self.db_url
        self._pool = None
        self._sqlite_path = "apix.db"
        if "sqlite:///" in self.db_url:
            self._sqlite_path = self.db_url.replace("sqlite:///", "")

    async def connect(self):
        if self.is_postgres:
            try:
                import asyncpg
                self._pool = await asyncpg.create_pool(
                    dsn=self.db_url,
                    min_size=2,
                    max_size=10,
                    timeout=10
                )
                logger.info("Connected to PostgreSQL / TimescaleDB connection pool")
                return
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed ({e}). Falling back to SQLite.")
                self.is_postgres = False

        import aiosqlite
        # Verify SQLite DB exists
        if not os.path.exists(self._sqlite_path):
            from db.seed_data import seed_database
            seed_database(self._sqlite_path)
        logger.info(f"Connected to SQLite database at {self._sqlite_path}")

    async def disconnect(self):
        if self.is_postgres and self._pool:
            await self._pool.close()
            logger.info("Closed PostgreSQL pool")

    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch all rows matching query as list of dictionaries."""
        if self.is_postgres and self._pool:
            # PostgreSQL parameter conversion ($1, $2, ...)
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(r) for r in rows]
        else:
            # SQLite parameter conversion (? instead of $n)
            import aiosqlite
            sqlite_query = query
            for i in range(1, 10):
                sqlite_query = sqlite_query.replace(f"${i}", "?")
            # Replace Postgres specific syntax like NOW() - ('30 days')::INTERVAL
            sqlite_query = sqlite_query.replace("NOW() - ($1 || ' days')::INTERVAL", "datetime('now', '-' || ? || ' days')")
            sqlite_query = sqlite_query.replace("DATE_TRUNC('month', index_date)", "strftime('%Y-%m', index_date)")
            sqlite_query = sqlite_query.replace("DATE_TRUNC('month', index_date)::DATE", "strftime('%Y-%m-01', index_date)")

            async with aiosqlite.connect(self._sqlite_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(sqlite_query, args) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(r) for r in rows]

    async def fetch_val(self, query: str, *args) -> Any:
        rows = await self.fetch_all(query, *args)
        if rows:
            return list(rows[0].values())[0]
        return None

db = DatabaseManager()
