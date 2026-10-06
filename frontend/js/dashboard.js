// Логика панели преподавателя

const API_BASE = "";
const token = localStorage.getItem("token");

// Если нет токена — редирект на вход
if (!token) {
    window.location.href = "/login";
}

// ---------- Выход ----------

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "/";
});

// ---------- Счётчик символов ----------

const textArea = document.getElementById("text");
const charCount = document.getElementById("char-count");

if (textArea) {
    textArea.addEventListener("input", () => {
        charCount.textContent = textArea.value.length;
    });
}

// ---------- Загрузка материалов ----------

async function loadMaterials() {
    const container = document.getElementById("materials-container");

    try {
        const response = await fetch(`${API_BASE}/api/materials`, {
            headers: { "Authorization": `Bearer ${token}` },
        });

        if (response.status === 401) {
            localStorage.removeItem("token");
            window.location.href = "/login";
            return;
        }

        const materials = await response.json();

        if (materials.length === 0) {
            container.innerHTML = '<p class="empty-state">Пока нет материалов. Загрузите первую лекцию.</p>';
            return;
        }

        container.innerHTML = materials.map(m => `
            <div class="material-item">
                <div>
                    <h3>${escapeHtml(m.title)}</h3>
                    <small>${m.text_length} символов · ${m.created_at}</small>
                </div>
            </div>
        `).join("");
    } catch (err) {
        container.innerHTML = '<p class="error-message">Не удалось загрузить материалы.</p>';
    }
}

// ---------- Создание материала ----------

const materialForm = document.getElementById("material-form");
if (materialForm) {
    materialForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const title = document.getElementById("title").value.trim();
        const text = document.getElementById("text").value;
        const errorEl = document.getElementById("material-error");
        const successEl = document.getElementById("material-success");

        errorEl.textContent = "";
        successEl.textContent = "";

        try {
            const response = await fetch(`${API_BASE}/api/materials`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify({ title, text }),
            });

            const data = await response.json();

            if (!response.ok) {
                errorEl.textContent = data.detail || "Ошибка сохранения";
                return;
            }

            successEl.textContent = "Материал сохранён!";
            materialForm.reset();
            charCount.textContent = "0";
            loadMaterials();
        } catch (err) {
            errorEl.textContent = "Сервер недоступен.";
        }
    });
}

// ---------- Защита от XSS ----------

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// ---------- Запуск ----------

loadMaterials();