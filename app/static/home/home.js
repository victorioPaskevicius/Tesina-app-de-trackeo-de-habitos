const formHabit = document.getElementById("formHabit");
const btnMarkAsComplete = document.querySelectorAll(".btn-toggle-complete");
const btnDeleteHabit = document.querySelectorAll(".btn-delete");
const btnEditHabit = document.querySelectorAll(".form-edit-habit");

formHabit.addEventListener("submit", (e) => {
  e.preventDefault();

  const name = document.getElementById("title").value;
  const description = document.getElementById("description").value;

  const path = window.location.pathname;
  const parts = path.split("/");
  const user_id = parts[parts.length - 1];

  fetch(`/user/${user_id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      description,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.message) {
        alert(data.message);
        location.reload();
      } else {
        alert("Error: " + data.error);
      }
    })
    .catch((err) => console.log(err));
});

btnMarkAsComplete.forEach((button) => {
  button.addEventListener("click", () => {
    const habitId = button.dataset.habitId;
    const path = window.location.pathname;
    const parts = path.split("/");
    const user_id = parts[parts.length - 1];
    fetch(`/user/${user_id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        habitId,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.message) {
          // alert(data.message);
          location.reload();
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch((err) => console.log(err));
  });
});

btnDeleteHabit.forEach((button) => {
  button.addEventListener("click", () => {
    const habitId = button.dataset.habitId;
    const path = window.location.pathname;
    const parts = path.split("/");
    const user_id = parts[parts.length - 1];

    fetch(`/user/${user_id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        habitId,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.message) {
          // alert(data.message);
          location.reload();
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch((err) => console.log(err));
  });
});

btnEditHabit.forEach((form) => {
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const path = window.location.pathname;
    const parts = path.split("/");
    const user_id = parts[parts.length - 1];

    const habitId = form.dataset.habitId;
    const name = form.querySelector("[name='title']").value.trim();
    const description = form.querySelector("[name='description']").value.trim();

    fetch(`/user/${user_id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ habitId, name, description }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.message) {
          alert("✅ " + data.message);
          location.reload();
        } else {
          alert("❌ Error: " + data.error);
        }
      })
      .catch((err) => console.error(err));
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split("T")[0];
  const habitCards = document.querySelectorAll(".habit-card");

  habitCards.forEach((card) => {
    const logDate = card.dataset.logDate; // debes tener data-log-date="{{ habit.latest_log.log_date }}"
    const status = card.dataset.status; // y data-status="{{ habit.latest_log.status }}"

    // Si el log_date no es hoy o status = 0 => mostrar como pendiente
    if (logDate !== today || status === "0") {
      card.classList.remove("completed");
      card.classList.add("pending");

      const btn = card.querySelector(".btn-toggle-complete");
      if (btn) {
        btn.textContent = "Marcar como completado";
        btn.classList.remove("btn-success");
        btn.classList.add("btn-outline-secondary");
      }
    }
  });
});
