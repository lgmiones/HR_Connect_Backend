@echo off
REM HRConnect Backend - Project Structure Setup Script (Windows)
REM This script creates all necessary folders and __init__.py files

echo 🚀 Setting up HRConnect Backend project structure...

REM Create main app directory structure
mkdir app\api\v1\endpoints 2>nul
mkdir app\core 2>nul
mkdir app\db 2>nul
mkdir app\models 2>nul
mkdir app\schemas 2>nul
mkdir app\services 2>nul
mkdir app\ai 2>nul
mkdir app\utils 2>nul
mkdir app\middleware 2>nul

REM Create test directory
mkdir tests 2>nul

REM Create scripts directory
mkdir scripts 2>nul

REM Create docs directory
mkdir docs\hr_policies 2>nul

REM Create alembic directory
mkdir alembic\versions 2>nul

REM Create __init__.py files
type nul > app\__init__.py
type nul > app\api\__init__.py
type nul > app\api\v1\__init__.py
type nul > app\api\v1\endpoints\__init__.py
type nul > app\core\__init__.py
type nul > app\db\__init__.py
type nul > app\models\__init__.py
type nul > app\schemas\__init__.py
type nul > app\services\__init__.py
type nul > app\ai\__init__.py
type nul > app\utils\__init__.py
type nul > app\middleware\__init__.py
type nul > tests\__init__.py

echo ✅ Folder structure created successfully!
echo.
echo 📝 Next steps:
echo 1. Copy the provided files to their respective locations
echo 2. Create and configure your .env file
echo 3. Install dependencies: pip install -r requirements.txt
echo 4. Initialize database: python -c "from app.db.session import init_db; init_db()"
echo 5. Initialize ChromaDB: python scripts\init_vector_db.py
echo 6. Run the application: uvicorn app.main:app --reload

pause
