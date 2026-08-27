const input = document.getElementById("input");
const messages = document.getElementById("messages");

function usePrompt(text) {
  input.value = text;
  send();
}

function addMessage(text, who="assistant") {
  const wrap = document.createElement("div");
  wrap.className = `msg ${who}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text;
  wrap.appendChild(bubble);
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

function clearChat() {
  messages.innerHTML = '<div class="msg assistant"><div class="bubble">Chat cleared. What would you like to know?</div></div>';
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function send() {
  const q = input.value.trim();
  if (!q) return;
  addMessage(esc(q), "user");
  input.value = "";
  addMessage("Thinking…", "assistant");
  const thinking = messages.lastElementChild;
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message:q})
    });
    const data = await r.json();
    thinking.remove();
    if (!r.ok) throw new Error(data.error || "Request failed");
    let html = `<div class="intent">${esc(data.intent)}</div><div>${esc(data.answer || "")}</div>`;

    if (data.source) html += `<small class="meta">FAQ match: ${esc(data.source)} • Similarity: ${data.score}</small>`;

    if (data.products) {
      html += `<div class="product-grid">${data.products.map(p => `
        <div class="product">
          <b>${esc(p.product_name)}</b>
          <small>${esc(p.brand)} • ${esc(p.category)}</small>
          <strong>₹${Number(p.price).toLocaleString("en-IN")}</strong>
          <p>${esc(p.description)}</p>
          <em>Match ${Number(p.similarity).toFixed(2)}</em>
        </div>`).join("")}</div>`;
    }

    if (data.counts) {
      html += `<div class="sentiments">
        <span>Positive <b>${data.counts.Positive||0}</b></span>
        <span>Neutral <b>${data.counts.Neutral||0}</b></span>
        <span>Negative <b>${data.counts.Negative||0}</b></span>
      </div>`;
    }
    addMessage(html, "assistant");
  } catch (e) {
    thinking.remove();
    addMessage(`<b>Connection issue.</b> ${esc(e.message)}<br><small>Make sure Flask is running. Ollama is optional; without it the app uses fallback responses.</small>`, "assistant");
  }
}
