import json
import time

import mysql.connector
from sentence_transformers import SentenceTransformer
from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TIDB_DATABASE,
    TIDB_HOST,
    TIDB_PASSWORD,
    TIDB_PORT,
    TIDB_SSL_CA,
    TIDB_USER,
)


# ==============================
# EMBEDDER
# ==============================

embedder = None


def get_embedder():
    """
    Membuat model BGE-M3 hanya ketika
    proses retrieval membutuhkan embedding.
    """
    global embedder

    if embedder is None:
        embedder = SentenceTransformer("BAAI/bge-m3")

    return embedder


# ==============================
# GROQ CLIENT
# ==============================

llm_agent = None


def get_llm_agent():
    """
    Membuat client Groq ketika
    response membutuhkan LLM.
    """
    global llm_agent

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY belum ditemukan."
        )

    if llm_agent is None:
        llm_agent = Groq(
            api_key=GROQ_API_KEY
        )

    return llm_agent


# ==============================
# DATABASE CONNECTION
# ==============================

def create_database_connection():
    """
    Membuat koneksi ke TiDB Cloud.
    """

    if not all((TIDB_HOST, TIDB_USER, TIDB_PASSWORD)):
        raise RuntimeError(
            "Konfigurasi TiDB belum lengkap. "
            "Set TIDB_HOST, TIDB_USER, dan TIDB_PASSWORD."
        )

    db = mysql.connector.connect(
        host=TIDB_HOST,
        port=TIDB_PORT,
        user=TIDB_USER,
        password=TIDB_PASSWORD,
        database=TIDB_DATABASE,
        ssl_ca=TIDB_SSL_CA,
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )

    return db


# ==============================
# SEARCH DOCUMENT
# ==============================

def search_document(query, k_top=3):
    """
    Mencari dokumen paling relevan
    berdasarkan cosine similarity.
    """

    start_time = time.time()

    db = None
    curr = None

    try:

        # ==========================
        # EMBEDDING QUERY
        # ==========================

        query_embedding = (
            get_embedder()
            .encode(query)
            .tolist()
        )

        # ==========================
        # DATABASE
        # ==========================

        db = create_database_connection()

        curr = db.cursor()

        curr.execute(
            "SELECT text, embedding FROM documents"
        )

        rows = curr.fetchall()

        results = []

        # ==========================
        # COSINE SIMILARITY
        # ==========================

        query_norm = sum(
            q * q
            for q in query_embedding
        ) ** 0.5

        for text, embedding_json in rows:

            embedding = json.loads(
                embedding_json
            )

            dot_product = sum(
                q * d
                for q, d in zip(
                    query_embedding,
                    embedding
                )
            )

            document_norm = sum(
                d * d
                for d in embedding
            ) ** 0.5

            if (
                query_norm == 0
                or document_norm == 0
            ):
                similarity = 0

            else:
                similarity = (
                    dot_product
                    / (
                        query_norm
                        * document_norm
                    )
                )

            results.append(
                {
                    "text": text,
                    "similarity": similarity
                }
            )

        # ==========================
        # SORTING
        # ==========================

        results.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        # ==========================
        # TOP K
        # ==========================

        top_results = results[:k_top]

        retrieval_time = (
            time.time()
            - start_time
        )

        print(
            f"Retrieval: "
            f"{retrieval_time:.2f} detik"
        )

        return top_results

    finally:

        if curr:
            curr.close()

        if db:
            db.close()


# ==============================
# RESPONSE QUERY
# ==============================

def response_query(query):
    """
    Menghasilkan jawaban chatbot
    berdasarkan hasil retrieval dan Groq.
    """

    total_start = time.time()

    # ==========================
    # RETRIEVAL
    # ==========================

    docs = search_document(
        query,
        k_top=3
    )

    # ==========================
    # CONTEXT
    # ==========================

    context = "\n\n".join(
        doc["text"]
        for doc in docs
    )

    # ==========================
    # PROMPT
    # ==========================

    prompt = f"""
Context:

{context}

Pertanyaan:

{query}
"""

    # ==========================
    # GROQ
    # ==========================

    llm_start = time.time()

    response = (
        get_llm_agent()
        .chat
        .completions
        .create(
            model=GROQ_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": """
Kamu adalah AI Assistant Ruang Halal.

Jawab pertanyaan berdasarkan context
yang diberikan.

Aturan:
- Gunakan bahasa Indonesia.
- Jawab secara singkat dan jelas.
- Gunakan hanya informasi yang tersedia
  dalam context.
- Jangan membuat informasi baru.
- Jika informasi tidak tersedia dalam context,
  katakan bahwa informasi tersebut
  tidak tersedia.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_completion_tokens=80,

            reasoning_effort="low",

            include_reasoning=False
        )
    )

    answer = (
        response
        .choices[0]
        .message
        .content
    )

    # ==========================
    # TIMING
    # ==========================

    llm_time = (
        time.time()
        - llm_start
    )

    total_time = (
        time.time()
        - total_start
    )

    print(
        f"LLM: {llm_time:.2f} detik"
    )

    print(
        f"Total: {total_time:.2f} detik"
    )

    return answer


# ==============================
# TEST CHATBOT
# ==============================

if __name__ == "__main__":

    while True:

        query = input("\nUser: ")

        if query.lower() == "stop":

            print(
                "Chatbot dihentikan."
            )

            break

        try:

            response = response_query(
                query
            )

            print(
                "\nAI:",
                response
            )

        except Exception as e:

            print(
                "\nError:",
                e
            )
