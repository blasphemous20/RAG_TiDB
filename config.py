import os

# ==============================
# GROQ
# ==============================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-20b"


# ==============================
# TIDB
# ==============================

TIDB_HOST = os.getenv("TIDB_HOST")
TIDB_PORT = int(os.getenv("TIDB_PORT", "4000"))
TIDB_USER = os.getenv("TIDB_USER")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_DATABASE = os.getenv("TIDB_DATABASE", "RAG")
TIDB_SSL_CA = os.getenv("TIDB_SSL_CA", "isrgrootx1.pem")
