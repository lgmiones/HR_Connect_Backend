# retriever.py

import os
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from app.Chromadb.embed_documents import SentenceTransformerEmbeddings
from app.core.config import settings 

load_dotenv()

def query_hr_documents(question: str):
    # Initialize embeddings
    embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        collection_name="hr_documents",
        embedding_function=embedding
    )

    docs = vectorstore.similarity_search(
        query=question,
        k=3
    )

    context = "\n\n".join([d.page_content for d in docs])

    llm = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        temperature=1.0
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

    return {"answer": answer}