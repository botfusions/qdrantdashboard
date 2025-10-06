"""
Embedding Service for Document Processing
Uses HuggingFace Sentence Transformers for free local embeddings
"""

import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer

# Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks


class EmbeddingService:
    """Generate embeddings for documents"""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize embedding model"""
        print(f"[*] Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"[*] Model loaded. Embedding dimension: {self.embedding_dim}")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction error: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction error: {str(e)}")

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"TXT extraction error: {str(e)}")

    def extract_text(self, file_path: str, file_extension: str) -> str:
        """Extract text based on file extension"""
        extractors = {
            '.pdf': self.extract_text_from_pdf,
            '.docx': self.extract_text_from_docx,
            '.doc': self.extract_text_from_docx,
            '.txt': self.extract_text_from_txt
        }

        extractor = extractors.get(file_extension.lower())
        if not extractor:
            raise ValueError(f"Unsupported file type: {file_extension}")

        return extractor(file_path)

    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
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

                if break_point > chunk_size * 0.5:  # At least 50% of chunk
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if c]  # Remove empty chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def process_document(self, file_path: str, file_extension: str) -> Dict:
        """
        Process document: extract text, chunk, and generate embeddings

        Returns:
        {
            "text": "full text",
            "chunks": ["chunk1", "chunk2", ...],
            "embeddings": [[vec1], [vec2], ...],
            "metadata": {
                "num_chunks": int,
                "embedding_dim": int
            }
        }
        """
        # Extract text
        text = self.extract_text(file_path, file_extension)

        if not text:
            raise ValueError("No text extracted from document")

        # Chunk text
        chunks = self.chunk_text(text)

        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)

        return {
            "text": text,
            "chunks": chunks,
            "embeddings": embeddings,
            "metadata": {
                "num_chunks": len(chunks),
                "embedding_dim": self.embedding_dim,
                "total_chars": len(text)
            }
        }


# Global instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
