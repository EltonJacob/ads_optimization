"""Database initialization script.

This script creates all database tables and performs initial setup.

Usage:
    python -m agent.database.init_db
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from agent.database.connection import create_tables, drop_tables, sync_engine
from agent.database.models import Base

# Load environment variables
env_path = project_root / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def init_database(drop_existing: bool = False):
    """Initialize the database.

    Args:
        drop_existing: If True, drop all existing tables first (DANGER!)
    """
    logger.info("=" * 60)
    logger.info("Database Initialization")
    logger.info("=" * 60)

    # Show connection info (without password)
    db_url = str(sync_engine.url)
    safe_url = db_url.split("@")[-1] if "@" in db_url else db_url
    logger.info(f"Database: {safe_url}")

    if drop_existing:
        logger.warning("⚠️  DROP EXISTING TABLES REQUESTED")
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Aborted by user")
            return
        drop_tables()

    # Create tables
    logger.info("Creating tables...")
    create_tables()

    # Verify tables were created
    logger.info("Verifying tables...")
    inspector = None
    try:
        from sqlalchemy import inspect
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")

        # Show table details
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            logger.info(f"\nTable: {table_name}")
            logger.info(f"  Columns: {len(columns)}")
            for col in columns:
                logger.info(f"    - {col['name']}: {col['type']}")
            logger.info(f"  Indexes: {len(indexes)}")
            for idx in indexes:
                logger.info(f"    - {idx['name']}: {idx['column_names']}")

    except Exception as e:
        logger.error(f"Error verifying tables: {e}")

    logger.info("=" * 60)
    logger.info("✅ Database initialization complete!")
    logger.info("=" * 60)


def check_connection():
    """Check database connection."""
    logger.info("Testing database connection...")

    try:
        with sync_engine.connect() as conn:
            result = conn.execute("SELECT 1")
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Unexpected result from database")
                return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Amazon PPC database")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before creating (DANGER: deletes all data)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check database connection",
    )

    args = parser.parse_args()

    if args.check:
        check_connection()
    else:
        init_database(drop_existing=args.drop)
