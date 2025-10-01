import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

PDF_FOLDER = os.getenv("PDF_FOLDER", "pdfs/")
DATA_FOLDER = os.getenv("DATA_FOLDER", "data/")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", 3))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.25))

TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 300))

PDF_DOCUMENTS = {
    "shopify-privacy policy.pdf": "Privacy Policy",
    "shopify-terms of services.pdf": "Terms of Service"
}

REFUND_PERCENTAGE = float(os.getenv("REFUND_PERCENTAGE", 0.8))