import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import chat_bot


class EncodedVector(list):
    def tolist(self):
        return list(self)


def make_database(rows):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    database = MagicMock()
    database.cursor.return_value = cursor
    return database, cursor


def test_create_database_connection_uses_configuration(monkeypatch):
    connector = MagicMock()
    monkeypatch.setattr(chat_bot.mysql.connector, "connect", connector)
    monkeypatch.setattr(chat_bot, "TIDB_HOST", "test-host")
    monkeypatch.setattr(chat_bot, "TIDB_PORT", 4000)
    monkeypatch.setattr(chat_bot, "TIDB_USER", "test-user")
    monkeypatch.setattr(chat_bot, "TIDB_PASSWORD", "test-password")
    monkeypatch.setattr(chat_bot, "TIDB_DATABASE", "test-db")
    monkeypatch.setattr(chat_bot, "TIDB_SSL_CA", "test-ca.pem")

    chat_bot.create_database_connection()

    connector.assert_called_once_with(
        host="test-host", port=4000, user="test-user", password="test-password",
        database="test-db", ssl_ca="test-ca.pem", ssl_verify_cert=True,
        ssl_verify_identity=True,
    )


def test_search_document_ranks_results_and_honors_k_top(monkeypatch):
    rows = [
        ("orthogonal", json.dumps([0, 1])),
        ("best match", json.dumps([1, 0])),
        ("partial match", json.dumps([1, 1])),
        ("opposite", json.dumps([-1, 0])),
    ]
    database, cursor = make_database(rows)
    embedder = MagicMock()
    embedder.encode.return_value = EncodedVector([1, 0])
    monkeypatch.setattr(chat_bot, "get_embedder", lambda: embedder)
    monkeypatch.setattr(chat_bot, "create_database_connection", lambda: database)

    results = chat_bot.search_document("uji", k_top=3)

    assert [item["text"] for item in results] == ["best match", "partial match", "orthogonal"]
    assert len(results) == 3
    cursor.execute.assert_called_once_with("SELECT text, embedding FROM documents")
    cursor.close.assert_called_once()
    database.close.assert_called_once()


def test_search_document_returns_empty_when_no_documents(monkeypatch):
    database, cursor = make_database([])
    embedder = MagicMock()
    embedder.encode.return_value = EncodedVector([1, 0])
    monkeypatch.setattr(chat_bot, "get_embedder", lambda: embedder)
    monkeypatch.setattr(chat_bot, "create_database_connection", lambda: database)

    assert chat_bot.search_document("uji") == []
    cursor.close.assert_called_once()
    database.close.assert_called_once()


def test_search_document_handles_zero_vector_without_division_error(monkeypatch):
    database, _ = make_database([("dokumen", json.dumps([1, 2]))])
    embedder = MagicMock()
    embedder.encode.return_value = EncodedVector([0, 0])
    monkeypatch.setattr(chat_bot, "get_embedder", lambda: embedder)
    monkeypatch.setattr(chat_bot, "create_database_connection", lambda: database)

    results = chat_bot.search_document("uji")

    assert results == [{"text": "dokumen", "similarity": 0}]


def test_search_document_propagates_database_error_without_network_retry(monkeypatch):
    monkeypatch.setattr(chat_bot, "create_database_connection", MagicMock(side_effect=RuntimeError("db down")))
    monkeypatch.setattr(chat_bot, "get_embedder", MagicMock())

    with pytest.raises(RuntimeError, match="db down"):
        chat_bot.search_document("uji")


def test_response_query_builds_context_and_uses_configured_groq_model(monkeypatch):
    completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Jawaban teruji"))])
    client = MagicMock()
    client.chat.completions.create.return_value = completion
    monkeypatch.setattr(chat_bot, "search_document", lambda query, k_top: [{"text": "Dokumen A"}, {"text": "Dokumen B"}])
    monkeypatch.setattr(chat_bot, "get_llm_agent", lambda: client)
    monkeypatch.setattr(chat_bot, "GROQ_MODEL", "openai/gpt-oss-20b")

    answer = chat_bot.response_query("Apa layanan yang tersedia?")

    assert answer == "Jawaban teruji"
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == "openai/gpt-oss-20b"
    assert "Dokumen A\n\nDokumen B" in request["messages"][1]["content"]
    assert "Apa layanan yang tersedia?" in request["messages"][1]["content"]


def test_response_query_accepts_empty_retrieval_context(monkeypatch):
    completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Informasi tidak tersedia."))])
    client = MagicMock()
    client.chat.completions.create.return_value = completion
    monkeypatch.setattr(chat_bot, "search_document", lambda query, k_top: [])
    monkeypatch.setattr(chat_bot, "get_llm_agent", lambda: client)

    assert chat_bot.response_query("Pertanyaan baru") == "Informasi tidak tersedia."
    assert "Pertanyaan baru" in client.chat.completions.create.call_args.kwargs["messages"][1]["content"]


def test_response_query_propagates_groq_error(monkeypatch):
    client = MagicMock()
    client.chat.completions.create.side_effect = RuntimeError("groq unavailable")
    monkeypatch.setattr(chat_bot, "search_document", lambda query, k_top: [{"text": "Dokumen"}])
    monkeypatch.setattr(chat_bot, "get_llm_agent", lambda: client)

    with pytest.raises(RuntimeError, match="groq unavailable"):
        chat_bot.response_query("uji")
