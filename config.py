import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configurations
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "deepseek-r1-distill-llama-70b"

# Memory configurations
CHAT_HISTORY_DIR = "chat_histories"
VECTOR_STORE_DIR = "vector_stores"
EMBEDDING_DIM = 384  # Dimension for embeddings

# Create necessary directories
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
