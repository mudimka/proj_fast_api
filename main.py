from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="Простой FastAPI сервис")

# Модель для валидации входящих данных (вместо schemas.py)
class TaskItem(BaseModel):
    title: str
    description: Optional[str] = None

# Функция для подключения к локальной БД
def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row  # Чтобы получать данные как словари
    return conn

# Создаем таблицу при старте (если ее нет)
@app.on_event("startup")
def startup():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

# 1. GET - Получить все задачи
@app.get("/tasks")
def get_tasks():
    conn = get_db()
    cursor = conn.execute("SELECT * FROM tasks")
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

# 2. POST - Создать задачу
@app.post("/tasks", status_code=201)
def create_task(task: TaskItem):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (task.title, task.description)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": task.title, "description": task.description}

# 3. PUT - Обновить задачу
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskItem):
    conn = get_db()
    cursor = conn.execute(
        "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
        (task.title, task.description, task_id)
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"id": task_id, "title": task.title, "description": task.description}

# 4. DELETE - Удалить задачу
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"message": "Задача удалена"}