from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
import sys

settings = get_settings()

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful.")
    except OperationalError as e:
        print(f"Failed to connect to the database at {DATABASE_URL}\nError: {e}")
        sys.exit(1)
    from app.models import chat_history, users, articles

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

init_db()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
