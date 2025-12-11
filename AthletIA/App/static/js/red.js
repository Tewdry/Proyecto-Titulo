// ======================================================
// 1. UTILIDADES Y CONFIGURACIÓN GLOBAL
// ======================================================

// Variables Globales para Rutinas
let rutinasCache = null;
let rutinaSeleccionadaId = null;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Genera headers comunes
const getJsonHeaders = () => ({
    "X-CSRFToken": getCookie("csrftoken"),
    "Content-Type": "application/json",
    "Accept": "application/json"
});

// Función para retrasar ejecución (Debounce)
const debounce = (func, delay) => {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
};

// ======================================================
// 2. DOM READY (EVENT LISTENERS)
// ======================================================
document.addEventListener("DOMContentLoaded", () => {
    // Inicializar Tooltips
    [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(el => new bootstrap.Tooltip(el));

    // ------------------------------------------------------
    // A. Event Delegation para Filtros de Rutinas
    // ------------------------------------------------------
    document.body.addEventListener("click", (e) => {
        const btn = e.target.closest(".filter-rutina-btn");
        if (btn) {
            // Reset visual
            document.querySelectorAll(".filter-rutina-btn").forEach(b => {
                b.classList.remove("active", "btn-light");
                b.classList.add("btn-outline-light");
            });
            // Activar actual
            btn.classList.remove("btn-outline-light");
            btn.classList.add("active", "btn-light");
            
            aplicarFiltrosYOrden();
        }
    });

    // B. Select de Fecha
    const selectOrden = document.getElementById("ordenarRutinas");
    if (selectOrden) {
        selectOrden.addEventListener("change", () => aplicarFiltrosYOrden());
    }

    // C. Buscador con Debounce
    const inputBuscar = document.getElementById("buscadorRutinas");
    if (inputBuscar) {
        inputBuscar.addEventListener("input", debounce(() => {
            aplicarFiltrosYOrden();
        }, 300));
    }

    // D. Abrir Modal Rutinas
    const btnAbrir = document.getElementById("btnAbrirModalRutinas");
    if (btnAbrir) {
        btnAbrir.addEventListener("click", () => {
            const modalEl = document.getElementById("rutinasModal");
            if (!modalEl) return;
            
            bootstrap.Modal.getOrCreateInstance(modalEl).show();
            
            rutinaSeleccionadaId = null;
            const btnConf = document.getElementById("btnConfirmarCompartirRutina");
            if (btnConf) {
                btnConf.disabled = true;
                btnConf.textContent = "📤 Compartir en el muro";
            }

            // Cargar rutinas si no existen en caché
            if (!rutinasCache) {
                cargarRutinasUsuario();
            } else {
                renderizarRutinasModal(rutinasCache);
            }
        });
    }

    // E. Botón Confirmar Compartir
    const btnConfirmar = document.getElementById("btnConfirmarCompartirRutina");
    if (btnConfirmar) {
        btnConfirmar.addEventListener("click", () => {
            if (rutinaSeleccionadaId) compartirRutinaDesdeMuro(rutinaSeleccionadaId);
        });
    }

    // F. Crear Grupo
    const btnCrearGrupo = document.getElementById("btnAbrirCrearGrupo");
    if (btnCrearGrupo) {
        btnCrearGrupo.addEventListener("click", () => {
            const modalEl = document.getElementById("crearGrupoModal");
            if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl).show();
        });
    }
});


// ======================================================
// 3. LÓGICA DE RUTINAS (Cargar, Renderizar, Filtrar)
// ======================================================

function mostrarSkeletonRutinas(show) {
    const skeleton = document.getElementById("rutinasSkeleton");
    const contenedor = document.getElementById("rutinasListContainer");
    if (!skeleton) return;

    if (show) {
        skeleton.classList.remove("d-none");
        if (contenedor) contenedor.classList.add("d-none");
    } else {
        skeleton.classList.add("d-none");
        if (contenedor) contenedor.classList.remove("d-none");
    }
}

function cargarRutinasUsuario() {
    mostrarSkeletonRutinas(true);
    fetch("/muro/rutinas/list/")
        .then(res => res.json())
        .then(data => {
            rutinasCache = data || { propias: [], guardadas: [] };
            renderizarRutinasModal(rutinasCache);
            mostrarSkeletonRutinas(false);
        })
        .catch(err => {
            console.error(err);
            mostrarSkeletonRutinas(false);
            const contenedor = document.getElementById("rutinasListContainer");
            if (contenedor) contenedor.innerHTML = "<p class='text-center text-danger mt-3'>Error cargando rutinas.</p>";
        });
}

function renderizarRutinasModal(data) {
    const contenedor = document.getElementById("rutinasListContainer");
    if (!contenedor) return;

    contenedor.innerHTML = "";
    let todas = [];

    // Unificar Propias
    if (data.propias) {
        data.propias.forEach(r => {
            todas.push({
                id: r.id,
                nombre: r.nombre,
                descripcion: r.descripcion,
                fecha: r.fecha_creacion,
                tipo: 'propia',
                timestamp: new Date(r.fecha_creacion).getTime()
            });
        });
    }

    // Unificar Guardadas
    if (data.guardadas) {
        data.guardadas.forEach(r => {
            todas.push({
                id: r.rutina__id,
                nombre: r.rutina__nombre,
                descripcion: r.rutina__descripcion,
                fecha: r.rutina__fecha_creacion,
                tipo: 'guardada',
                timestamp: new Date(r.rutina__fecha_creacion).getTime()
            });
        });
    }

    if (todas.length === 0) {
        contenedor.innerHTML = "<p class='text-center text-muted mt-4'>No tienes rutinas disponibles.</p>";
        return;
    }

    // Generar HTML
    const html = todas.map(r => {
        const isSaved = r.tipo === 'guardada';
        return `
        <div class="rutina-item-card mb-2" 
             onclick="seleccionarRutina(this)"
             data-id="${r.id}" 
             data-nombre="${r.nombre}" 
             data-descripcion="${r.descripcion || ''}"
             data-tipo="${r.tipo}" 
             data-timestamp="${r.timestamp}">
             
            <div class="rutina-item-header">
                <span class="rutina-item-tag ${isSaved ? 'rutina-item-tag-guardada' : ''}">
                    ${isSaved ? '📦 Guardada' : '⭐ Propia'}
                </span>
                <span class="rutina-item-date text-muted small">
                    ${new Date(r.fecha).toLocaleDateString()}
                </span>
            </div>
            <h6 class="rutina-item-name mb-1 fw-bold text-white">${r.nombre}</h6>
            <p class="rutina-item-desc mb-0 text-muted small text-truncate">${r.descripcion || "Sin descripción."}</p>
        </div>`;
    }).join("");

    contenedor.innerHTML = html;
    aplicarFiltrosYOrden();
}

function aplicarFiltrosYOrden() {
    const contenedor = document.getElementById("rutinasListContainer");
    if (!contenedor) return;

    // Obtener valores UI
    const btnActivo = document.querySelector(".filter-rutina-btn.active");
    const filtroTipo = btnActivo ? btnActivo.getAttribute("data-filter") : "todas";
    const textoBusqueda = (document.getElementById("buscadorRutinas")?.value || "").toLowerCase().trim();
    const ordenFecha = document.getElementById("ordenarRutinas")?.value || "desc";

    let tarjetas = Array.from(contenedor.querySelectorAll(".rutina-item-card"));

    // Filtrar
    tarjetas.forEach(card => {
        const tipo = card.getAttribute("data-tipo");
        const nombre = (card.getAttribute("data-nombre") || "").toLowerCase();
        const desc = (card.getAttribute("data-descripcion") || "").toLowerCase();

        const matchTipo = (filtroTipo === "todas") || (filtroTipo === tipo);
        const matchTexto = !textoBusqueda || nombre.includes(textoBusqueda) || desc.includes(textoBusqueda);

        if (matchTipo && matchTexto) {
            card.classList.remove("d-none");
        } else {
            card.classList.add("d-none");
            if (card.classList.contains("selected")) card.classList.remove("selected");
        }
    });

    // Ordenar
    tarjetas.sort((a, b) => {
        const timeA = parseInt(a.getAttribute("data-timestamp") || "0");
        const timeB = parseInt(b.getAttribute("data-timestamp") || "0");
        return (ordenFecha === "desc") ? (timeB - timeA) : (timeA - timeB);
    });

    tarjetas.forEach(card => contenedor.appendChild(card));

    // Validar Botón Confirmar
    const visibleSelected = document.querySelector(".rutina-item-card.selected:not(.d-none)");
    const btn = document.getElementById("btnConfirmarCompartirRutina");
    if (btn && !visibleSelected) {
        rutinaSeleccionadaId = null;
        btn.disabled = true;
        btn.textContent = "📤 Compartir en el muro";
    }
}

function seleccionarRutina(card) {
    document.querySelectorAll(".rutina-item-card").forEach(c => c.classList.remove("selected"));
    card.classList.add("selected");
    rutinaSeleccionadaId = card.getAttribute("data-id");
    
    const btn = document.getElementById("btnConfirmarCompartirRutina");
    if (btn) {
        btn.disabled = false;
        btn.textContent = "📤 Compartir en el muro";
    }
}

function compartirRutinaDesdeMuro(rutinaId) {
    fetch("/muro/compartir-rutina/", {
        method: "POST",
        headers: getJsonHeaders(),
        body: JSON.stringify({ rutina_id: rutinaId, es_ia: false })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            Swal.fire("Publicado", "Rutina compartida.", "success").then(() => {
                const modalEl = document.getElementById("rutinasModal");
                if(modalEl) bootstrap.Modal.getOrCreateInstance(modalEl).hide();
                window.location.reload();
            });
        } else {
            Swal.fire("Error", data.error, "error");
        }
    })
    .catch(() => Swal.fire("Error", "Error de conexión.", "error"));
}


// ======================================================
// 4. COMENTARIOS
// ======================================================
function abrirComentariosModal(pubId) {
    const modalEl = document.getElementById("comentariosModal");
    if (!modalEl) return;

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();

    const form = document.getElementById("form-comentario-modal");
    if (form) {
        form.setAttribute("data-pubid", pubId);
        form.onsubmit = enviarComentarioDesdeMuro;
    }

    const cont = document.getElementById("comentariosModalContent");
    cont.innerHTML = "<p class='text-center my-3 text-white fw-bold'>⌛ Cargando comentarios...</p>";

    fetch(`/muro/${pubId}/comentarios/`)
        .then(res => res.json())
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) {
                cont.innerHTML = "<p class='text-center my-3 text-white fw-bold'>💬 ¡Sé el primero en comentar!</p>";
                return;
            }
            let html = "";
            data.forEach(c => {
                html += `
                  <div class="comment-item d-flex align-items-start mb-3">
                      <img src="${c.foto}" class="comment-avatar rounded-circle me-2" width="40" height="40">
                      <div class="flex-grow-1">
                          <div class="d-flex justify-content-between align-items-center">
                              <div class="d-flex gap-2 align-items-center">
                                  <span class="fw-bold">${c.usuario}</span>
                                  <span class="text-muted small">${c.fecha}</span>
                              </div>
                              <button class="btn btn-sm btn-outline-danger btn-report" onclick="reportarComentario(${c.id})">🚩</button>
                          </div>
                          <p class="mb-0 mt-1">${c.comentario}</p>
                      </div>
                  </div>`;
            });
            cont.innerHTML = html;
        })
        .catch(() => cont.innerHTML = "<p class='text-danger text-center'>Error cargando comentarios.</p>");
}

function enviarComentarioDesdeMuro(e) {
    e.preventDefault();
    const pubId = this.getAttribute("data-pubid");
    const contenido = (this.contenido.value || "").trim();
    if (!pubId || !contenido) return;

    const btn = this.querySelector("button[type=submit]");
    const txtOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "⌛";

    fetch(`/muro/${pubId}/comentario/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: "contenido=" + encodeURIComponent(contenido)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            Swal.fire("Error", data.error, "error");
        } else {
            const cont = document.getElementById("comentariosModalContent");
            const nuevo = `
              <div class="comment-item d-flex align-items-start mb-3">
                  <img src="${data.foto || '/media/avatar.png'}" class="comment-avatar rounded-circle me-2" width="40" height="40">
                  <div class="flex-grow-1">
                      <span class="fw-bold">${data.usuario}</span>
                      <span class="text-muted small ms-2">Ahora</span>
                      <p class="mb-0 mt-1">${data.comentario}</p>
                  </div>
              </div>`;
            cont.innerHTML = nuevo + cont.innerHTML;
            this.reset();
        }
    })
    .catch(() => Swal.fire("Error", "No se pudo comentar.", "error"))
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = txtOriginal;
    });
}

function reportarComentario(id) {
    if (!id) return;
    const modalEl = document.getElementById("comentariosModal");
    if(modalEl) bootstrap.Modal.getOrCreateInstance(modalEl).hide();

    Swal.fire({
        title: "Reportar", input: "textarea", showCancelButton: true, confirmButtonText: "Enviar"
    }).then(res => {
        if (!res.isConfirmed) return;
        fetch(`/comentario/${id}/reportar/`, {
            method: "POST", headers: getJsonHeaders(), body: JSON.stringify({ motivo: res.value })
        }).then(r => r.json()).then(d => d.success ? Swal.fire("Enviado", d.message, "success") : Swal.fire("Error", d.error, "error"));
    });
}


// ======================================================
// 5. LIKES Y FAVORITOS (OPTIMISTIC UI)
// ======================================================
function toggleLike(pubId, btn) {
    const countSpan = btn.querySelector(".like-count");
    const icon = btn.querySelector("i");
    const yaLike = btn.classList.contains("liked");
    let actual = parseInt(countSpan.textContent) || 0;

    if (yaLike) {
        btn.classList.remove("liked");
        icon.classList.replace("bi-heart-fill", "bi-heart");
        countSpan.textContent = Math.max(0, actual - 1);
    } else {
        btn.classList.add("liked");
        icon.classList.replace("bi-heart", "bi-heart-fill");
        countSpan.textContent = actual + 1;
    }

    fetch(`/muro/${pubId}/like/`, { method: "POST", headers: getJsonHeaders() })
    .then(res => {
        if(res.status === 401 || res.url.includes("login")) throw new Error("NO_LOGIN");
        if(!res.ok) throw new Error("HTTP");
        return res.json();
    })
    .then(d => { if(countSpan) countSpan.textContent = d.total_likes; })
    .catch(err => {
        if(yaLike) { btn.classList.add("liked"); icon.classList.replace("bi-heart", "bi-heart-fill"); }
        else { btn.classList.remove("liked"); icon.classList.replace("bi-heart-fill", "bi-heart"); }
        countSpan.textContent = actual;
        if(err.message === "NO_LOGIN") Swal.fire("Info", "Inicia sesión para dar like.", "info");
    });
}

function toggleFavorite(pubId, btn) {
    const icon = btn.querySelector("i");
    const count = btn.querySelector(".fav-count");
    const yaFav = btn.classList.contains("fav-active");
    let actual = parseInt(count.textContent) || 0;

    if(yaFav) {
        btn.classList.remove("fav-active");
        icon.classList.replace("bi-star-fill", "bi-star");
        count.textContent = Math.max(0, actual - 1);
    } else {
        btn.classList.add("fav-active");
        icon.classList.replace("bi-star", "bi-star-fill");
        count.textContent = actual + 1;
    }

    fetch(`/muro/${pubId}/favorite/`, { method: "POST", headers: getJsonHeaders() })
    .then(res => {
        if(res.status === 401 || res.url.includes("login")) throw new Error("NO_LOGIN");
        return res.json();
    })
    .then(d => {
        document.querySelectorAll(`.btn-fav[onclick*="${pubId}"]`).forEach(b => {
            b.querySelector(".fav-count").textContent = d.total_favorites;
            const i = b.querySelector("i");
            if(d.status === 'added') { b.classList.add("fav-active"); i.classList.replace("bi-star", "bi-star-fill"); }
            else { b.classList.remove("fav-active"); i.classList.replace("bi-star-fill", "bi-star"); }
        });
    })
    .catch(err => {
        if(yaFav) { btn.classList.add("fav-active"); icon.classList.replace("bi-star", "bi-star-fill"); }
        else { btn.classList.remove("fav-active"); icon.classList.replace("bi-star-fill", "bi-star"); }
        count.textContent = actual;
        if(err.message === "NO_LOGIN") Swal.fire("Info", "Inicia sesión para guardar.", "info");
    });
}

function toggleFollow(id, btn) {
    // 1. Bloquear botón temporalmente
    btn.disabled = true;
    
    fetch(`/toggle-follow/${id}/`, { method: "POST", headers: getJsonHeaders() })
    .then(r => r.json())
    .then(d => {
        if(d.siguiendo) {
            // --- AHORA LO SIGUES ---
            // 1. Quitar clases de "No siguiendo"
            btn.classList.remove("not-following", "btn-primary", "btn-athletia-primary");
            // 2. Agregar clase de "Siguiendo"
            btn.classList.add("following"); 
            // 3. Inyectar HTML específico para el efecto hover rojo
            btn.innerHTML = '<i class="bi bi-check-lg"></i> <span class="text-siguiendo">Siguiendo</span>';
        } else {
            // --- YA NO LO SIGUES ---
            // 1. Quitar clases de "Siguiendo"
            btn.classList.remove("following", "btn-secondary");
            // 2. Agregar clase de "No siguiendo"
            btn.classList.add("not-following");
            // 3. HTML simple de Seguir
            btn.innerHTML = '<i class="bi bi-person-plus-fill"></i> Seguir';
        }
    })
    .catch(err => {
        console.error(err);
        Swal.fire("Error", "No se pudo actualizar.", "error");
    })
    .finally(() => {
        // Desbloquear botón
        btn.disabled = false;
    });
}


// ======================================================
// 6. GRUPOS, ELIMINAR POST, ETC.
// ======================================================
function crearGrupo() {
    const nom = document.getElementById("grupoNombre").value;
    const desc = document.getElementById("grupoDescripcion").value;
    if(!nom) return Swal.fire("Info", "Falta nombre.", "info");

    fetch("/grupos/crear/", {
        method: "POST", headers: getJsonHeaders(), body: JSON.stringify({nombre: nom, descripcion: desc})
    }).then(r => r.json()).then(d => d.success ? window.location.href=`/grupos/${d.grupo_id}/` : Swal.fire("Error", d.error, "error"));
}

function unirseGrupo(id, btn) {
    fetch(`/grupos/${id}/unirse/`, { method: "POST", headers: getJsonHeaders() })
    .then(r => r.json())
    .then(d => {
        if(d.joined || d.reactivated) {
            Swal.fire("Éxito", d.message, "success");
            btn.textContent = "✓ Miembro";
            btn.disabled = true;
            btn.classList.replace("btn-athletia-primary", "btn-secondary");
        } else Swal.fire("Info", d.message, "info");
    });
}

function salirGrupo(id) {
    Swal.fire({title:"¿Salir?", showCancelButton:true, confirmButtonText:"Sí"}).then(r => {
        if(r.isConfirmed) fetch(`/grupos/${id}/salir/`, { method: "POST", headers: getJsonHeaders() })
            .then(res => res.json()).then(d => d.left_group ? window.location.reload() : Swal.fire("Info", d.message, "info"));
    });
}

function eliminarPublicacion(id) {
    Swal.fire({title:"¿Eliminar?", showCancelButton:true, confirmButtonText:"Sí"}).then(r => {
        if(r.isConfirmed) fetch(`/muro/${id}/eliminar/`, { method: "POST", headers: {"X-CSRFToken": getCookie("csrftoken")} })
            .then(res => res.json()).then(d => { if(d.success) { window.location.reload(); } });
    });
}

function editarPublicacion(id, actual) {
    Swal.fire({title:"Editar", input:"textarea", inputValue: actual, showCancelButton:true, confirmButtonText:"Guardar"}).then(r => {
        if(r.isConfirmed && r.value) fetch(`/muro/${id}/editar/`, {
            method: "POST", headers: {"Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": getCookie("csrftoken")},
            body: "contenido=" + encodeURIComponent(r.value)
        }).then(res => res.json()).then(d => d.success ? window.location.reload() : Swal.fire("Error", d.error, "error"));
    });
}

function compartirRutina(id, ia=false) {
    Swal.fire({title:"Compartir en muro?", showCancelButton:true, confirmButtonText:"Sí"}).then(r => {
        if(r.isConfirmed) fetch("/muro/compartir-rutina/", { method: "POST", headers: getJsonHeaders(), body: JSON.stringify({rutina_id:id, es_ia:ia}) })
            .then(res => res.json()).then(d => d.success ? Swal.fire("Listo", "Compartido", "success").then(()=>window.location.reload()) : Swal.fire("Error", d.error, "error"));
    });
}

async function verRutinaDesdePost(btn) {
    const card = btn.closest(".post-card") || btn.closest(".rutina-compartida-card");
    if (!card) return;

    // Buscamos el data-rutina
    // buscar el contenedor que tiene los datos
    const containerData = btn.closest("[data-rutina]"); 
    if (!containerData) return;

    const rutinaId = containerData.getAttribute("data-rutinaid");
    let ejerciciosData = [];
    
    try { 
        ejerciciosData = JSON.parse(containerData.getAttribute("data-rutina") || "[]"); 
    } catch (e) {
        console.error("Error parsing:", e);
    }

    // Construimos el HTML
    let htmlContent = '';

    if (ejerciciosData.length > 0) {
        // Header con conteo
        htmlContent += `
            <div class="rutina-modal-stats">
                <span>🏋️ Total ejercicios: <strong style="color:#fff">${ejerciciosData.length}</strong></span>
                <span>🔥 Intensidad: <strong style="color:#fff">Variable</strong></span>
            </div>
            <div class="rutina-modal-scroll">
        `;

        // Lista de ejercicios
        htmlContent += ejerciciosData.map((e, index) => `
            <div class="rutina-modal-item">
                <div class="rutina-index-badge">${index + 1}</div>
                <div class="rutina-details">
                    <h6>${e.ejercicio__nombre}</h6>
                    <p>${e.ejercicio__descripcion || "Sin descripción disponible."}</p>
                </div>
            </div>
        `).join("");

        htmlContent += `</div>`; // Cierre scroll
    } else {
        htmlContent = `<p class="text-muted text-center my-4">No hay detalles disponibles para esta rutina.</p>`;
    }

    // HTML del Footer (Botón Guardar)
    htmlContent += `
        <div class="text-center mt-2">
            <button id="btnGuardarRutinaModal" class="btn-modal-save">
                💾 Guardar Rutina
            </button>
            <div class="mt-2 small text-muted">
                <span id="contadorGuardadasModal" class="fw-bold" style="color:var(--ath-primary)">...</span> personas la tienen
            </div>
        </div>
    `;

    // Lanzar SweetAlert
    Swal.fire({
        title: `<span style="color:var(--ath-primary)">Detalles de la Rutina</span>`,
        html: htmlContent,
        background: "#021e26", // Fondo oscuro base
        color: "#e8fdf8",
        showConfirmButton: false,
        showCloseButton: true,
        width: 600, // Un poco más ancho para leer bien
        didOpen: async () => {
            const btnSave = document.getElementById("btnGuardarRutinaModal");
            const contador = document.getElementById("contadorGuardadasModal");

            try {
                // Obtener estado actual (si ya la tengo o no)
                const infoRes = await fetch(`/ia/calendario/info-guardado/?rutina_id=${rutinaId}`);
                const infoData = await infoRes.json();

                if (contador) contador.textContent = infoData.total_guardadas;

                if (infoData.ya_guardada) {
                    btnSave.textContent = "✅ Ya la tienes";
                    btnSave.disabled = true;
                } else {
                    // Evento Click Guardar
                    btnSave.onclick = async () => {
                        const originalText = btnSave.textContent;
                        btnSave.textContent = "Guardando...";
                        btnSave.disabled = true;

                        const res = await fetch("/ia/calendario/guardar-rutina/", {
                            method: "POST",
                            headers: getJsonHeaders(),
                            body: JSON.stringify({ rutina_id: rutinaId })
                        });
                        const data = await res.json();

                        if (data.success) {
                            btnSave.textContent = "✅ Guardada";
                            if (contador) contador.textContent = data.total_guardadas;
                            Swal.fire({
                                icon: 'success',
                                title: '¡Guardada!',
                                text: 'La rutina se añadió a tus guardadas.',
                                toast: true,
                                position: 'top-end',
                                timer: 3000,
                                showConfirmButton: false,
                                background: "#0e1726",
                                color: "#fff"
                            });
                        } else {
                            btnSave.textContent = originalText;
                            btnSave.disabled = false;
                            Swal.fire("Error", data.error, "error");
                        }
                    };
                }
            } catch (err) {
                console.error(err);
                if (btnSave) {
                    btnSave.textContent = "⚠️ Error de conexión";
                    btnSave.disabled = true;
                }
            }
        }
    });
}