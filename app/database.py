# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create SQLite database (file storage)
SQLALCHEMY_DATABASE_URL = "sqlite:///./crypto_arbitrage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# ORM base class
Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()