from app.core.config import settings
from sqlalchemy import create_engine

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

try:
    with engine.connect() as conn:
        print("✅ Connected successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
