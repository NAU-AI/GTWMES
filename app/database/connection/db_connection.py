from contextlib import contextmanager
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging

load_dotenv()

Base = declarative_base()

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self, pool_size: int = 10, max_overflow: int = 20):
        self.database_url = self._build_database_url()
        self.engine = create_engine(
            self.database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=False,
        )
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        logger.info("Database connection initialized.")

    def _build_database_url(self) -> str:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")

        if not all([db_user, db_password, db_host, db_name]):
            raise ValueError("Missing required database environment variables.")

        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back due to an error: {e}", exc_info=True)
            raise
        finally:
            session.close()
            self.Session.remove()
            logger.info("Session closed.")

    def check_connection(self) -> bool:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection is healthy.")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}", exc_info=True)
            return False
