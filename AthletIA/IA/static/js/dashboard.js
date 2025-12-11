const UI = {
    por: (id) => document.getElementById(id),
    txt: (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; },
    html: (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val; }
};

const ATH = {
    fetchJSON: async (url) => {
        try {
            const r = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
            return r.ok ? await r.json() : null;
        } catch { return null; }
    }
};

/* --- INICIALIZACIÓN --- */
document.addEventListener("DOMContentLoaded", () => {
    saludarUsuario(); // Sorpresa 1: Saludo temporal
    iniciarGraficoPeso();
    cargarKPIs();
    cargarGraficos14();
});

/* --- SALUDO TEMPORAL --- */
function saludarUsuario() {
    const hora = new Date().getHours();
    const el = UI.por("saludoUsuario");
    let saludo = "Bienvenido";
    
    if (hora < 12) saludo = "Buenos días, ánimo!";
    else if (hora < 19) saludo = "Buenas tardes, dale con todo hoy!";
    else saludo = "Buenas noches, a descansar!";
    
    if(el) el.textContent = saludo;
}

/* --- GRÁFICO PESO (LIMPIO & MONOSPACED) --- */
let chartPeso = null;

function iniciarGraficoPeso() {
    const tagData = UI.por("historial-data");
    if (!tagData) return;
    
    let historial = [];
    try { historial = JSON.parse(tagData.textContent.trim()); } catch(e) { return; }

    const ctx = UI.por("graficoPeso").getContext('2d');
    
    // Gradiente
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(37, 226, 215, 0.4)'); 
    gradient.addColorStop(1, 'rgba(37, 226, 215, 0.0)');

    if (chartPeso) chartPeso.destroy();

    chartPeso = new Chart(ctx, {
        type: "line",
        data: {
            labels: historial.map(i => new Date(i.fecha).toLocaleDateString("es-CL", { day: '2-digit', month: '2-digit' })),
            datasets: [{
                label: "Peso",
                data: historial.map(i => i.peso_kg),
                borderColor: "#25e2d7",
                backgroundColor: gradient,
                borderWidth: 2,
                pointBackgroundColor: "#020c12",
                pointBorderColor: "#25e2d7",
                pointRadius: 4,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: "#8caeb0", font: { family: "'JetBrains Mono'" } } },
                y: { grid: { color: "rgba(255,255,255,0.05)" }, border: { display: false }, ticks: { color: "#8caeb0", font: { family: "'JetBrains Mono'" } } }
            }
        }
    });
}

/* --- DATA CENTER (KPIs) --- */
async function cargarKPIs() {
    const k = await ATH.fetchJSON("/api/IA/dashboard/kpi/");
    if (!k) return;

    // Actualizar Textos
    animarNumero("kpiRutinasSemanaValor", k.rutinas_semana);
    UI.txt("kpiRutinasSemanaObjetivo", `/ ${k.objetivo_semana}`);
    UI.txt("kpiCumplimientoValor", `${k.cumplimiento}%`);
    UI.txt("kpiCumplimientoTexto", k.cumplimiento_texto);
    
    // Pluralización inteligente
    UI.txt("kpiRachaValor", `${k.racha} día${k.racha !== 1 ? 's' : ''}`);
    UI.txt("kpiMinutosValor", k.minutos_7dias);

    // Color condicional
    const elCump = UI.por("kpiCumplimientoValor");
    elCump.style.color = k.cumplimiento >= 80 ? "#00E0A1" : (k.cumplimiento < 30 ? "#FF9F1C" : "#25e2d7");

    actualizarEnergia(k);
    calcularNivel(k); // Sistema de Niveles
    renderAgenda(k.proximas_rutinas);
    renderLogros(k.logros);
}

/* --- CÁLCULO DE NIVEL (XP) --- */
function calcularNivel(k) {
    const xp = (k.racha * 20) + k.minutos_7dias;
    let nivel = "Iniciado";
    let icon = "🛡️";
    let progresoNivel = Math.min(100, (xp / 500) * 100); // 500 XP para siguiente nivel

    if (xp > 1000) { nivel = "CYBORG 🤖"; icon = "🤖"; }
    else if (xp > 500) { nivel = "Élite 🔥"; icon = "🔥"; }
    else if (xp > 200) { nivel = "Constante ⚔️"; icon = "⚔️"; }

    UI.txt("textoNivel", `Nvl. ${nivel}`);
    UI.html("badgeNivel", `<span class="level-icon">${icon}</span> <span class="level-text">${nivel}</span>`);
    
    // Barra de XP en la tarjeta de proyección
    const xpBar = UI.por("xpBarra");
    if(xpBar) xpBar.style.width = `${progresoNivel}%`;
    
    // Actualizar texto de proyección
    if (xp > 0) UI.txt("proyeccionTexto", `XP Actual: ${xp}. Estás al ${Math.round(progresoNivel)}% de tu siguiente evolución.`);
}

/* --- AGENDA --- */
function renderAgenda(rutinas) {
    const cont = UI.por("timelineRutinas");
    if (!cont) return;
    cont.innerHTML = "";

    if (!rutinas.length) {
        cont.innerHTML = `<p class="text-muted" style="font-style:italic">Sin misiones pendientes.</p>`;
        return;
    }

    rutinas.forEach((r, index) => {
        const esHoy = index === 0;
        cont.innerHTML += `
            <div class="timeline-item ${esHoy ? 'next' : ''}">
                <div>
                    <span class="timeline-date">${r.fecha}</span>
                    <span class="timeline-name" style="color:white;">${r.nombre}</span>
                </div>
                ${r.hora ? `<span class="font-mono text-muted" style="font-size:0.8rem">${r.hora}</span>` : '<span style="font-size:0.8rem">⏳</span>'}
            </div>`;
    });
}

function renderLogros(logros) {
    const l = UI.por("listaLogros");
    if(!l) return;
    l.innerHTML = logros.length ? logros.map(x => `<div class="logro-tag">🏆 ${x}</div>`).join('') : '<span class="text-muted">Aún no hay trofeos esta semana.</span>';
}

function actualizarEnergia(k) {
    const valor = Math.min(100, k.cumplimiento + (k.racha*5));
    const barra = UI.por("energiaBarra");
    if(barra) barra.style.width = `${valor}%`;
    UI.txt("energiaValorTexto", `${valor}%`);
    
    const frases = [
        "Sistemas inactivos. Requiere imput.", 
        "Carga estable. Listo para iniciar.", 
        "Niveles óptimos. Rendimiento pico detectado."
    ];
    UI.txt("energiaTexto", valor < 30 ? frases[0] : (valor < 70 ? frases[1] : frases[2]));
}

/* --- ANIMACIÓN NÚMEROS --- */
function animarNumero(id, fin) {
    const obj = UI.por(id);
    if (!obj) return;
    let start = 0;
    const duration = 1000;
    let startTime = null;
    
    const step = (ts) => {
        if (!startTime) startTime = ts;
        const progress = Math.min((ts - startTime) / duration, 1);
        obj.innerHTML = Math.floor(progress * (fin - start) + start);
        if (progress < 1) requestAnimationFrame(step); else obj.innerHTML = fin;
    };
    requestAnimationFrame(step);
}

/* --- GRÁFICO BARRAS --- */
async function cargarGraficos14() {
    const d = await ATH.fetchJSON("/api/IA/dashboard/datos-graficos/");
    if (!d) return;
    const ctx = UI.por("graficoRutinas14").getContext('2d');
    
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, '#00E0A1'); 
    gradient.addColorStop(1, '#009e70'); 

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: d.rutinas_14d.fechas,
            datasets: [{ data: d.rutinas_14d.valores, backgroundColor: gradient, borderRadius: 3, barPercentage: 0.5 }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: "#8caeb0", font: { size: 10, family: "'JetBrains Mono'" } } },
                y: { display: false }
            }
        }
    });
}