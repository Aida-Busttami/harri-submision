from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

# SQLite database URL
DATABASE_URL = "sqlite:///harri_ai.db"

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Create all tables from models
Base.metadata.create_all(bind=engine)