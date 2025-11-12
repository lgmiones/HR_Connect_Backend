# 🧭 HRConnect: Human Resource Information System (HRIS)

## 📘 Introduction

### Project Overview
**HRConnect** is a **web-based Human Resource Information System (HRIS)** designed to streamline essential HR processes, with a primary focus on **Leave Management**.  
The system enhances traditional HR operations through the integration of the **HRConnect Chatbot**, an **AI-powered virtual assistant** that automates HR interactions and improves accessibility to HR-related information.

The **HRConnect Chatbot** leverages **Artificial Intelligence (AI)** and **Natural Language Processing (NLP)** to provide employees and HR personnel with **instant, context-aware assistance**.  
It enables users to:
- Access HR policies,
- Check leave credits,
- Receive automated guidance for filing requests.

By integrating intelligent automation, **HRConnect** aims to:
- Enhance employee self-service,
- Reduce administrative workload,
- Improve overall HR efficiency within the organization.

---

## 🎯 Project Scope

The current phase of **HRConnect** focuses exclusively on the **Leave Management Module** and its integration with the **AI-powered HRConnect Chatbot**.  
This phase aims to automate leave-related processes, provide instant employee assistance through intelligent chat responses, and enhance accessibility to HR policies and procedures.

Within this scope, employees can:
- Check available leave balances,
- Understand HR leave policies,
- Instantly view their remaining leave credits through chatbot interactions.

The **HRConnect Chatbot** uses an **Agentic Retrieval-Augmented Generation (RAG)** model to ensure accurate, context-aware responses based on official HR documentation and company policies.

### Data Sources
- 🧠 **Vector Database (Chroma)** — Stores and indexes HR-related policies and documents for semantic retrieval.
- 🗄️ **MS SQL Database** — Stores structured employee records, user credentials, account details, and leave balances.

---

## ⚙️ System Requirements

### 2.1 Functional Requirements

#### 👩‍💼 Employee Functions
- Check remaining leave credits.  
- Access HR policies and FAQs via the AI-powered chatbot.  
- Receive real-time chatbot assistance for filing requests and understanding policies.  

#### 🤖 Chatbot Functions
- Retrieve and present HR-related information (e.g., policies, remainin leave credits).  
- Provide step-by-step guidance for filing leave.  
- Understand and respond to queries using Natural Language Processing (NLP).  
- Integrate with backend services to fetch data from SQL Server and Vector Database (Chroma).  
- Deliver AI-driven responses using **Azure OpenAI** based on the retrieved context.  

---

### 2.2 Non-Functional Requirements

| **Category** | **Requirement** |
|---------------|-----------------|
| **Performance** | Pages and chatbot responses should load within 3 seconds and support up to 500 concurrent users. |
| **Reliability** | Maintain 99% uptime and implement automatic backups to prevent data loss. |
| **Security** | Implement RBAC, encrypted passwords, and secure API communication (HTTPS, JWT). |
| **Usability** | Provide an intuitive, user-friendly interface with minimal training required; chatbot should use clear, natural language. |
| **Scalability** | The system should support future expansion for additional HR modules. |
| **Compatibility** | Accessible through major browsers (Chrome, Edge, Firefox) and mobile devices. |
| **Maintainability** | Modular and well-documented codebase for easier updates and debugging. |
| **AI Accuracy** | Chatbot should maintain policy-aligned, contextually correct responses using RAG-based retrieval. |
| **Data Privacy** | Sensitive HR data must comply with privacy standards and company policies. |

---

## 🧱 System Architecture and Design Overview

### 3.1 Architecture Overview
The **HRConnect** system follows a **three-layer architecture** integrated with an **Agentic Retrieval-Augmented Generation (RAG)** framework.  
This structure combines **structured HR data** with **unstructured policy documents**, allowing the chatbot to autonomously reason, plan, and execute context-driven actions.

| **Layer** | **Description** |
|------------|-----------------|
| **Presentation Layer** | Frontend interface (Chatbot UI, HR dashboards). Enables users to check leave credits, inquire about policies, and receive guided assistance for filing requests. Focuses on user experience and real-time communication. |
| **Application Layer** | Core logic and intelligent agent processing. Implements the Agentic RAG pipeline for reasoning, query understanding, retrieval, and response generation using Azure OpenAI and NLP. Handles workflow orchestration and backend integration. |
| **Data Layer** | Manages data storage and retrieval. Includes: <br>• **MS SQL Database** — Structured employee and leave data. <br>• **Chroma Vector Database** — Embedded HR policy documents and FAQs for semantic retrieval. Ensures synchronization and efficient access for AI operations. |

---

### 3.2 User Interface Design
- User-friendly and accessible web interface.  
- Integrated chatbot panel for interactive HR communication.  
- Real-time response display for leave-related queries and HR policy lookups.

### 3.3 Database Design
The system includes an **Entity Relationship Diagram (ERD)** representing the structure of employee records, leave balances, and policy references stored in SQL Server.

---

## 💻 Implementation Details

### 4.1 Development Environment

| **Tools / Frameworks** | **Usage** |
|--------------------------|------------|
| **Python, FastAPI** | Backend development |
| **SQL Server, SQLAlchemy, Alembic** | Database and ORM |
| **LangChain, Azure OpenAI, ChromaDB** | AI & Chatbot Integration |
| **Next.js, Tailwind CSS** | Frontend interface |
| **bcrypt, python-jose, JWT Auth** | Authentication & Security |
| **Git, GitHub** | Version Control & Collaboration |
| **Visual Studio Code** | Development Environment |

---

### 4.2 Key Components
- **Authentication & Role Management** — Ensures secure access for different user roles.  
- **Leave Management Module** — Automates leave filing, validation, and balance tracking.  
- **Chatbot Assistant** — Provides real-time, intelligent HR communication.

---

### 4.3 Agentic RAG Chatbot Integration
- **Knowledge Retrieval:** Embeds and indexes HR policies and employee leave data for accurate retrieval.  
- **Answer Generation:** Uses Azure OpenAI LLMs to synthesize and generate precise responses.  
- **Context-Aware Conversations:** Maintains session context for multi-turn dialogues and follow-up queries.  

---

### 4.4 Installation & Setup
Follow these steps to run HRConnect locally:
**Clone the repository**
**1. git clone https://github.com/your-org/hrconnect.git
cd hrconnect

**2. Set up the backend
cd HR_Connect_Backend
pip install -r requirements.txt

**3. Configure environment variables
Create a .env file and add:
DATABASE_URL=mssql+pyodbc://(localdb)\MSSQLLocalDB/HRConnectDB?driver=ODBC+Driver+17+for+SQL+Server
AZURE_OPENAI_API_KEY=your-api-key
SECRET_KEY=your-secret-key

**4. Run the FastAPI server
cd HR_Connect_Frontend
npm install
npm run dev

**5. Run the frontend (optional)
cd HR_Connect_Frontend
npm install
npm run dev

**6. Access the system
Open your browser and go to:
http://localhost:8000 (Backend API)
 http://localhost:3000 (Frontend UI)


## ✅ Conclusion

**HRConnect** demonstrates the potential of AI-driven automation in modern HR systems.  
By combining **structured databases**, **vectorized document retrieval**, and **Agentic AI reasoning**, HRConnect enables organizations to streamline leave management, enhance employee engagement, and ensure efficient HR operations with intelligent, real-time support.

---

##
This project is developed for organizational use.  
All intellectual property rights belong to the **HRConnect Project Team**.

---

## 📞 Contact
For inquiries or collaboration opportunities:  
📧 **sdalipio@n-pax.com*
    **eyong@n-pax.com*
    **rlsanchez@n-pax.com*

