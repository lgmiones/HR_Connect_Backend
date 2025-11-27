# """
# Database session configuration
# """

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# # Create database engine
# engine = create_engine(
#     settings.SQLALCHEMY_DATABASE_URI,
#     pool_pre_ping=True,  # Verify connections before using them
#     echo=False  # Set to True to see SQL queries in console
# )

# # Create session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create Base class for models
# Base = declarative_base()


# # Dependency to get database session
# def get_db():
#     """
#     Database session dependency
#     Yields a database session and ensures it's closed after use
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



"""
Database session configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
)

# ✅ CRITICAL: expire_on_commit=True prevents caching
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True,  # ✅ This is CRITICAL!
)

Base = declarative_base()


def get_db():
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        # ✅ Expire all cached objects at start of request
        db.expire_all()
        yield db
    finally:
        db.close()