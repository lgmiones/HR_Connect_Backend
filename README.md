# HRConnect - Intelligent HR Information System

An AI-powered Human Resource Information System featuring an **Agentic RAG chatbot** that intelligently routes queries between policy documents (vector database) and employee data (SQL database).

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![LangChain](https://img.shields.io/badge/LangChain-0.1-orange)
![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4o--mini-purple)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Usage Examples](#-usage-examples)
- [Development](#-development)
- [Team](#-team)
- [License](#-license)

---

## ✨ Features

### 🤖 Intelligent Agentic Chatbot
- **Query Classification** - Automatically determines if questions are about policies or personal data
- **Multi-Source RAG** - Routes queries to appropriate data sources (Chroma DB or SQL Server)
- **Compound Query Handling** - Processes multiple questions in one request
- **Smart Context Management** - Maintains conversation state across queries

### 🔐 Authentication & Security
- JWT-based authentication
- Password hashing with bcrypt
- Token blacklisting for logout
- Protected API endpoints
- Role-based access control ready

### 📊 HR Management Features
- Employee leave balance tracking
- Leave request management
- Company policy document search
- Attendance records (planned)
- Performance reviews (planned)

### 🎯 Advanced RAG System
- **Vector Search** - ChromaDB for policy document retrieval
- **Semantic Search** - SentenceTransformer embeddings
- **SQL Integration** - Direct database queries for employee data
- **LangGraph Orchestration** - Workflow automation for query routing

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    User Request                         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌────────────────────────────────────────────────────────┐
│              FastAPI Chatbot Endpoint                   │
│              (Authentication Required)                  │
└────────────────────┬───────────────────────────────────┘
                     ↓
┌────────────────────────────────────────────────────────┐
│           LangGraph Agentic Orchestrator               │
│                                                        │
│  ┌──────────────┐      ┌───────────────┐               │
│  │ Query        │  →   │ Router        │               │
│  │ Decomposer   │      │ (Classifier)  │               │
│  └──────────────┘      └───────┬───────┘               │
│                                ↓                       │
│         ┌──────────────────────|─────────────────┐     │
│         ↓                      ↓                 ↓     │
│  ┌────────────┐         ┌─────────────┐   ┌──────────┐ │
│  │ Policy     │         │ Personal    │   │ General  │ │
│  │ Handler    │         │ Data Handler│   │ Handler  │ │
│  └─────┬──────┘         └──────┬──────┘   └──────────┘ │
└────────┼───────────────────────|───────────────────────┘
         ↓                       ↓
┌────────────────┐    ┌─────────────────┐
│ Chroma DB      │    │ SQL Server      │
│ (Policy Docs)  │    │ (Employee Data) │
│                │    │                 │
│ - Embeddings   │    │ - Leave Balance │
│ - Vector Search│    │ - Attendance    │
└────────────────┘    └─────────────────┘
         ↓                      ↓
         └──────────┬───────────┘
                    ↓
        ┌──────────────────────┐
        │  Azure OpenAI        │
        │  (GPT-4o-mini)       │
        │  - Query Classification
        │  - Response Generation
        └──────────────────────┘
```

### Key Components

1. **Query Decomposer** - Breaks compound questions into sub-queries
2. **Router** - Classifies queries as policy/personal_data/general
3. **Policy Handler** - Searches HR documents using RAG
4. **Personal Data Handler** - Queries SQL database for user-specific data
5. **General Handler** - Handles system information queries

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### AI & LLM
- **Azure OpenAI** - GPT-4o-mini for query classification and generation
- **LangChain** - LLM application framework
- **LangGraph** - Workflow orchestration for agentic behavior

### Vector Database & Embeddings
- **ChromaDB** - Vector database for document storage
- **SentenceTransformers** - `all-MiniLM-L6-v2` for embeddings

### Database
- **SQL Server** - Employee data storage
- **SQLAlchemy** - ORM and database toolkit
- **Alembic** - Database migrations

### Authentication
- **python-jose** - JWT token handling
- **passlib** - Password hashing

### Document Processing
- **LangChain Text Splitters** - Document chunking
- **PyPDF2** - PDF text extraction
- **docx2txt** - Word document processing

---

## 📦 Prerequisites

- Python 3.11+
- SQL Server (local or Azure)
- Azure OpenAI API access
- Git

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HR_Connect_Backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:
```env
# Database Configuration
SQLALCHEMY_DATABASE_URI=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# JWT Configuration
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Optional: Groq API (Fallback)
GROQ_API_KEY=your_groq_key
```

### 5. Set Up Database

Run migrations:
```bash
alembic upgrade head
```

### 6. Add HR Documents

Place your HR policy documents in:
```
data/hr_docs/
├── employee_handbook.pdf
├── leave_policy.docx
├── code_of_conduct.pdf
└── ...
```

### 7. Build Vector Database
```bash
python -m app.Chromadb.embed_documents
```

---

## ⚙️ Configuration

### Database Schema

The system uses the following tables:
```sql
-- Users table
CREATE TABLE users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

-- Leave balance table
CREATE TABLE leave_balance (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES users(user_id),
    total_leaves INT NOT NULL,
    used_leaves INT DEFAULT 0
);
```

### Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy a model (GPT-4o-mini recommended)
3. Copy the endpoint, key, and deployment name to `.env`

---

## 🏃 Running the Application

### Development Mode
```bash
python -m uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Key Endpoints

#### Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
```

#### Chatbot
```http
POST /api/v1/chatbot/query
GET  /api/v1/chatbot/history
GET  /api/v1/chatbot/health
```

### Example Usage

#### 1. Register a User
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@hrconnect.com",
    "password": "SecurePass123"
  }'
```

#### 2. Login
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@hrconnect.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

#### 3. Query Chatbot
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chatbot/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "question": "How many leaves do I have?"
  }'
```

**Response:**
```json
{
  "answer": "You have **15 leaves remaining** (5/20 used).",
  "query_type": "personal_data",
  "source": "personal_database",
  "is_compound": false,
  "num_questions": 1
}
```

---

## 📁 Project Structure
```
HR_Connect_Backend/
├── app/
│   ├── Agent/                      # Agentic RAG system
│   │   ├── handlers/
│   │   │   ├── base_handler.py    # Handler interface
│   │   │   ├── policy_handler.py  # Policy queries → Chroma
│   │   │   ├── personal_data_handler.py  # Personal queries → SQL
│   │   │   └── general_handler.py # General system info
│   │   ├── utils/
│   │   │   └── llm_config.py      # LLM initialization
│   │   ├── models.py               # Pydantic state models
│   │   ├── query_decomposer.py    # Multi-query splitting
│   │   └── orchestrator.py        # LangGraph workflow
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   └── chatbot.py         # Chatbot endpoints
│   │   └── dependencies.py        # Auth dependencies
│   │
│   ├── core/
│   │   ├── config.py              # Settings management
│   │   ├── auth_utils.py          # JWT & password utils
│   │   └── token_blacklist.py    # Token revocation
│   │
│   ├── db/
│   │   └── session.py             # Database connection
│   │
│   ├── models/
│   │   └── user.py                # SQLAlchemy models
│   │
│   ├── repositories/
│   │   ├── base_repository.py     # Generic CRUD
│   │   └── user_repository.py     # User data access
│   │
│   ├── schemas/
│   │   └── auth_schemas.py        # Request/response schemas
│   │
│   ├── services/
│   │   ├── auth_service.py        # Auth business logic
│   │   └── retriever.py           # RAG query system
│   │
│   └── Chromadb/
│       ├── chroma_setup.py        # Vector DB setup
│       ├── embed_documents.py     # Document embedding
│       ├── file_loader.py         # Document processing
│       └── config.py              # Chroma configuration
│
├── data/
│   └── hr_docs/                   # HR policy documents
│
├── chroma_db/                     # Vector database (generated)
│
├── alembic/                       # Database migrations
│
├── main.py                        # FastAPI application entry
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (create this)
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## 💡 Usage Examples

### Single Query - Personal Data

**Question:** "How many leaves do I have?"

**Response:**
```json
{
  "answer": "You have **15 leaves remaining** (5/20 used).",
  "query_type": "personal_data",
  "source": "personal_database"
}
```

---

### Single Query - Policy

**Question:** "What is the leave policy?"

**Response:**
```json
{
  "answer": "Employees receive 10 vacation days and 5 sick days per year. Leave requests are submitted through HRConnect and require HR approval. Unused leave is paid out when you leave the company.",
  "query_type": "policy",
  "source": "policy_documents"
}
```

---

### Compound Query

**Question:** "What is the leave policy? How many leaves do I have? How do I apply for emergency leave?"

**Response:**
```json
{
  "answer": "Employees receive 10 vacation days and 5 sick days per year. Leave requests require HR approval through HRConnect.\n\nYou have **15 leaves remaining** (5/20 used).\n\nTo apply for emergency leave: file leave as usual, select 'Emergency Leave', provide a brief reason, and submit for HR review.",
  "query_type": "compound",
  "source": "multiple_sources (3 questions)"
}
```

---

## 🔧 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Style
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

### Rebuild Vector Database
```bash
# Delete existing database
rm -rf chroma_db/

# Rebuild from documents
python -m app.Chromadb.embed_documents
```

---

## 🧪 Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Access protected endpoint with token
- [ ] Query personal data: "How many leaves do I have?"
- [ ] Query policy: "What is the leave policy?"
- [ ] Test compound query with 3 questions
- [ ] Logout and verify token is revoked
- [ ] Attempt to access endpoint with revoked token (should fail)

---

## 🎯 Key Features Demonstrated

### SOLID Principles
- **Single Responsibility**: Each handler does one thing
- **Open/Closed**: Easy to add new handlers without modifying existing code
- **Liskov Substitution**: All handlers implement `BaseQueryHandler`
- **Interface Segregation**: Handlers only implement what they need
- **Dependency Inversion**: High-level code depends on abstractions

### Design Patterns
- **Repository Pattern**: Data access layer abstraction
- **Factory Pattern**: Handler creation
- **Strategy Pattern**: Different query handling strategies

### Advanced RAG Techniques
- **Agentic Routing**: Intelligent query classification
- **Multi-Source Retrieval**: Combines vector DB and SQL
- **Query Decomposition**: Handles compound questions
- **Semantic Search**: Uses embeddings for policy retrieval

---

## 👥 Team

**HRConnect Development Team**
- Team Size: 7 members
- Roles: AI Engineers, Data Engineer, DevOps Engineer
- Timeline: 1 month capstone project
- Constraints: Free resources only

---

## 📝 License

This project is developed as a capstone project for educational purposes.

---

## 🤝 Contributing

This is a capstone project. For questions or suggestions, please contact the development team.

---

## 🔮 Future Enhancements

- [ ] Conversation history tracking
- [ ] Feedback mechanism for chatbot responses
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Integration with email/Slack
- [ ] Mobile application
- [ ] Real-time notifications
- [ ] Performance review management
- [ ] Onboarding workflow automation

---

## 📞 Support

For issues or questions:
1. Check the [API Documentation](http://127.0.0.1:8000/docs)
2. Review the logs in the terminal
3. Contact the development team

---

## 🙏 Acknowledgments

- **Azure OpenAI** for LLM capabilities
- **LangChain** for RAG framework
- **ChromaDB** for vector storage
- **FastAPI** for excellent API framework
- **Anthropic Claude** for development assistance

---

**Built with ❤️ by the HRConnect Team**

*Last Updated: November 2025*