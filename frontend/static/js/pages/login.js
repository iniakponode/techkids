document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  if (!loginForm) return;

  const usernameField = document.getElementById("username");
  const passwordField = document.getElementById("password");
  const nextField = document.getElementById("next");
  const messageDiv = document.getElementById("loginMessage");

  const params = new URLSearchParams(window.location.search);
  if (nextField && !nextField.value) {
    const nextParam = params.get("next");
    if (nextParam) {
      nextField.value = nextParam;
    }
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (messageDiv) {
      messageDiv.innerHTML = "";
    }

    const payload = {
      username: usernameField.value.trim(),
      password: passwordField.value,
    };

    if (nextField && nextField.value) {
      payload.next = nextField.value;
    }

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        if (messageDiv) {
          messageDiv.innerHTML = `<div class="alert alert-success" role="status">${data.detail || "Login successful"}</div>`;
        }

        const redirectTarget = data.redirect_url || "/";
        setTimeout(() => {
          window.location.assign(redirectTarget);
        }, 400);
      } else {
        const errorMessage = data.detail || "Login failed. Please try again.";
        if (messageDiv) {
          messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">${errorMessage}</div>`;
        }
      }
    } catch (error) {
      console.error("Login error:", error);
      if (messageDiv) {
        messageDiv.innerHTML = `<div class="alert alert-danger" role="alert">An unexpected error occurred. Please try again.</div>`;
      }
    }
  });
});