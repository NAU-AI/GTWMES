from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Define the declarative base class (Base for ORM models)
Base = declarative_base()

# Database connection string (PostgreSQL)
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create the database engine (Manages DB connections)
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

# Create session factory (Manages DB transactions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
