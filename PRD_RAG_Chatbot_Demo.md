# Product Requirements Document (PRD)

# RAG Chatbot Demo Website

## 1. Informasi Produk

### Nama Produk
Ruang Halal AI Assistant

### Jenis Produk
Website Demo / Prototype

### Platform
Web Browser

### Status
Prototype / Demo

### Tujuan
Membuat website prototype yang mengintegrasikan chatbot berbasis Retrieval-Augmented Generation (RAG) untuk membantu pengguna memperoleh informasi mengenai Ruang Halal secara interaktif.

---

# 2. Latar Belakang

Ruang Halal merupakan platform yang menyediakan layanan dan informasi berkaitan dengan ekosistem halal. Untuk membantu pengguna memperoleh informasi secara lebih cepat, dibuat sebuah chatbot berbasis Artificial Intelligence yang dapat menjawab pertanyaan berdasarkan knowledge base yang telah disiapkan.

Chatbot menggunakan pendekatan Retrieval-Augmented Generation (RAG). Pertanyaan pengguna diproses menggunakan model embedding BGE-M3, kemudian sistem mencari informasi yang relevan dari database TiDB. Informasi yang ditemukan digunakan sebagai context untuk Large Language Model (LLM) DeepSeek yang dijalankan melalui Ollama.

Website prototype dibuat sebagai media demonstrasi untuk memperlihatkan bagaimana chatbot dapat diintegrasikan ke dalam sebuah website.

---

# 3. Tujuan Produk

Tujuan utama prototype:

1. Menampilkan website sederhana yang merepresentasikan platform Ruang Halal.
2. Mengintegrasikan chatbot AI ke dalam website.
3. Memungkinkan pengguna mengajukan pertanyaan mengenai Ruang Halal.
4. Menampilkan jawaban chatbot secara langsung.
5. Mendemonstrasikan alur RAG dari pertanyaan pengguna hingga menghasilkan jawaban.
6. Menjadi prototype yang dapat digunakan ketika melakukan demo kepada calon client atau pihak perusahaan.

---

# 4. Target Pengguna

Prototype ditujukan untuk:

- Calon client.
- Pengunjung website.
- Tim internal perusahaan.
- Pihak yang ingin melihat demonstrasi teknologi AI.
- Pengguna yang membutuhkan informasi mengenai Ruang Halal.

---

# 5. Scope Produk

## 5.1 Fitur Utama

Prototype hanya mencakup fitur berikut:

### A. Landing Page

Halaman utama yang memperkenalkan Ruang Halal.

Komponen:

- Navbar
- Hero section
- Deskripsi singkat Ruang Halal
- Informasi layanan
- Keunggulan
- Call-to-action
- AI Chatbot

---

### B. AI Chatbot

Chatbot menjadi fitur utama prototype.

Pengguna dapat:

- Membuka chatbot.
- Menulis pertanyaan.
- Mengirim pertanyaan.
- Melihat jawaban AI.
- Mengirim pertanyaan berikutnya.
- Melihat riwayat percakapan selama halaman masih terbuka.

Contoh pertanyaan:

> Apa itu Ruang Halal?

> Apa saja layanan Ruang Halal?

> Bagaimana proses sertifikasi halal?

> Siapa yang dapat menggunakan layanan Ruang Halal?

> Apa manfaat sertifikasi halal?

---

### C. Integrasi API

Frontend website terhubung dengan backend FastAPI.

Endpoint:

```text
POST /chat