from fastapi.testclient import TestClient

import api


def test_home_returns_service_status():
    client = TestClient(api.app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Ruang Halal AI Assistant API is running"}


def test_chat_returns_response_when_query_is_valid(monkeypatch):
    monkeypatch.setattr(api, "response_query", lambda query: f"Jawaban untuk: {query}")
    client = TestClient(api.app)

    response = client.post("/chat", json={"message": "Apa itu Ruang Halal?"})

    assert response.status_code == 200
    assert response.json() == {"response": "Jawaban untuk: Apa itu Ruang Halal?"}


def test_chat_rejects_empty_or_whitespace_message():
    client = TestClient(api.app)

    assert client.post("/chat", json={"message": ""}).status_code == 422
    assert client.post("/chat", json={"message": "   "}).status_code == 422


def test_chat_rejects_invalid_schema():
    client = TestClient(api.app)

    assert client.post("/chat", json={"question": "Apa itu Ruang Halal?"}).status_code == 422


def test_chat_returns_safe_error_payload_when_rag_fails(monkeypatch):
    def fail(*, query):
        raise RuntimeError("service unavailable")

    monkeypatch.setattr(api, "response_query", fail)
    client = TestClient(api.app)

    response = client.post("/chat", json={"message": "uji"})

    assert response.status_code == 503
    assert response.json() == {"error": "Layanan chatbot sedang tidak tersedia. Silakan coba lagi."}
