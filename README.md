# HRConnect Backend

AI-powered Human Resource Information System with intelligent chatbot assistance.

## 🚀 Features

- **JWT Authentication** - Secure user authentication and authorization
- **Leave Management** - Track and manage employee leave balances
- **AI Chatbot** - Agentic RAG-based chatbot for HR assistance
- **Vector Search** - ChromaDB integration for policy document retrieval
- **Azure OpenAI** - Powered by GPT-4 for intelligent responses
- **RESTful API** - Built with FastAPI for high performance

## 📋 Prerequisites

- Python 3.9+
- SQL Server (or Azure SQL Database)
- Azure OpenAI API access
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd hrconnect-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your actual credentials
```

**Important:** Update the following in `.env`:
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `DATABASE_URL` - Your SQL Server connection string
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint

### 5. Set Up Database

```bash
# Initialize database tables
python -c "from app.db.session import init_db; init_db()"

# Or use Alembic for migrations
alembic upgrade head
```

### 6. Initialize ChromaDB

```bash
# Load HR policy documents into vector database
python scripts/init_vector_db.py
```

### 7. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs for API documentation

## 📁 Project Structure

```
hrconnect-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core configuration
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── ai/               # AI/RAG components
│   └── main.py           # Application entry point
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── docs/                 # Documentation
├── requirements.txt      # Dependencies
└── .env.example          # Example environment variables
```

## 🔐 Authentication

### Register a New User

```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### Login

```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

Returns:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Use Token in Requests

```bash
GET /api/v1/users/me
Authorization: Bearer eyJ...
```

## 🤖 Chatbot Usage

### Query the Chatbot

```bash
POST /api/v1/chatbot/query
Authorization: Bearer eyJ...
{
  "query": "How many leave credits do I have?",
  "session_id": "user-123"
}
```

Response:
```json
{
  "response": "Based on your current leave balance, you have 12 days remaining...",
  "sources_count": 3,
  "has_employee_data": true
}
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user

### Leave Balances
- `GET /api/v1/leave-balances/me` - Get my leave balance
- `PUT /api/v1/leave-balances/me` - Update leave balance

### Chatbot
- `POST /api/v1/chatbot/query` - Query the chatbot
- `DELETE /api/v1/chatbot/session/{session_id}` - Clear session history

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## 📝 Adding HR Documents

1. Place your HR policy documents in `docs/hr_policies/`
2. Supported formats: PDF, DOCX, TXT
3. Run initialization script:

```bash
python scripts/init_vector_db.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | `openssl rand -hex 32` |
| `DATABASE_URL` | SQL Server connection | `mssql+pyodbc://...` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | `sk-...` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB location | `./chroma_db` |

### Chatbot Parameters

- `MAX_CONVERSATION_HISTORY` - Number of messages to keep in context
- `SIMILARITY_THRESHOLD` - Minimum similarity for document retrieval
- `TOP_K_RESULTS` - Number of documents to retrieve
- `AZURE_OPENAI_TEMPERATURE` - LLM creativity (0-1)

## 🚀 Deployment

### Using Docker

```bash
# Build image
docker build -t hrconnect-backend .

# Run container
docker run -p 8000:8000 --env-file .env hrconnect-backend
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [ReDoc](http://localhost:8000/redoc) - Alternative API docs
- [Setup Guide](BACKEND_SETUP_GUIDE.md) - Detailed setup instructions

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run tests and linting
5. Submit a pull request

## 🐛 Troubleshooting

### ChromaDB Connection Issues

```bash
# Clear and reinitialize
rm -rf chroma_db/
python scripts/init_vector_db.py
```

### SQL Server Connection Issues

```bash
# Test connection
python -c "from app.db.session import engine; print(engine.connect())"
```

### Azure OpenAI Issues

```bash
# Test connection
python -c "from app.ai.llm import test_connection; test_connection()"
```

## 📄 License

[Your License Here]

## 👥 Team

- **Project Manager:** Raquel Sanchez
- **Backend Lead:** Eugene Apostol
- **Backend Developers:** Shaundyl Alipio, Louell Grey
- **Frontend Lead:** Earl Francis Ong
- **Frontend Developer:** James Anquillano
- **DevOps/QA:** Rhea Mae Arnado

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

Built with ❤️ using FastAPI, Azure OpenAI, and ChromaDB
