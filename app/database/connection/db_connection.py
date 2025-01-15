import psycopg2
from psycopg2.extras import RealDictCursor
import os 
from dotenv import load_dotenv

load_dotenv()  

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                cursor_factory=RealDictCursor
            )
            return self.connection
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()
