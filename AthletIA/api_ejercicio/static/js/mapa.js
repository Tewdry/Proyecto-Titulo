// Descripciones de músculos
const MUSCLE_INFO = {
  "Pectoral": "Músculo clave para empujes y fuerza del torso.",
  "Espalda": "Fundamental para tracción y postura.",
  "Hombros": "Rotación y elevación del brazo.",
  "Bíceps": "Flexión del codo.",
  "Tríceps": "Extensión del brazo.",
  "Abdomen": "Estabilidad del core y control del torso.",
  "Piernas": "Potencia, estabilidad y movilidad.",
  "Glúteos": "Fuerza en cadera y postura.",
  "Antebrazos": "Agarre y control de muñeca.",
  "Deltoides": "Movimiento del hombro en varias direcciones.",
  "Lumbares": "Soporte lumbar y protección de la columna.",
  "Oblicuos": "Rotación del torso y estabilidad lateral.",
  "Trapecio": "Estabilidad de cuello y zona superior de la espalda.",
  "Gemelos": "Impulso al caminar, correr y saltar.",
  "Adductores": "Estabilidad interna de la cadera.",
  "Cuello": "Postura cervical y movilidad del cuello.",
  "Core": "Centro de fuerza del cuerpo.",
  "Cuádriceps": "Extensión de rodilla y potencia en piernas.",
  "Dorsales": "Músculo principal de tracción del tren superior, clave para fuerza y amplitud en la espalda.",
  "Femorales": "Músculos posteriores del muslo responsables de la flexión de rodilla y extensión de cadera.",
};


const MAPA_MUSCULOS = {
  1: "Pectoral",
  2: "Espalda",
  3: "Hombros",
  4: "Bíceps",
  5: "Tríceps",
  6: "Abdomen",
  7: "Piernas",
  8: "Glúteos",
  9: "Cuerpo completo",
  10: "Cardiovascular",
  11: "Antebrazos",
  12: "Deltoides",
  13: "Lumbares",
  14: "Oblicuos",
  15: "Trapecio",
  16: "Gemelos",
  17: "Adductores",
  18: "Cuello",
  19: "Core",
  20: "Pantorrillas",
  21: "Cuádriceps",
  22: "Dorsales",
  23: "Femorales"
};

// Mapeo clases m-#
const MAPA_CLASES = {};
Object.keys(MAPA_MUSCULOS).forEach(id => {
  MAPA_CLASES[`m-${id}`] = MAPA_MUSCULOS[id];
});

// Obtiene nombre de músculo lo mejor posible
function obtenerMusculo(el) {
  const idAttr = el.getAttribute("data-muscle-id");
  if (idAttr && MAPA_MUSCULOS[idAttr]) return MAPA_MUSCULOS[idAttr];

  for (let clase of el.classList) {
    if (MAPA_CLASES[clase]) return MAPA_CLASES[clase];
  }

  const nameAttr = el.getAttribute("data-muscle-name");
  if (nameAttr) return nameAttr;

  // Fallback suaves si no tenemos nada más
  if (el.id) return el.id;
  if (el.classList.length) return el.classList[0];

  return "Zona muscular";
}

function obtenerMusculo(el) {
  const idAttr = el.getAttribute("data-muscle-id");
  if (idAttr && MAPA_MUSCULOS[idAttr]) return MAPA_MUSCULOS[idAttr];

  // Detectar por clase m-#
  for (let clase of el.classList) {
    if (MAPA_CLASES[clase]) return MAPA_CLASES[clase];
  }

  // Detectar nombre crudo del SVG
  let raw = el.getAttribute("data-muscle-name") || el.id || [...el.classList][0] || null;
  if (!raw) return "Zona muscular";

  // Limpieza automática de nombres: elimina left, right, l, r
  raw = raw
    .replace(/[-_]?left/gi, "")
    .replace(/[-_]?right/gi, "")
    .replace(/[-_]?l\b/gi, "")
    .replace(/[-_]?r\b/gi, "")
    .replace(/[-_]+/g, " ")          // reemplaza guiones por espacios
    .trim();

  // Primera letra mayúscula
  raw = raw.charAt(0).toUpperCase() + raw.slice(1);

  return raw;
}


document.addEventListener("DOMContentLoaded", () => {
  const zonas = document.querySelectorAll("#mapa-container svg path, #mapa-container svg polygon");
  if (!zonas.length) return;

  // Tooltip único
  const tooltip = document.createElement("div");
  tooltip.className = "muscle-tooltip";
  document.body.appendChild(tooltip);

  zonas.forEach(zona => {
    const musculo = obtenerMusculo(zona);

    zona.addEventListener("mouseenter", () => {
      const desc = MUSCLE_INFO[musculo] || "Zona muscular del cuerpo humano.";

      tooltip.innerHTML = `
        <strong>${musculo}</strong><br>
        <span>${desc}</span>
      `;
      tooltip.style.display = "block";
    });

    zona.addEventListener("mousemove", (e) => {
      tooltip.style.left = (e.pageX + 12) + "px";
      tooltip.style.top = (e.pageY + 12) + "px";
    });

    zona.addEventListener("mouseleave", () => {
      tooltip.style.display = "none";
    });

    zona.addEventListener("click", (e) => {
      // CLICK deshabilitado por ahora (solo informativo)
    });
  });
});
