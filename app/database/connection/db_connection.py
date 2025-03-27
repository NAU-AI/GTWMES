from contextlib import contextmanager
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging

load_dotenv()

Base = declarative_base()
logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self):
        self.database_url = self._build_database_url()

        # Pool parameters from environment variables with default fallbacks
        pool_size = int(os.getenv("DB_POOL_SIZE", 10))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", 20))
        pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", 30))
        pool_recycle = int(os.getenv("DB_POOL_RECYCLE", 1800))  # Recycle every 30 mins

        self.engine = create_engine(
            self.database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            echo=False,
        )

        # Important: Set expire_on_commit=False
        self.Session = scoped_session(
            sessionmaker(bind=self.engine, expire_on_commit=False)
        )
        logger.info(
            "Database connection initialized with pool_size=%s and max_overflow=%s",
            pool_size,
            max_overflow,
        )

    def _build_database_url(self) -> str:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")

        missing_vars = [
            var
            for var in ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
            if not os.getenv(var)
        ]
        if missing_vars:
            raise ValueError(
                f"Missing required database environment variables: {missing_vars}"
            )

        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
            logger.debug("Transaction committed successfully.")
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}", exc_info=True)
            raise
        finally:
            session.close()
            logger.debug("Session closed.")

    def check_connection(self) -> bool:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection is healthy.")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}", exc_info=True)
            return False
