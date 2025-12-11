// ---------- ChatBot AthletIA ----------
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("chatbot-button");
  const modal = document.getElementById("chatbot-modal");
  const closeBtn = document.getElementById("chatbot-close");
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-message");
  const body = document.getElementById("chatbot-body");
  const resetBtn = document.getElementById("reset-chat");

  // ✅ Si el chatbot no está presente (usuario no logeado), no hace nada
  if (!btn || !modal || !closeBtn || !sendBtn || !input || !body || !resetBtn) return;

  // Mostrar / Ocultar modal
  btn.addEventListener("click", () => {
    modal.style.display = modal.style.display === "flex" ? "none" : "flex";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // Enviar mensaje
  async function enviarMensaje() {
    const mensaje = input.value.trim();
    if (!mensaje) return;

    agregarMensaje(`Tú: ${mensaje}`, "chat-user");
    input.value = "";

    // Detectar página actual para el contexto IA
    const contexto = window.location.pathname;
    agregarMensaje("⏳ Coach está pensando...", "text-muted");

    try {
      const resp = await fetch("/ia/chat_api/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mensaje: `${mensaje}\n(Contexto actual: ${contexto})`
        })
      });

      const data = await resp.json();
      const ultimo = body.lastChild;
      if (ultimo && ultimo.classList.contains("text-muted")) body.removeChild(ultimo);
      agregarMensaje(`Coach: ${data.respuesta}`, "chat-bot");
    } catch (e) {
      agregarMensaje("⚠️ Error al conectar con AthletIA Coach.", "chat-bot");
    }
  }

  sendBtn.addEventListener("click", enviarMensaje);
  input.addEventListener("keypress", e => {
    if (e.key === "Enter") enviarMensaje();
  });

  // Función para agregar mensajes
  function agregarMensaje(texto, clase) {
    const div = document.createElement("div");
    div.className = clase;
    div.innerHTML = texto;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  // Reiniciar conversación
  resetBtn.addEventListener("click", async () => {
    await fetch("/ia/chat_api/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: "__reset__" })
    });
    body.innerHTML =
      "<div class='text-muted text-center'>💬 Conversación reiniciada. ¿En qué puedo ayudarte hoy?</div>";
  });
});
