from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from chat_bot import response_query


# ==============================
# FASTAPI
# ==============================

app = FastAPI(
    title="Ruang Halal AI Assistant API",
    description=(
        "API chatbot RAG Ruang Halal "
        "menggunakan Groq, BGE-M3, dan TiDB."
    ),
    version="1.0.0"
)


# ==============================
# CORS
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================
# REQUEST MODEL
# ==============================

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, pattern=r".*\S.*")


# ==============================
# HOME
# ==============================

@app.get("/")
def home():

    return {
        "message": (
            "Ruang Halal AI Assistant "
            "API is running"
        )
    }


# ==============================
# CHAT
# ==============================

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        response = response_query(
            query=request.message
        )

        return {
            "response": response
        }

    except Exception:

        return JSONResponse(
            status_code=503,
            content={
                "error": (
                    "Layanan chatbot sedang tidak tersedia. "
                    "Silakan coba lagi."
                )
            },
        )
