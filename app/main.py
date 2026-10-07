"""
Главный файл FastAPI-приложения.
"""

from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import get_db
from app.schemas import (
    UserRegister, UserLogin, TokenResponse,
    MaterialCreate, MaterialOut,
)
from app.auth import (
    hash_password, verify_password,
    create_access_token, decode_access_token,
)
from app.llm_service import generate_quiz


app = FastAPI(
    title="GITS — Generator of Interactive Training Simulators",
    description="Веб-сервис генерации обучающих тренажёров на базе LLM",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---------- Health ----------

@app.get("/health")
def health():
    return {"status": "ok", "service": "gits"}


# ---------- HTML ----------

@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/register")
def register_page():
    return FileResponse(FRONTEND_DIR / "register.html")


@app.get("/login")
def login_page():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


# ---------- Auth ----------

@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: UserRegister, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Email уже занят")

    password_hash = hash_password(data.password)
    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (data.email, password_hash),
    )
    db.commit()
    user_id = cursor.lastrowid

    token = create_access_token({"sub": str(user_id), "email": data.email})
    return TokenResponse(access_token=token)


@app.post("/api/auth/login", response_model=TokenResponse)
def login(data: UserLogin, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, email, password_hash FROM users WHERE email = ?",
        (data.email,),
    )
    user = cursor.fetchone()

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return TokenResponse(access_token=token)


# ---------- Вспомогательная функция ----------

def _get_user_id(authorization: str, db):
    """Извлекает user_id из JWT в заголовке Authorization."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    return int(payload["sub"])


# ---------- Materials ----------

@app.post("/api/materials", response_model=MaterialOut)
def create_material(
    data: MaterialCreate,
    authorization: str = Header(None),
    db=Depends(get_db),
):
    user_id = _get_user_id(authorization, db)

    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO quizzes (user_id, title, source_text, quiz_type, difficulty)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, data.title, data.text, "pending", "pending"),
    )
    db.commit()
    material_id = cursor.lastrowid

    cursor.execute(
        """SELECT id, title, LENGTH(source_text) as text_length, created_at
           FROM quizzes WHERE id = ?""",
        (material_id,),
    )
    row = cursor.fetchone()

    return MaterialOut(
        id=row["id"],
        title=row["title"],
        text_length=row["text_length"],
        created_at=str(row["created_at"]),
    )


@app.get("/api/materials")
def list_materials(authorization: str = Header(None), db=Depends(get_db)):
    user_id = _get_user_id(authorization, db)

    cursor = db.cursor()
    cursor.execute(
        """SELECT id, title, LENGTH(source_text) as text_length, created_at
           FROM quizzes WHERE user_id = ? ORDER BY created_at DESC""",
        (user_id,),
    )
    rows = cursor.fetchall()

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "text_length": r["text_length"],
            "created_at": str(r["created_at"]),
        }
        for r in rows
    ]


# ---------- AI Generation ----------

@app.post("/api/generate")
def generate(
    data: MaterialCreate,
    authorization: str = Header(None),
    db=Depends(get_db),
):
    """
    Принимает текст лекции → возвращает массив вопросов, сгенерированных LLM.
    """
    user_id = _get_user_id(authorization, db)

    try:
        quiz = generate_quiz(
            text=data.text,
            num_questions=5,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации: {str(e)}",
        )

    return {
        "title": quiz.title,
        "questions": [q.model_dump() for q in quiz.questions],
    }