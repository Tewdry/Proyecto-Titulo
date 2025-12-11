document.addEventListener("DOMContentLoaded", function () {
    const tabBtns = document.querySelectorAll(".perfil-tab-btn");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {

            // Desactivar todo
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".perfil-tab-pane").forEach(p => p.classList.remove("active"));

            // Activar botón
            btn.classList.add("active");

            // Activar panel objetivo
            const target = btn.getAttribute("data-target");
            const pane = document.querySelector(target);

            if (pane) {
                pane.classList.add("active");
            }
        });
    });
});


// ======================================================
// 2. LISTA DE SEGUIDORES / SIGUIENDO (Exclusivo de Perfil)
// ======================================================

function abrirListaSeguidores(perfilId) {
    abrirLista('seguidores', `/perfil/${perfilId}/seguidores/`);
}

function abrirListaSiguiendo(perfilId) {
    abrirLista('siguiendo', `/perfil/${perfilId}/siguiendo/`);
}

function abrirLista(tipo, url) {
    const modalEl = document.getElementById("seguidoresModal");
    if (!modalEl) return;

    // Usamos la instancia correcta de Bootstrap 5
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    
    const title = document.getElementById("seguidoresModalTitle");
    const content = document.getElementById("seguidoresModalContent");

    title.textContent = tipo === 'seguidores' ? "Seguidores" : "Siguiendo";
    content.innerHTML = "<p class='text-center text-white my-3'>Cargando...</p>";
    
    modal.show();

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (!data.usuarios || !data.usuarios.length) {
                content.innerHTML = "<p class='text-center my-3' style='color:#eafffb;'>Lista vacía.</p>";
                return;
            }

            content.innerHTML = data.usuarios.map(u => {
                let boton = "";
                
                // Si no soy yo mismo, muestro botón de seguir/dejar de seguir
                if (!u.es_mio) {
                    const clase = u.lo_sigo ? "btn-secondary" : "btn-outline-primary";
                    const texto = u.lo_sigo ? "Siguiendo" : "Seguir";
                    
                    boton = `
                        <button class="btn btn-sm ${clase}" onclick="toggleFollow(${u.id}, this)">
                            ${texto}
                        </button>
                    `;
                }

                return `
                    <div class="list-group-item d-flex align-items-center justify-content-between mb-2 rounded border-0 bg-transparent">
                        <div class="d-flex align-items-center gap-3">
                            <img src="${u.foto}" class="rounded-circle border border-secondary" width="45" height="45" style="object-fit:cover;">
                            <a href="/perfil/${u.id}/" class="text-white text-decoration-none fw-bold fs-6">
                                ${u.username}
                            </a>
                        </div>
                        ${boton}
                    </div>
                `;
            }).join("");
        })
        .catch((err) => {
            console.error(err);
            content.innerHTML = "<p class='text-center text-danger'>Error al cargar la lista.</p>";
        });
}