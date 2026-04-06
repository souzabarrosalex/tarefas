from database import get_connection

# ================= USUÁRIOS =================
def create_user(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    conn.close()
    return data


# ================= TAREFAS =================
def create_task(task):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO tasks (title, description, created_at, due_date, priority, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, task)

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return task_id


def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    data = cursor.fetchall()
    conn.close()
    return data


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    cursor.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM task_users WHERE task_id = ?", (task_id,))

    conn.commit()
    conn.close()


# ================= SUBTAREFAS =================
def add_subtask(task_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO subtasks (task_id, name, status)
    VALUES (?, ?, 'Pendente')
    """, (task_id, name))
    conn.commit()
    conn.close()


def get_subtasks(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks WHERE task_id = ?", (task_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def update_subtask_status(subtask_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE subtasks SET status = ?
    WHERE id = ?
    """, (status, subtask_id))
    conn.commit()
    conn.close()

def update_task_status(task_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE tasks
    SET status = ?
    WHERE id = ?
    """, (status, task_id))

    conn.commit()
    conn.close()  

# ================= TEMPLATES =================

def create_template(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO task_templates (name) VALUES (?)", (name,))
    template_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return template_id


def add_template_subtask(template_id, name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO template_subtasks (template_id, name)
    VALUES (?, ?)
    """, (template_id, name))

    conn.commit()
    conn.close()


def get_templates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM task_templates")
    data = cursor.fetchall()

    conn.close()
    return data


def get_template_subtasks(template_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM template_subtasks
    WHERE template_id = ?
    """, (template_id,))

    data = cursor.fetchall()
    conn.close()

    return data    
  
def create_subtasks_from_template(task_id, template_id):
    from database import get_connection

    # pega subtarefas do template
    subtasks = get_template_subtasks(template_id)

    conn = get_connection()
    cursor = conn.cursor()

    for sub in subtasks:
        cursor.execute("""
        INSERT INTO subtasks (task_id, name, status)
        VALUES (?, ?, 'Pendente')
        """, (task_id, sub[2]))

    conn.commit()
    conn.close()