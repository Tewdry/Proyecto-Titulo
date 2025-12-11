document.addEventListener("DOMContentLoaded", () => {

    /* ================================
       1. VALIDACIÓN DE FORMULARIO
    ================================= */
    
    const form = document.querySelector(".login-form");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    function createError(input) {
        let error = document.createElement("small");
        error.classList.add("error-text");
        error.style.color = "#ff4d4d";
        error.style.fontSize = "0.8rem";
        error.style.marginTop = "3px";
        error.innerText = "Este campo es obligatorio.";
        input.parentNode.appendChild(error);
        return error;
    }

    function removeError(input) {
        const error = input.parentNode.querySelector(".error-text");
        if (error) error.remove();
    }

    function marcarError(input) {
        input.classList.add("is-invalid");
        input.style.borderColor = "#ff4d4d";
        input.style.boxShadow = "0 0 5px rgba(255,0,0,0.4)";
        input.classList.add("shake");

        setTimeout(() => input.classList.remove("shake"), 400);
    }

    function limpiarErrorVisual(input) {
        input.classList.remove("is-invalid");
        input.style.borderColor = "";
        input.style.boxShadow = "";
    }

    form.addEventListener("submit", (e) => {
        let valido = true;

        limpiarErrorVisual(usernameInput);
        limpiarErrorVisual(passwordInput);
        removeError(usernameInput);
        removeError(passwordInput);

        if (usernameInput.value.trim() === "") {
            marcarError(usernameInput);
            createError(usernameInput);
            valido = false;
        }

        if (passwordInput.value.trim() === "") {
            marcarError(passwordInput);
            createError(passwordInput);
            valido = false;
        }

        if (!valido) {
            e.preventDefault();
        }
    });


    /* ================================
       2. SWEETALERT para mensajes Django
    ================================= */

    const djangoMessages = document.querySelectorAll("#django-messages .msg");

    djangoMessages.forEach(msg => {
        const type = msg.dataset.type; // success / error / warning
        const text = msg.dataset.text;

        let icon = "info";

        if (type.includes("success")) icon = "success";
        if (type.includes("error")) icon = "error";
        if (type.includes("warning")) icon = "warning";

        Swal.fire({
            title: icon === "success" ? "¡Perfecto!" : "Atención",
            text: text,
            icon: icon,
            confirmButtonColor: "#1e88e5",
            confirmButtonText: "Aceptar",
            background: "#f7f9fc",
            color: "#333",
        });
    });

});
