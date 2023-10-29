from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define your database URL
DATABASE_URL = "sqlite:///./blogdb.db"  # Use SQLite as an example, replace with your actual database URL

# Create a SQLAlchemy engine to connect to the database
engine = create_engine(DATABASE_URL)

# Create a session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
