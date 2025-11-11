# file_loader.py
import os
import docx2txt
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

def load_pdf(file_path):
    """Load PDF with error handling and metadata extraction"""
    try:
        text = ""
        reader = PdfReader(file_path)
        metadata = {
            "source": os.path.basename(file_path),
            "page_count": len(reader.pages),
            "file_type": "pdf"
        }
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text.strip():
                text += f"Page {page_num + 1}: {page_text}\n"
        
        return text, metadata
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        return "", {"source": os.path.basename(file_path), "error": str(e)}

def load_docx(file_path):
    """Load DOCX file with error handling"""
    try:
        text = docx2txt.process(file_path)
        return text, {
            "source": os.path.basename(file_path),
            "file_type": "docx"
        }
    except Exception as e:
        logger.error(f"Error loading DOCX {file_path}: {str(e)}")
        return "", {"source": os.path.basename(file_path), "error": str(e)}

def load_txt(file_path):
    """Load text file with proper encoding handling"""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                text = f.read()
                return text, {
                    "source": os.path.basename(file_path),
                    "file_type": "txt",
                    "encoding": encoding
                }
        except UnicodeDecodeError:
            continue
    logger.error(f"Could not decode file: {file_path}")
    return "", {"source": os.path.basename(file_path), "error": "Encoding failed"}

def load_hr_documents(folder_path="./data/hr_docs"):
    """Load all HR documents with comprehensive error handling"""
    docs = []
    
    if not os.path.exists(folder_path):
        logger.error(f"Documents folder not found: {folder_path}")
        return docs
    
    supported_extensions = {'.pdf', '.docx', '.txt'}
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in supported_extensions:
            logger.warning(f"Skipping unsupported file type: {filename}")
            continue
        
        if file_ext == '.pdf':
            text, metadata = load_pdf(file_path)
        elif file_ext == '.docx':
            text, metadata = load_docx(file_path)
        elif file_ext == '.txt':
            text, metadata = load_txt(file_path)
        
        if text and text.strip():
            docs.append(Document(
                page_content=text.strip(),
                metadata=metadata
            ))
            logger.info(f"✅ Loaded: {filename} ({len(text)} characters)")
        else:
            logger.warning(f"⚠️ Empty or failed to load: {filename}")
    
    logger.info(f"📊 Total documents loaded: {len(docs)}")
    return docs

def split_documents(docs, chunk_size=500, chunk_overlap=100):
    """Split documents with configurable parameters"""
    if not docs:
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    
    split_docs = splitter.split_documents(docs)
    logger.info(f"📄 Split {len(docs)} docs into {len(split_docs)} chunks")
    return split_docs