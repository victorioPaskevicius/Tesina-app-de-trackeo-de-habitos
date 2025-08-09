document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("inputMail").value.trim();
    const password = document.getElementById("inputPass").value;
    const errorContainer = document.getElementById("errorContainer");

    let isValid = true;
    let messages = [];

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

    if (!isValid) {
      alert(messages.join("\n"));
      const textError = document.createElement("p");
      textError.textContent = `${messages.join("\n")}`;
      textError.classList.add("error");
      errorContainer.appendChild(textError);
    } else {
      fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.message) {
            window.location.href = `user/${data.user_id}`;
          } else {
            alert("Error: " + data.error);
          }
        })
        .catch((err) => console.error(err));
    }
  });
});
