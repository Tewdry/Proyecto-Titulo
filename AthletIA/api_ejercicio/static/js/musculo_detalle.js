// AthletIA - Músculo Detalle (Rutina Manual)
document.addEventListener("DOMContentLoaded", () => {

  const STORAGE_KEY = "athletia_rutina_manual_v1";

  const cards = Array.from(document.querySelectorAll(".ejercicio-card"));
  const carritoBtn = document.getElementById("carrito-ejercicios");
  const carritoCounter = document.getElementById("carrito-counter");

  const inputTexto = document.getElementById("filtro-texto");
  const selectTipo = document.getElementById("filtro-tipo");

  let carritoEjercicios = [];

  // ---------- Storage ----------
  function cargarDesdeStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const data = JSON.parse(raw);
      if (Array.isArray(data)) carritoEjercicios = data;
    } catch (err) {
      console.error("Error leyendo storage:", err);
    }
  }

  function guardarEnStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(carritoEjercicios));
    } catch (err) {
      console.error("Error guardando storage:", err);
    }
  }

  function getCardData(card) {
    return {
      id: card.dataset.id,
      nombre: card.dataset.nombre || "",
      descripcion: card.dataset.descripcion || "",
      tipo: card.dataset.tipo || "",
      nivel: card.dataset.nivel || ""
    };
  }

  // ---------- UI selección ----------
  function refrescarUISeleccion() {
    const idsSel = new Set(carritoEjercicios.map(e => String(e.id)));

    cards.forEach(card => {
      const id = String(card.dataset.id);
      const btn = card.querySelector(".btn-agregar");
      if (!btn) return;

      if (idsSel.has(id)) {
        card.classList.add("seleccionado");
        btn.textContent = "✔ Añadido";
      } else {
        card.classList.remove("seleccionado");
        btn.textContent = "➕ Agregar a rutina";
      }
    });

    carritoCounter.textContent = carritoEjercicios.length;
  }

  // ---------- Filtros ----------
  function aplicarFiltros() {
    const texto = (inputTexto?.value || "").toLowerCase();
    const tipo = (selectTipo?.value || "").toLowerCase();

    cards.forEach(card => {
      const nombre = (card.dataset.nombre || "").toLowerCase();
      const desc = (card.dataset.descripcion || "").toLowerCase();
      const tipoCard = (card.dataset.tipo || "").toLowerCase();

      let visible = true;

      if (texto && !(nombre + " " + desc).includes(texto)) visible = false;
      if (tipo && tipoCard !== tipo) visible = false;

      if (visible) {
          card.classList.remove("hide");
          card.parentElement.classList.remove("hide");
      } else {
          card.classList.add("hide");
          card.parentElement.classList.add("hide");
      }
    });
  }

  inputTexto?.addEventListener("input", aplicarFiltros);
  selectTipo?.addEventListener("change", aplicarFiltros);

  // ---------- Toggle ejercicio ----------
  function toggleEjercicio(card) {
    const data = getCardData(card);
    const id = String(data.id);

    const index = carritoEjercicios.findIndex(e => String(e.id) === id);

    if (index >= 0) {
      carritoEjercicios.splice(index, 1);
    } else {
      carritoEjercicios.push(data);
    }

    guardarEnStorage();
    refrescarUISeleccion();
  }

  cards.forEach(card => {
    const btn = card.querySelector(".btn-agregar");
    if (!btn) return;
    btn.addEventListener("click", () => toggleEjercicio(card));
  });

  // ---------- Eliminar desde modal ----------
  window.eliminarDelCarrito = function(id) {
    carritoEjercicios = carritoEjercicios.filter(e => String(e.id) !== String(id));
    guardarEnStorage();
    refrescarUISeleccion();
    abrirModalCrearRutina();
  };

  // ---------- Modal crear rutina ----------
  carritoBtn?.addEventListener("click", abrirModalCrearRutina);

  function abrirModalCrearRutina() {
    if (!carritoEjercicios.length) {
      Swal.fire({
        icon: "warning",
        title: "Sin ejercicios",
        text: "Selecciona ejercicios antes de crear tu rutina.",
        background: "#031820",
        color: "#e8fdf8"
      });
      return;
    }

    const lista = carritoEjercicios.map(e => `
      <li style="margin-bottom:5px;">
        <b>${e.nombre}</b>
        ${e.nivel ? ` <span style="color:#00ffbf;">[${e.nivel}]</span>` : ""}
        <button 
          onclick="eliminarDelCarrito('${e.id}')"
          style="float:right; color:#ff4b4b; background:none; border:none; cursor:pointer;">
          ✖
        </button>
      </li>
    `).join("");

    Swal.fire({
      title: "Crear rutina manual",
      html: `
        <div style="max-height:190px; overflow-y:auto; text-align:left; border:1px solid #123; padding:8px; border-radius:8px; margin-bottom:10px;">
          <strong>Ejercicios seleccionados (${carritoEjercicios.length}):</strong>
          <ul style="margin-top:6px; padding-left:18px; font-size:13px;">
            ${lista}
          </ul>
        </div>

        <input id="rutinaNombre" class="swal2-input" placeholder="Nombre de la rutina">
        <textarea id="rutinaDesc" class="swal2-textarea" placeholder="Descripción (opcional)"></textarea>
        <hr>
        <label class="swal2-label">¿Asignar al calendario ahora?</label>
        <input id="rutinaFecha" type="date" class="swal2-input" style="max-width: 220px;">
        <textarea id="rutinaNotas" class="swal2-textarea" placeholder="Notas para el calendario (opcional)"></textarea>
      `,
      showCancelButton: true,
      confirmButtonText: "Guardar rutina",
      cancelButtonText: "Cancelar",
      background: "#031820",
      color: "#e8fdf8",
      preConfirm: () => {
        const nombre = document.getElementById("rutinaNombre").value.trim();
        const descripcion = document.getElementById("rutinaDesc").value.trim();

        if (!nombre) {
          Swal.showValidationMessage("El nombre de la rutina es obligatorio.");
          return false;
        }
        if (!carritoEjercicios.length) {
          Swal.showValidationMessage("Debes seleccionar al menos un ejercicio.");
          return false;
        }

        return {
          nombre,
          descripcion,
          fecha: document.getElementById("rutinaFecha").value,
          notas: document.getElementById("rutinaNotas").value.trim()
        };
      }
    }).then(res => {
      if (!res.isConfirmed) return;

      const { nombre, descripcion, fecha, notas } = res.value;
      const ejerciciosIds = carritoEjercicios.map(e => e.id);
      guardarRutinaManual(nombre, descripcion, ejerciciosIds, fecha, notas);
    });
  }

  // ---------- Guardar rutina ----------
  function guardarRutinaManual(nombre, descripcion, ejerciciosIds, fecha, notas) {
    fetch(URL_GUARDAR_RUTINA_MANUAL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        nombre,
        descripcion,
        ejercicios: ejerciciosIds
      })
    })
    .then(r => r.json())
    .then(data => {
      if (!data.success) {
        Swal.fire("Error", data.error || "No se pudo guardar la rutina.", "error");
        return;
      }

      const rutinaId = data.rutina_id;

      if (!fecha) {
        Swal.fire("Rutina guardada", "Puedes verla en tus rutinas manuales.", "success");
        carritoEjercicios = [];
        guardarEnStorage();
        refrescarUISeleccion();
        return;
      }

      asignarRutinaAlCalendario(rutinaId, fecha, notas);
    });
  }

  // ---------- Calendar ----------
  function asignarRutinaAlCalendario(rutinaId, fecha, notas) {
    fetch(URL_CALENDARIO_MANUAL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        fecha,
        rutina_id: rutinaId,
        notas,
        hora: null
      })
    })
    .then(r => r.json())
    .then(data => {
      Swal.fire(
        data.success ? "Rutina asignada" : "Error",
        data.message || data.error || "",
        data.success ? "success" : "error"
      );

      if (data.success) {
        carritoEjercicios = [];
        guardarEnStorage();
        refrescarUISeleccion();
      }
    });
  }

  // ---------- Init ----------
  cargarDesdeStorage();
  refrescarUISeleccion();
  aplicarFiltros();
});
