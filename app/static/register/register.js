document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const username = document.getElementById("inputName").value.trim();
    const email = document.getElementById("inputMail").value.trim();
    const password = document.getElementById("inputPass").value;
    const rePassword = document.getElementById("inputRePass").value;
    const phone = document.getElementById("inputNumber").value.trim();
    const errorContainer = document.getElementById("errorContainer");

    let isValid = true;
    let messages = [];

    // Validar nombre
    if (username.length < 3) {
      isValid = false;
      messages.push("El nombre debe tener al menos 3 caracteres.");
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
      messages.push("Las contraseñas no coinciden.", "\n");
    }

    // Validar número de teléfono
    const phoneRegex = /^[0-9]{7,15}$/;
    if (!phoneRegex.test(phone)) {
      isValid = false;
      messages.push("El número de teléfono debe tener entre 7 y 15 dígitos.");
    }

    if (!isValid) {
      alert(messages.join("\n"));
      const textError = document.createElement("p");
      textError.textContent = `${messages.join('\n')}`;
      textError.classList.add('error')
      errorContainer.appendChild(textError);
    } else {
      alert("Registro exitoso.");
      form.submit();
      window.location.href = "user/${username}";
    }
  });
});
