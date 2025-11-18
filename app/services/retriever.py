"""
Retriever service - OPTIMIZED with LCEL chains and Azure Embeddings
Supports both single and compound policy queries
"""

import os
import logging
import time
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from app.core.config import settings
from app.Agent.utils.llm_config import get_llm

load_dotenv()
logger = logging.getLogger(__name__)

_embedding = None
_vectorstore = None


def get_vectorstore():
    """Get or create vectorstore with Azure embeddings (singleton)"""
    global _embedding, _vectorstore
    
    if _vectorstore is None:
        logger.info("Initializing Azure embeddings and vectorstore...")
        
        _embedding = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_EMBEDDINGS_ENDPOINT,
            azure_deployment=settings.AZURE_EMBEDDINGS_DEPLOYMENT,
            api_key=settings.AZURE_EMBEDDINGS_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        
        _vectorstore = Chroma(
            persist_directory="./chroma_db",
            collection_name="hr_documents",
            embedding_function=_embedding
        )
        logger.info("✅ Vectorstore initialized and cached")
    
    return _vectorstore


# ============================================
# Document Retrieval Functions
# ============================================

def retrieve_documents(question: str, k: int = 2) -> str:
    """
    Retrieve relevant documents from ChromaDB for a single question
    
    Args:
        question: Single HR policy question
        k: Number of documents to retrieve
        
    Returns:
        Formatted context string with retrieved documents
    """
    try:
        vectorstore = get_vectorstore()
        
        # ChromaDB search (includes Azure embedding API call)
        docs = vectorstore.similarity_search(query=question, k=k)
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        # Trim if too long
        max_context_length = 1000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        logger.info(f"Retrieved {len(docs)} documents ({len(context)} chars)")
        return context
        
    except Exception as e:
        logger.error(f"ChromaDB retrieval error: {str(e)}", exc_info=True)
        return "Error retrieving documents."


# Around line 60 - Update this function
def retrieve_documents_broad(questions: list[str], k: int = 3) -> str:  # ✅ Changed to 3
    """
    Retrieve documents using multiple questions for broader context
    Optimized for compound queries with speed priority
    """
    try:
        vectorstore = get_vectorstore()
        
        # Combine questions for broader retrieval
        combined_query = " | ".join(questions)
        
        # ChromaDB search
        docs = vectorstore.similarity_search(query=combined_query, k=k)
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        # Aggressive trimming for speed
        max_context_length = 1000  # ✅ Reduced from 1500
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        logger.info(f"Retrieved {len(docs)} documents for compound query ({len(context)} chars)")
        return context
        
    except Exception as e:
        logger.error(f"ChromaDB compound retrieval error: {str(e)}", exc_info=True)
        return "Error retrieving documents."


# Around line 100 - Update compound prompt
compound_policy_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant. Answer ALL questions below based on the policy documents.

IMPORTANT: Be CONCISE and DIRECT.
- Use bullet points
- Avoid repeating information
- Maximum 5 bullet points per question
- Keep answers short and actionable"""),
    ("user", """Policy Documents:
{context}

Questions:
{questions}

Provide SHORT, clear answers for each question.""")
])

# ============================================
# LCEL Prompt Templates
# ============================================

# Single question prompt (around line 100)
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant. Answer based on the policy documents provided.

IMPORTANT: Be CONCISE. Use bullet points. Keep it short."""),  # ✅ Added conciseness
    ("user", "Policy:\n{context}\n\nQ: {question}\nA:")
])

# Compound questions prompt
compound_policy_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant. Answer ALL questions below based on the policy documents.

CRITICAL: Be CONCISE and DIRECT.
- Use bullet points
- Avoid repeating information
- Maximum 5 bullet points per question"""),
    ("user", """Policy Documents:
{context}

Questions:
{questions}

Provide SHORT, clear answers for each question.""")
])


# ============================================
# LCEL Chains
# ============================================

# Get cached LLM instance
llm = get_llm()

# ✅ Single question RAG chain
rag_chain = (
    RunnableParallel({
        "context": lambda x: retrieve_documents(x["question"], k=x.get("k", 2)),
        "question": lambda x: x["question"]
    })
    | rag_prompt
    | llm
    | StrOutputParser()
)

# ✅ Compound questions RAG chain
compound_rag_chain = (
    RunnableParallel({
        "context": lambda x: retrieve_documents_broad(x["questions_list"], k=x.get("k", 5)),
        "questions": lambda x: "\n".join([
            f"{i+1}. {q}" 
            for i, q in enumerate(x["questions_list"])
        ])
    })
    | compound_policy_prompt
    | llm
    | StrOutputParser()
)


# ============================================
# Public API Functions
# ============================================

def query_hr_documents(question: str, k: int = 2):
    """
    Query HR documents using LCEL chain (optimized for single questions)
    
    Performance targets with Azure Embeddings:
    - Query embedding: ~2.7s (Azure API - cannot optimize)
    - ChromaDB search: ~0.1s
    - LLM generation: ~5-6s
    - Total: ~8-9s
    
    Args:
        question: Single HR policy question
        k: Number of documents to retrieve
        
    Returns:
        dict with 'answer' key
    """
    total_start = time.time()
    
    try:
        logger.info(f"🔍 RAG query: {question}")
        
        # ✅ Use LCEL chain
        answer = rag_chain.invoke({"question": question, "k": k})
        
        total_time = time.time() - total_start
        logger.info(f"⏱️ TOTAL: {total_time:.2f}s")
        
        return {"answer": answer}
        
    except Exception as e:
        logger.error(f"RAG error: {str(e)}", exc_info=True)
        raise


def query_compound_policies(questions: list[str], k: int = 5):
    """
    Query HR documents for multiple related policy questions using LCEL
    Optimized to retrieve once and generate one comprehensive answer
    
    Performance improvement:
    - Before (parallel): 2 retrievals + 2 LLM calls = ~14-16s
    - After (merged): 1 retrieval + 1 LLM call = ~9-10s
    - Savings: ~40% faster for compound queries
    
    Args:
        questions: List of related policy questions
        k: Number of documents to retrieve
        
    Returns:
        dict with 'answer' key
    """
    total_start = time.time()
    
    try:
        logger.info(f"🔍 Compound RAG query with {len(questions)} questions")
        
        # ✅ Use compound LCEL chain
        answer = compound_rag_chain.invoke({"questions_list": questions, "k": k})
        
        total_time = time.time() - total_start
        logger.info(f"⏱️ COMPOUND TOTAL: {total_time:.2f}s")
        
        return {"answer": answer}
        
    except Exception as e:
        logger.error(f"Compound RAG error: {str(e)}", exc_info=True)
        raise