# GITS — Generator of Interactive Training Simulators

Веб-сервис генерации интерактивных обучающих тренажёров на базе LLM.

**Проектный практикум, 2 курс**  
Кафедра «Математическая кибернетика и информационные технологии»  
Руководитель: Галкин Владимир Владимирович

## Команда
- **Покровский Максим** - Backend
- **Бариев Вагиф** —  Frontend
- **Емелин Григорий** — AI/QA

## Стек

- **Backend:** Python 3.12, FastAPI, SQLite
- **Frontend:** HTML5, CSS3, Vanilla JS
- **Auth:** bcrypt + JWT

## старт
https://gits-vm2h.onrender.com
### 1. Клонировать репозиторий

```bash
git clone https://github.com/Secluded-1/gits.git
cd gits

## 🤖 AI-часть (Отчёт 2)

### Стек
- **Ollama 0.40.0** — локальный сервер LLM
- **Модель `llama3.1:8b`** (q3_k_m, 3.74 ГБ)
- **Python-библиотека `ollama==0.6.3`**

### Эндпоинт `POST /api/generate`

Принимает текст лекции, возвращает массив сгенерированных вопросов.

**Пример запроса:**
```json
{
  "title": "Тест по FastAPI",
  "text": "FastAPI — современный веб-фреймворк для Python..."
}

**Пример ответа**
{
  "title": "Тест по FastAPI",
  "questions": [
    {
      "type": "single_choice",
      "question": "На каком стандарте основан FastAPI?",
      "options": ["ASGI", "WSGI", "Pydantic", "RESTful"],
      "correct_index": 0,
      "explanation": "FastAPI основан на стандарте ASGI."
    }
  ]
}