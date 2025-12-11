document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("quickchat-button");
    const panel = document.getElementById("quickchat-panel");
    const closeBtn = document.getElementById("qc-close");
    const list = document.getElementById("qc-conversations");

    if (!btn || !panel || !list) return;

    // ABRIR panel
    btn.addEventListener("click", () => {
        // Siempre abrir cargando
        panel.classList.add("open");
        cargarConversaciones();
    });

    // CERRAR panel
    closeBtn.addEventListener("click", () => {
        panel.classList.remove("open");
    });

    // ------ FUNCIÓN PARA CARGAR CONVERSACIONES ------
    function cargarConversaciones() {
        list.innerHTML = `
            <div class="text-muted text-center py-3">Cargando…</div>
        `;

        fetch("/mensajes/quick/")
            .then(res => res.json())
            .then(data => {
                if (!data.length) {
                    list.innerHTML = `
                        <p class="text-center text-muted mt-3">Aún no tienes mensajes.</p>
                    `;
                    return;
                }

                list.innerHTML = data.map(c => `
                    <div class="qc-item" onclick="window.location.href='/mensajes/${c.id}/'">
                        <img src="${c.foto}" class="qc-avatar">
                        <div>
                            <div class="qc-name">${c.usuario}</div>
                            <div class="qc-last">${c.ultimo}</div>
                        </div>
                        ${c.unread > 0 ? `<span class="qc-unread">${c.unread}</span>` : ""}
                    </div>
                `).join("");
            })
            .catch(() => {
                list.innerHTML = `
                    <p class="text-center text-danger mt-3">Error al cargar mensajes.</p>
                `;
            });
    }

});
