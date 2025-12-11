document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 JS Registro: Validaciones completas activadas");

    const passInput = document.querySelector("input[name='password1']");
    const strengthBox = document.getElementById("password-strength");

    function evaluarFuerza(password) {
        let fuerza = 0;
        if (password.length >= 8) fuerza++;
        if (/[A-Z]/.test(password)) fuerza++;
        if (/[a-z]/.test(password)) fuerza++;
        if (/[0-9]/.test(password)) fuerza++;
        if (/[^A-Za-z0-9]/.test(password)) fuerza++;
        return fuerza;
    }

    if (passInput && strengthBox) {
        passInput.addEventListener("input", () => {
            const pass = passInput.value;
            const nivel = evaluarFuerza(pass);

            if (!pass) {
                strengthBox.innerHTML = "";
                return;
            }

            if (nivel <= 2) {
                strengthBox.innerHTML = "🔴 Contraseña débil";
                strengthBox.style.color = "#ff4757";
            } else if (nivel <= 4) {
                strengthBox.innerHTML = "🟠 Contraseña media";
                strengthBox.style.color = "#ffa502";
            } else {
                strengthBox.innerHTML = "🟢 Contraseña fuerte";
                strengthBox.style.color = "#2ed573";
            }
        });
    }

    const steps = document.querySelectorAll(".form-step");
    const nextBtns = document.querySelectorAll(".next-step");
    const prevBtns = document.querySelectorAll(".prev-step");
    const indicators = document.querySelectorAll(".step");
    const form = document.getElementById("registroForm");

    let currentStep = 0;

    function pareceURL(texto) {
        return /^(https?:\/\/|ftp:\/\/|www\.|file:)/i.test(texto) || /\.(com|org|net|io|gov|edu)/i.test(texto);
    }

    function contienePayloadPeligroso(texto) {
        return /(<script|#exec|cmd|union|select|drop|onerror|onload|-->|<!--)/i.test(texto);
    }

    function usernameSeguro(username) {
        return /^[a-zA-Z0-9_-]{3,20}$/.test(username);
    }

    function emailValido(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function validarEdad(fechaStr) {
        if (!fechaStr) return false;
        const hoy = new Date();
        const fn = new Date(fechaStr);
        fn.setMinutes(fn.getMinutes() + fn.getTimezoneOffset());
        let edad = hoy.getFullYear() - fn.getFullYear();
        if (hoy.getMonth() < fn.getMonth() || 
           (hoy.getMonth() === fn.getMonth() && hoy.getDate() < fn.getDate())) edad--;
        return edad >= 14;
    }

    function limpiarErrores(step) {
        step.querySelectorAll(".error-msg-dynamic").forEach(e => e.remove());
        step.querySelectorAll("input").forEach(i => {
            i.style.borderColor = "";
            i.style.boxShadow = "";
        });
    }

    function marcarError(input, mensaje) {
        input.style.borderColor = "#ff4757";
        input.style.boxShadow = "0 0 8px rgba(255,71,87,.3)";
        if (!input.parentNode.querySelector(".error-msg-dynamic")) {
            const msg = document.createElement("div");
            msg.className = "error-msg-dynamic";
            msg.style.color = "#ff6b81";
            msg.style.fontSize = "0.8rem";
            msg.innerText = mensaje;
            input.parentNode.appendChild(msg);
        }
    }

    function validarPaso() {
        const step = steps[currentStep];
        const inputs = step.querySelectorAll("input, select");
        limpiarErrores(step);

        let valido = true;

        inputs.forEach(input => {
            const v = input.value.trim();

            if (input.required && !v) {
                marcarError(input, "Campo obligatorio");
                valido = false;
            }

            if (input.name === "username") {
                if (pareceURL(v) || contienePayloadPeligroso(v) || !usernameSeguro(v)) {
                    marcarError(input, "Usuario inválido");
                    valido = false;
                }
            }

            if (input.name === "email") {
                if (!emailValido(v) || /(c:|file:|\\|\/etc\/|windows|system32)/i.test(v)) {
                    marcarError(input, "Correo peligroso");
                    valido = false;
                }
            }

            if (input.name === "password1") {
                if (v.length < 8 || !/[A-Z]/.test(v) || !/[0-9]/.test(v)) {
                    marcarError(input, "Debe tener mayúscula y número");
                    valido = false;
                }
            }

            if (input.name === "password2") {
                if (v !== document.querySelector("input[name='password1']").value) {
                    marcarError(input, "No coinciden");
                    valido = false;
                }
            }

            if (input.name === "fecha_nacimiento" && !validarEdad(v)) {
                marcarError(input, "Edad mínima 14");
                valido = false;
            }
        });

        return valido;
    }

    function showStep(n) {
        steps.forEach((s,i)=> s.style.display = i===n ? "block" : "none");
        indicators.forEach((i,idx)=> i.classList.toggle("active", idx===n));
    }

    showStep(currentStep);

    nextBtns.forEach(btn => btn.onclick = ()=> validarPaso() && showStep(++currentStep));
    prevBtns.forEach(btn => btn.onclick = ()=> showStep(--currentStep));

    if (form) {
        form.onsubmit = (e) => {
            e.preventDefault();
            if(validarPaso()) form.submit();
        };

        form.querySelectorAll("input").forEach(input => {
            input.addEventListener("paste", e => {
                const texto = (e.clipboardData || window.clipboardData).getData("text");
                if(contienePayloadPeligroso(texto)) {
                    e.preventDefault();
                    marcarError(input,"Pegado bloqueado");
                }
            });
        });
    }
});
