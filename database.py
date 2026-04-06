import sqlite3

DB_NAME = "tasks.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # Tarefas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        created_at TEXT,
        due_date TEXT,
        priority TEXT,
        status TEXT,
        created_by INTEGER
    )
    """)

    # Relacionamento tarefa x usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_users (
        task_id INTEGER,
        user_id INTEGER
    )
    """)

    # Subtarefas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subtasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        name TEXT,
        status TEXT
    )
    """)

    # Templates de tarefas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

# Subtarefas do template
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS template_subtasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER,
        name TEXT
    )
    """)

    conn.commit()
    conn.close()