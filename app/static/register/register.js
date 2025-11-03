document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const username = document.getElementById("inputName").value.trim();
    const email = document.getElementById("inputMail").value.trim();
    const password = document.getElementById("inputPass").value;
    const rePassword = document.getElementById("inputRePass").value;
    const errorContainer = document.getElementById("errorContainer");

    let isValid = true;
    let messages = [];

    // Validar nombre
    if (username.length < 3 || username.length > 20) {
      isValid = false;
      messages.push("El nombre debe tener entre 3 y 20 caracteres");
    }

    // Validar email con expresión regular
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      isValid = false;
      messages.push("El correo electrónico no es válido.");
    }

    // Validar contraseña
    if (password.length < 6) {
      isValid = false;
      messages.push("La contraseña debe tener al menos 6 caracteres.");
    }

    // Confirmar contraseña
    if (password !== rePassword) {
      isValid = false;
      messages.push("Las contraseñas no coinciden.");
    }

    if (!isValid) {
      errorContainer.innerHTML = "";
      messages.forEach((message) => {
        const textError = document.createElement("p");
        textError.textContent = message;
        textError.classList.add("error","fs-5")
        errorContainer.appendChild(textError)
      });
    } else {
      fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.message) {
            alert(data.message);
            window.location.href = `user/${data.user_id}`;

          } else {
            alert("Error: " + data.error);
          }
        })
        .catch((err) => console.error(err));
    }
  });
});