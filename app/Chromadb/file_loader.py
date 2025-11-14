# file_loader.py
import os
import docx2txt
import logging
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def load_pdf(file_path: str):
    try:
        reader = PdfReader(file_path)
        text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                # avoid verbose "Page X:" unless you want it
                text.append(page_text)
        content = "\n\n".join(text).strip()
        metadata = {"source": os.path.basename(file_path), "file_type": "pdf", "page_count": len(reader.pages)}
        return content, metadata
    except Exception as e:
        logger.error("Error loading PDF %s: %s", file_path, e)
        return "", {"source": os.path.basename(file_path), "error": str(e)}

def load_docx(file_path: str):
    try:
        text = docx2txt.process(file_path) or ""
        return text.strip(), {"source": os.path.basename(file_path), "file_type": "docx"}
    except Exception as e:
        logger.error("Error loading DOCX %s: %s", file_path, e)
        return "", {"source": os.path.basename(file_path), "error": str(e)}

def load_txt(file_path: str):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                text = f.read()
                return text.strip(), {"source": os.path.basename(file_path), "file_type": "txt", "encoding": enc}
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error("Error reading TXT %s: %s", file_path, e)
            break
    logger.error("Could not decode file: %s", file_path)
    return "", {"source": os.path.basename(file_path), "error": "Encoding failed"}

def load_hr_documents(folder_path: str = "./data/hr_docs"):
    docs = []
    if not os.path.exists(folder_path):
        logger.error("Documents folder not found: %s", folder_path)
        return docs

    supported = {'.pdf', '.docx', '.txt'}
    for filename in os.listdir(folder_path):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in supported:
            logger.warning("Skipping unsupported file type: %s", filename)
            continue

        path = os.path.join(folder_path, filename)
        if file_ext == '.pdf':
            text, metadata = load_pdf(path)
        elif file_ext == '.docx':
            text, metadata = load_docx(path)
        else:
            text, metadata = load_txt(path)

        if text:
            docs.append(Document(page_content=text, metadata=metadata))
            logger.info("Loaded %s (%d chars)", filename, len(text))
        else:
            logger.warning("Empty/failed to load: %s", filename)

    logger.info("Total documents loaded: %d", len(docs))
    return docs


def split_documents(docs, chunk_size=500, chunk_overlap=100):
    if not docs:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    split_docs = splitter.split_documents(docs)
    logger.info("Split %d documents into %d chunks", len(docs), len(split_docs))
    return split_docs