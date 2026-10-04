const messagesEl = document.querySelector("#messages");
const formEl = document.querySelector("#chat-form");
const inputEl = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const statusPill = document.querySelector("#status-pill");
const intentValue = document.querySelector("#intent-value");
const userValue = document.querySelector("#user-value");
const ticketValue = document.querySelector("#ticket-value");
const stateView = document.querySelector("#state-view");

let conversation = [];

function addMessage(role, content) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "U" : "A";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;

  article.append(avatar, bubble);
  messagesEl.append(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  sendButton.textContent = isBusy ? "处理中" : "发送";
}

function updateInspector(payload) {
  intentValue.textContent = payload.intent || "unknown";
  userValue.textContent = payload.state?.user_id || "无";
  ticketValue.textContent = payload.state?.ticket_id || "无";
  stateView.textContent = JSON.stringify(payload.state || {}, null, 2);
}

async function checkHealth() {
  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    statusPill.textContent = "后端已连接";
    statusPill.className = "status-pill ok";
  } catch (error) {
    statusPill.textContent = "后端未连接";
    statusPill.className = "status-pill error";
  }
}

async function sendMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) return;

  addMessage("user", trimmed);
  inputEl.value = "";
  setBusy(true);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed, conversation }),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const payload = await res.json();
    conversation = payload.state?.conversation || [
      ...conversation,
      { role: "user", content: trimmed },
      { role: "assistant", content: payload.response },
    ];
    addMessage("assistant", payload.response || "暂无回复");
    updateInspector(payload);
  } catch (error) {
    addMessage("assistant", `请求失败：${error.message}`);
  } finally {
    setBusy(false);
    inputEl.focus();
  }
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(inputEl.value);
});

document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => {
    sendMessage(button.dataset.message || "");
  });
});

checkHealth();
