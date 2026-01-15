import os
from pathlib import Path
from typing import List, Dict
from PyPDF2 import PdfReader
from docx import Document
import markdown


class DocumentIngestionService:
    """Service for ingesting and processing documents"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.markdown'}
    
    def __init__(self, documents_path: str = "./data/documents"):
        self.documents_path = Path(documents_path)
        self.documents_path.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF {file_path}: {str(e)}")
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX {file_path}: {str(e)}")
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading TXT {file_path}: {str(e)}")
    
    def extract_text_from_markdown(self, file_path: Path) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            # Convert markdown to plain text (remove formatting)
            html = markdown.markdown(md_content)
            # Simple HTML tag removal (basic implementation)
            import re
            text = re.sub(r'<[^>]+>', '', html)
            return text
        except Exception as e:
            raise Exception(f"Error reading Markdown {file_path}: {str(e)}")
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text based on file extension"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif suffix == '.docx':
            return self.extract_text_from_docx(file_path)
        elif suffix in ['.txt']:
            return self.extract_text_from_txt(file_path)
        elif suffix in ['.md', '.markdown']:
            return self.extract_text_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap  # Overlap for context
        
        return chunks
    
    def ingest_file(self, file_path: Path) -> Dict:
        """Ingest a single file and return metadata"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        return {
            "filename": file_path.name,
            "file_type": file_path.suffix,
            "size": len(text),
            "chunks": chunks,
            "metadata": {
                "path": str(file_path),
                "num_chunks": len(chunks)
            }
        }
    
    def ingest_directory(self, directory: Path = None) -> List[Dict]:
        """Ingest all supported files from a directory"""
        if directory is None:
            directory = self.documents_path
        
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        ingested_files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    result = self.ingest_file(file_path)
                    ingested_files.append(result)
                except Exception as e:
                    print(f"Error ingesting {file_path}: {str(e)}")
                    continue
        
        return ingested_files
