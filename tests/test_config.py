from pathlib import Path
import re

import config


def test_groq_model_matches_the_supported_model():
    assert config.GROQ_MODEL == "openai/gpt-oss-20b"


def test_groq_api_key_is_optional_at_import_time_and_never_printed():
    assert config.GROQ_API_KEY is None or isinstance(config.GROQ_API_KEY, str)


def test_credentials_are_read_from_environment_not_hardcoded():
    source = Path("config.py").read_text(encoding="utf-8")
    assert 'GROQ_API_KEY = os.getenv("GROQ_API_KEY")' in source
    assert 'TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")' in source


def test_source_files_do_not_assign_literal_database_passwords():
    for filename in ("config.py", "chat_bot.py", "knowledge_embed.py"):
        source = Path(filename).read_text(encoding="utf-8")
        assert not re.search(r"password\s*=\s*['\"]", source, flags=re.IGNORECASE)
