"""
AI-модуль: интеграция с Ollama для генерации тестов.
"""

import json
import re
from typing import Optional

import ollama
from pydantic import BaseModel, Field, ValidationError


# ---------- Pydantic-схемы для валидации ----------

class Question(BaseModel):
    """Один вопрос теста."""
    type: str = Field(..., pattern="^(single_choice|fill_in_the_blank)$")
    question: Optional[str] = None
    options: Optional[list[str]] = None
    correct_index: Optional[int] = None
    sentence: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: str


class Quiz(BaseModel):
    """Набор вопросов."""
    title: str
    questions: list[Question] = Field(..., min_length=1)


# ---------- System prompt ----------

SYSTEM_PROMPT = """Ты — эксперт по созданию образовательных тестов.

Твоя задача — на основе текста лекции создать интерактивный тест.

ВАЖНЫЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО валидным JSON. Без markdown-разметки, без ```json, без пояснений.
2. Формат ответа строго такой:
{
  "title": "Название теста",
  "questions": [
    {
      "type": "single_choice",
      "question": "Текст вопроса?",
      "options": ["Вариант 1", "Вариант 2", "Вариант 3", "Вариант 4"],
      "correct_index": 0,
      "explanation": "Почему этот ответ правильный."
    }
  ]
}
3. Типы вопросов: только "single_choice" (один правильный ответ).
4. У вопросов single_choice ВСЕГДА 4 варианта, только один правильный.
5. Язык вопросов = язык текста лекции.
"""


def build_user_prompt(text: str, num_questions: int) -> str:
    """Строит пользовательский промпт."""
    return f"""Создай тест из {num_questions} вопросов по следующему тексту.

Текст лекции:
\"\"\"
{text}
\"\"\"

Верни только JSON по указанной схеме."""


def extract_json(raw: str) -> str:
    """Извлекает JSON из ответа LLM."""
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if match:
        return match.group(1)
    start = raw.find('{')
    end = raw.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("JSON не найден в ответе LLM")
    return raw[start:end + 1]


def generate_quiz(
    text: str,
    num_questions: int = 5,
    max_retries: int = 3,
) -> Quiz:
    """
    Генерирует тест из текста лекции с retry-логикой.
    """
    user_prompt = build_user_prompt(text, num_questions)
    last_error = None

    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model="llama3.1:8b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.7, "num_ctx": 4096},
            )

            raw = response["message"]["content"]
            json_str = extract_json(raw)
            data = json.loads(json_str)
            quiz = Quiz(**data)
            return quiz

        except (ValueError, json.JSONDecodeError, ValidationError) as e:
            last_error = e
            user_prompt = (
                f"Твой предыдущий ответ был невалидным: {e}. "
                f"Верни ТОЛЬКО валидный JSON без пояснений."
            )
            continue

    raise RuntimeError(f"Не удалось сгенерировать тест за {max_retries} попыток: {last_error}")