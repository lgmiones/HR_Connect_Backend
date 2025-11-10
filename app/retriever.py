import os
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq  
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def get_vectorstore():
    """Load persisted Chroma vector store"""
    return Chroma(
        persist_directory="./chroma_db",
        collection_name="hr_documents"
    )

def query_hr_documents(question: str):
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        collection_name="hr_documents"
    )

    # Perform a similarity search directly
    docs = vectorstore.similarity_search(
        query=question,
        k=3  # number of relevant documents
    )

    context = "\n\n".join([d.page_content[:500] for d in docs])

    # LLM part remains the same
    llm = ChatGroq(
        temperature=0.3,
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are an HR assistant chatbot. "
            "Use the following HR documents as context to answer.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer clearly and concisely based on the policy."
        ),
    )

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    return {"answer": answer, "sources": [d.metadata for d in docs]}
