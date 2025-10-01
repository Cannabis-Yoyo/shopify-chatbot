import streamlit as st

# Load secrets from Streamlit
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_MODEL = st.secrets["GROQ_MODEL"]
PDF_FOLDER = st.secrets["PDF_FOLDER"]
DATA_FOLDER = st.secrets["DATA_FOLDER"]
EMBEDDING_MODEL = st.secrets["EMBEDDING_MODEL"]

CHUNK_SIZE = int(st.secrets["CHUNK_SIZE"])
CHUNK_OVERLAP = int(st.secrets["CHUNK_OVERLAP"])
SEARCH_TOP_K = int(st.secrets["SEARCH_TOP_K"])
SIMILARITY_THRESHOLD = float(st.secrets["SIMILARITY_THRESHOLD"])
TEMPERATURE = float(st.secrets["TEMPERATURE"])
MAX_TOKENS = int(st.secrets["MAX_TOKENS"])
REFUND_PERCENTAGE = float(st.secrets["REFUND_PERCENTAGE"])
