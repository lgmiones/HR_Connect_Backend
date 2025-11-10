"""
Initialize ChromaDB with HR Policy Documents

This script loads HR policy documents into the ChromaDB vector store.
Place your HR documents in the docs/hr_policies/ directory before running.
"""
import os
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ai.vector_store import get_vector_store
from app.core.config import settings

# Import document loaders
try:
    from PyPDF2 import PdfReader
    import docx
except ImportError:
    print("Please install required packages: pip install PyPDF2 python-docx")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> str:
    """Load text from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        return ""


def load_docx(file_path: str) -> str:
    """Load text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error loading DOCX {file_path}: {str(e)}")
        return ""


def load_txt(file_path: str) -> str:
    """Load text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading TXT {file_path}: {str(e)}")
        return ""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # Only break if we're at least halfway
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def load_documents_from_directory(directory: str) -> dict:
    """
    Load all documents from a directory
    
    Args:
        directory: Path to directory containing documents
        
    Returns:
        Dictionary mapping filename to text content
    """
    documents = {}
    
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return documents
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        logger.info(f"Loading document: {filename}")
        
        if filename.endswith('.pdf'):
            text = load_pdf(file_path)
        elif filename.endswith('.docx'):
            text = load_docx(file_path)
        elif filename.endswith('.txt'):
            text = load_txt(file_path)
        else:
            logger.warning(f"Unsupported file type: {filename}")
            continue
        
        if text:
            documents[filename] = text
            logger.info(f"Loaded {len(text)} characters from {filename}")
    
    return documents


def initialize_vector_database():
    """Initialize ChromaDB with HR policy documents"""
    logger.info("Starting ChromaDB initialization...")
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Load documents
    docs_directory = "docs/hr_policies"
    documents = load_documents_from_directory(docs_directory)
    
    if not documents:
        logger.warning("No documents found. Creating sample documents...")
        create_sample_documents(docs_directory)
        documents = load_documents_from_directory(docs_directory)
    
    # Process and add documents to vector store
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    for filename, content in documents.items():
        logger.info(f"Processing {filename}...")
        
        # Chunk the document
        chunks = chunk_text(content)
        
        # Create metadata and IDs for each chunk
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": filename,
                "chunk_id": i,
                "total_chunks": len(chunks)
            })
            all_ids.append(f"{filename}_chunk_{i}")
    
    # Add to vector store
    if all_chunks:
        logger.info(f"Adding {len(all_chunks)} chunks to vector store...")
        vector_store.add_documents(
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids
        )
        logger.info("✓ ChromaDB initialization complete!")
        logger.info(f"Total documents: {len(documents)}")
        logger.info(f"Total chunks: {len(all_chunks)}")
    else:
        logger.error("No chunks to add to vector store")


def create_sample_documents(directory: str):
    """Create sample HR policy documents"""
    os.makedirs(directory, exist_ok=True)
    
    # Sample Leave Policy
    leave_policy = """
    LEAVE POLICY
    
    Annual Leave Entitlement:
    All employees are entitled to 15 days of annual leave per year. Leave credits are
    earned monthly and can be used after probation period.
    
    Types of Leave:
    1. Annual Leave - 15 days per year
    2. Sick Leave - 10 days per year
    3. Emergency Leave - 5 days per year
    4. Maternity Leave - 60 days (for female employees)
    5. Paternity Leave - 7 days (for male employees)
    
    Leave Application Process:
    1. Log in to HRConnect system
    2. Navigate to Leave Management
    3. Click "File Leave Request"
    4. Select leave type and dates
    5. Provide reason for leave
    6. Submit for approval
    
    Leave Approval:
    - Leave requests must be submitted at least 3 days in advance
    - Immediate supervisor approval required
    - HR will verify leave credits
    - Approved leave will reflect in your leave balance
    
    Unused Leave:
    - Unused annual leave can be carried over up to 5 days
    - Unused leave may be converted to cash at year-end (subject to policy)
    
    Contact HR for questions: hr@company.com
    """
    
    # Sample FAQs
    faqs = """
    HR FREQUENTLY ASKED QUESTIONS
    
    Q: How do I check my remaining leave balance?
    A: Log in to HRConnect and ask the chatbot "What is my leave balance?" or 
    navigate to the Leave Management dashboard.
    
    Q: Can I file leave on weekends?
    A: No, leave can only be filed for regular working days.
    
    Q: What happens if I get sick during my leave?
    A: File a sick leave and provide a medical certificate. Your annual leave
    will be converted to sick leave.
    
    Q: How do I cancel my leave request?
    A: Contact your supervisor and HR immediately. Cancellation is subject to
    approval and timing.
    
    Q: Can I use my leave credits before they are earned?
    A: No, leave credits must be earned before they can be used.
    
    Q: What is the difference between annual and sick leave?
    A: Annual leave is for planned time off. Sick leave requires medical
    documentation and is for health-related absences.
    
    Q: How do I file an emergency leave?
    A: Notify your supervisor immediately and file through HRConnect as soon
    as possible with supporting documents.
    """
    
    # Write sample documents
    with open(os.path.join(directory, "leave_policy.txt"), "w") as f:
        f.write(leave_policy)
    
    with open(os.path.join(directory, "faqs.txt"), "w") as f:
        f.write(faqs)
    
    logger.info("Sample documents created")


if __name__ == "__main__":
    initialize_vector_database()
