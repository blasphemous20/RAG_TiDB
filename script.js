const chatShell = document.querySelector('.chat-shell');
const chatForm = document.querySelector('#chatForm');
const chatInput = document.querySelector('#chatInput');
const messages = document.querySelector('#chatMessages');
const sendButton = document.querySelector('#sendButton');
const endpoint = 'http://127.0.0.1:8000/chat';

function openChat() {
  chatShell.classList.add('is-open');
  chatShell.setAttribute('aria-hidden', 'false');
  setTimeout(() => chatInput.focus(), 180);
}

function closeChat() {
  chatShell.classList.remove('is-open');
  chatShell.setAttribute('aria-hidden', 'true');
}

function addMessage(text, role, typing = false) {
  const item = document.createElement('div');
  item.className = `message ${role}-message${typing ? ' typing' : ''}`;
  const label = role === 'assistant' ? 'Ruang Halal AI' : 'Anda';
  item.innerHTML = `<span class="message-label">${label}</span><p></p>`;
  item.querySelector('p').textContent = text;
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message) return;

  addMessage(message, 'user');
  chatInput.value = '';
  chatInput.style.height = 'auto';
  sendButton.disabled = true;
  const pending = addMessage('Ruang Halal sedang menelusuri informasi…', 'assistant', true);

  try {
    const result = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const payload = await result.json().catch(() => ({}));
    if (!result.ok || payload.error) throw new Error(payload.error || 'Layanan belum dapat merespons.');
    pending.remove();
    addMessage(payload.response || 'Maaf, saya belum menemukan jawaban untuk pertanyaan tersebut.', 'assistant');
  } catch (error) {
    pending.remove();
    addMessage('Koneksi ke asisten belum tersedia. Pastikan layanan RAG berjalan di http://127.0.0.1:8000, lalu coba lagi.', 'assistant');
  } finally {
    sendButton.disabled = false;
    chatInput.focus();
  }
}

document.querySelectorAll('[data-open-chat]').forEach((button) => button.addEventListener('click', openChat));
document.querySelector('[data-close-chat]').addEventListener('click', closeChat);
chatShell.addEventListener('click', (event) => { if (event.target === chatShell) closeChat(); });
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && chatShell.classList.contains('is-open')) closeChat(); });
chatForm.addEventListener('submit', (event) => { event.preventDefault(); sendMessage(chatInput.value); });
chatInput.addEventListener('input', () => { chatInput.style.height = 'auto'; chatInput.style.height = `${Math.min(chatInput.scrollHeight, 92)}px`; });
chatInput.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); chatForm.requestSubmit(); } });
document.querySelectorAll('.suggestions button').forEach((button) => button.addEventListener('click', () => { openChat(); chatInput.value = button.textContent; chatForm.requestSubmit(); }));
