"""
LCEL RAG chains for single and compound queries
"""

import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from app.Agent.utils.llm_config import get_llm
from app.services.vectorstore import retrieve_documents, retrieve_documents_broad

logger = logging.getLogger(__name__)

# ============================================
# LCEL Prompt Templates
# ============================================

# Single question prompt
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant. Answer based on the policy documents provided.

IMPORTANT: Be CONCISE. Use bullet points. Keep it short."""),
    ("user", "Policy:\n{context}\n\nQ: {question}\nA:")
])

# Compound questions prompt
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
# LCEL Chains
# ============================================

# Get cached LLM instance
llm = get_llm()

# Single question RAG chain
rag_chain = (
    RunnableParallel({
        "context": lambda x: retrieve_documents(x["question"], k=x.get("k", 2)),
        "question": lambda x: x["question"]
    })
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Compound questions RAG chain
compound_rag_chain = (
    RunnableParallel({
        "context": lambda x: retrieve_documents_broad(x["questions_list"], k=x.get("k", 3)),
        "questions": lambda x: "\n".join([
            f"{i+1}. {q}" 
            for i, q in enumerate(x["questions_list"])
        ])
    })
    | compound_policy_prompt
    | llm
    | StrOutputParser()
)


logger.info("✅ RAG chains initialized")