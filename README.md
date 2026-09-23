# Ruang Halal RAG Chatbot

Prototype chatbot **Retrieval-Augmented Generation (RAG)** untuk menjawab pertanyaan seputar Ruang Halal. Aplikasi mengambil knowledge yang paling relevan dari TiDB Cloud, lalu menggunakan Groq untuk menyusun jawaban dalam bahasa Indonesia.

> Status: prototype/demo. Project ini belum dirancang sebagai sistem production.

## Fitur

- API FastAPI dengan endpoint `POST /chat`.
- Retrieval dokumen berbasis cosine similarity.
- Embedding menggunakan `BAAI/bge-m3`.
- Jawaban LLM melalui Groq model `openai/gpt-oss-20b`.
- Knowledge base dari file CSV ke tabel `documents` TiDB.
- Frontend demo vanilla HTML, CSS, dan JavaScript.
- Unit test terisolasi yang tidak memerlukan internet, API key, atau TiDB asli.

## Arsitektur singkat

```text
Browser / Frontend
        |
        | POST /chat { "message": "..." }
        v
      FastAPI
        |
        +--> BGE-M3 membuat embedding pertanyaan
        |
        +--> TiDB mengambil dokumen dan menghitung cosine similarity
        |
        +--> Groq menyusun jawaban dari context hasil retrieval
        v
{ "response": "..." }
```

## Struktur project

```text
RAG_TiDB/
├── api.py                 # FastAPI dan endpoint API
├── chat_bot.py            # Retrieval, TiDB, dan Groq
├── config.py              # Konfigurasi dari environment variable
├── knowledge_embed.py     # Import CSV dan pembuatan embedding ke TiDB
├── data_knowledge.csv     # Dataset knowledge base
├── index.html             # Frontend demo
├── style.css
├── script.js
├── requirements.txt       # Dependency aplikasi
├── requirements-test.txt  # Dependency test
└── tests/                 # Unit test pytest
```

## Prasyarat

- Python 3.10 atau lebih baru.
- Akun dan API key Groq.
- Database TiDB Cloud yang dapat diakses.
- Tabel `documents` pada database TiDB.
- Git, bila ingin clone atau push project ke GitHub.

## Instalasi

### 1. Clone repository

```powershell
git clone <URL_REPOSITORY_ANDA>
cd RAG_TiDB
```

### 2. Buat dan aktifkan virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Gunakan nama `.venv`, bukan `.env`, agar tidak tertukar dengan file konfigurasi environment.

### 3. Install dependency aplikasi

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Konfigurasi environment variable

Project ini membaca credential dari environment variable, bukan dari source code. Isi nilai berikut dengan credential milik Anda sendiri di PowerShell yang sama:

```powershell
$env:GROQ_API_KEY = "GROQ_API_KEY_ANDA"
$env:TIDB_HOST = "HOST_TIDB_ANDA"
$env:TIDB_PORT = "4000"
$env:TIDB_USER = "USER_TIDB_ANDA"
$env:TIDB_PASSWORD = "PASSWORD_TIDB_ANDA"
$env:TIDB_DATABASE = "RAG"
$env:TIDB_SSL_CA = "$PWD\isrgrootx1.pem"
```

Variabel yang digunakan:

| Variabel | Wajib | Keterangan |
| --- | --- | --- |
| `GROQ_API_KEY` | Ya | API key untuk client Groq. |
| `TIDB_HOST` | Ya | Host koneksi TiDB Cloud. |
| `TIDB_PORT` | Tidak | Port TiDB; default `4000`. |
| `TIDB_USER` | Ya | Username TiDB. |
| `TIDB_PASSWORD` | Ya | Password TiDB. |
| `TIDB_DATABASE` | Tidak | Nama database; default `RAG`. |
| `TIDB_SSL_CA` | Tidak | Lokasi sertifikat CA; default `isrgrootx1.pem`. |

Jangan menaruh credential di `config.py`, jangan commit credential ke GitHub, dan jangan membagikannya melalui issue atau log.

## Menyiapkan database dan knowledge base

Jika belum ada, buat tabel `documents` pada database TiDB:

```sql
CREATE TABLE documents (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    text TEXT NOT NULL,
    embedding JSON NOT NULL
);
```

Dataset harus memiliki kolom `question` dan `answer`, seperti pada `data_knowledge.csv`.

Untuk membangun ulang embedding dari CSV:

```powershell
python knowledge_embed.py
```

> Perintah ini menghapus isi tabel `documents` sebelum mengisi ulang data. Jalankan hanya pada database yang memang ditujukan untuk project ini.

## Menjalankan API

Aktifkan virtual environment dan pastikan seluruh environment variable sudah diisi, lalu jalankan:

```powershell
python -m uvicorn api:app --reload
```

API tersedia di:

- `http://127.0.0.1:8000`
- Dokumentasi interaktif: `http://127.0.0.1:8000/docs`

### Contoh request

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/chat" `
  -ContentType "application/json" `
  -Body '{"message":"Apa itu Ruang Halal?"}'
```

Contoh response sukses:

```json
{
  "response": "..."
}
```

Input kosong atau body yang tidak sesuai schema akan mendapat status `422`. Jika layanan RAG tidak tersedia, API mengembalikan status `503` dengan pesan aman tanpa detail credential.

## Menjalankan frontend demo

Jalankan API pada terminal pertama. Pada terminal kedua, dari root project, jalankan static server:

```powershell
python -m http.server 8080 --bind 127.0.0.1
```

Kemudian buka `http://127.0.0.1:8080` di browser. Frontend akan mengirim pertanyaan ke `http://127.0.0.1:8000/chat`.

## Unit testing

Install dependency test:

```powershell
python -m pip install -r requirements-test.txt
```

Jalankan seluruh unit test:

```powershell
pytest -v
```

Test menggunakan mock untuk SentenceTransformer, TiDB, dan Groq. Karena itu test tidak mengakses network, database cloud, ataupun Groq API asli.

## Troubleshooting

### `503 Service Unavailable` ketika memanggil `/chat`

Pastikan `GROQ_API_KEY`, `TIDB_HOST`, `TIDB_USER`, dan `TIDB_PASSWORD` sudah diisi di terminal yang menjalankan Uvicorn. Restart server setelah mengubah environment variable.

### Model embedding diunduh saat request pertama

Ini normal. `BAAI/bge-m3` dimuat secara lazy ketika retrieval pertama dipanggil. Koneksi internet diperlukan saat download model pertama kali; penggunaan berikutnya memanfaatkan cache lokal.

### Peringatan Hugging Face token

`HF_TOKEN` bersifat opsional. Token dapat digunakan untuk rate limit dan kecepatan download yang lebih baik, tetapi bukan penyebab kegagalan Groq atau TiDB.

### Port sudah digunakan

Ubah port Uvicorn, misalnya:

```powershell
python -m uvicorn api:app --reload --port 8001
```

Jika port API diubah, sesuaikan konstanta `endpoint` di `script.js`.

## Keamanan sebelum push ke GitHub

- Pastikan `.venv/`, `.env/`, cache Python, dan konfigurasi lokal tidak masuk commit.
- Jangan commit API key, password TiDB, atau file konfigurasi lokal.
- Gunakan GitHub Secrets atau environment variable pada platform deployment.
- Rotasi credential jika pernah tersimpan atau ter-push ke repository.

## License

Tambahkan lisensi yang sesuai sebelum repository dibuka untuk publik.
