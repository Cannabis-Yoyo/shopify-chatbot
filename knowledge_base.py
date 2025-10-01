import os
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import PyPDF2

class DocumentChunk:
    def __init__(self, content: str, metadata: dict, embedding: Optional[np.ndarray] = None):
        self.content = content
        self.metadata = metadata
        self.embedding = embedding

class RAGKnowledgeBase:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(model_name)
        self.chunks = []
        self.index = None
        self.chunk_size = 500
        self.overlap = 50

    def extract_pdf_text(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""

    def chunk_document(self, text: str, source: str) -> List[DocumentChunk]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunk = DocumentChunk(
                chunk_text, 
                {'source': source, 'chunk_id': len(chunks)}
            )
            chunks.append(chunk)
        return chunks

    def add_document(self, text: str, source: str):
        chunks = self.chunk_document(text, source)
        for chunk in chunks:
            embedding = self.embedding_model.encode([chunk.content])
            chunk.embedding = embedding[0]
        self.chunks.extend(chunks)
        self._rebuild_index()

    def add_pdf_document(self, pdf_path: str, source_name: str):
        text = self.extract_pdf_text(pdf_path)
        if text.strip():
            self.add_document(text, source_name)
            print(f"Added {source_name} to knowledge base")
        else:
            print(f"Failed to extract text from {source_name}")

    def _rebuild_index(self):
        if not self.chunks:
            return
        embeddings = np.array([chunk.embedding for chunk in self.chunks])
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

    def search(self, query: str, k: int = 3, similarity_threshold: float = 0.25):
        if not self.index or not self.chunks:
            return []
        
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, min(k, len(self.chunks)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= similarity_threshold:
                results.append((self.chunks[idx], float(score)))
        return results

    def load_pdf_folder(self, pdf_folder: str, pdf_mapping: dict):
        for filename, source_name in pdf_mapping.items():
            path = os.path.join(pdf_folder, filename)
            if os.path.exists(path):
                self.add_pdf_document(path, source_name)
            else:
                print(f"PDF not found: {path}")