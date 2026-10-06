// Логика регистрации и входа

const API_BASE = "";

// ---------- Регистрация ----------

const registerForm = document.getElementById("register-form");
if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const errorEl = document.getElementById("error-message");

        errorEl.textContent = "";

        try {
            const response = await fetch(`${API_BASE}/api/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                errorEl.textContent = data.detail || "Ошибка регистрации";
                return;
            }

            localStorage.setItem("token", data.access_token);
            window.location.href = "/dashboard";
        } catch (err) {
            errorEl.textContent = "Сервер недоступен. Попробуйте позже.";
        }
    });
}

// ---------- Вход ----------

const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const errorEl = document.getElementById("error-message");

        errorEl.textContent = "";

        try {
            const response = await fetch(`${API_BASE}/api/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                errorEl.textContent = data.detail || "Неверный email или пароль";
                return;
            }

            localStorage.setItem("token", data.access_token);
            window.location.href = "/dashboard";
        } catch (err) {
            errorEl.textContent = "Сервер недоступен. Попробуйте позже.";
        }
    });
}