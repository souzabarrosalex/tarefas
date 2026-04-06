import streamlit as st
import pandas as pd

from database import create_tables
from models import *
from services import calculate_progress
from utils import now
from models import (
    create_user,
    get_users,
    create_task,
    get_tasks,
    delete_task,
    add_subtask,
    get_subtasks,
    update_subtask_status,
    create_template,
    add_template_subtask,
    get_templates,
    create_subtasks_from_template  # 👈 ESSA LINHA FALTAVA
)

# Inicializa banco
create_tables()

st.set_page_config(page_title="Task Manager", layout="wide")

# ================= SIDEBAR =================
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Criar Tarefa",
    "Listar Tarefas",
    "Usuários",
    "Templates"
])

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    tasks = get_tasks()

    total = len(tasks)
    concluídas = len([t for t in tasks if t[6] == "Concluída"])
    pendentes = len([t for t in tasks if t[6] != "Concluída"])

    percentual = int((concluídas / total) * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total)
    col2.metric("Concluídas", concluídas)
    col3.metric("Pendentes", pendentes)
    col4.metric("Conclusão (%)", percentual)

    st.progress(percentual / 100 if total > 0 else 0)


# ================= USUÁRIOS =================
elif menu == "Usuários":
    st.title("👤 Usuários")

    nome = st.text_input("Nome do usuário")

    if st.button("Cadastrar"):
        create_user(nome)
        st.success("Usuário criado!")

    users = get_users()
    st.write(pd.DataFrame(users, columns=["ID", "Nome"]))

# ================= TEMPLATE =================
elif menu == "Templates":
    st.title("📋 Templates de Tarefas")

    # ================= CRIAR TEMPLATE =================
    nome_template = st.text_input("Nome do Template")

    if st.button("Criar Template"):
        template_id = create_template(nome_template)
        st.session_state["template_id"] = template_id
        st.success("Template criado!")

    # ================= ADICIONAR SUBTAREFAS =================
    if "template_id" in st.session_state:
        st.subheader("Adicionar Subtarefas ao Template")

        sub = st.text_input("Nome da subtarefa")

        if st.button("Adicionar subtarefa"):
            add_template_subtask(st.session_state["template_id"], sub)
            st.success("Subtarefa adicionada!")    


# ================= CRIAR TAREFA =================
elif menu == "Criar Tarefa":
    st.title("➕ Nova Tarefa")

    title = st.text_input("Nome da tarefa")
    description = st.text_area("Descrição")

    due_date = st.date_input("Data de vencimento", value=None)

    priority = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
    status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluída"])

    users = get_users()
    user_names = [u[1] for u in users]

    created_by = st.selectbox("Criado por", user_names if user_names else ["Nenhum"])

    responsaveis = st.multiselect("Responsáveis", user_names)

    templates = get_templates()
    template_dict = {t[1]: t[0] for t in templates}

    template_nome = st.selectbox(
        "Usar Template (opcional)",
        ["Nenhum"] + list(template_dict.keys())
    )

    if st.button("Salvar"):
        task = (
            title,
            description,
            now(),
            str(due_date),
            priority,
            status,
            None
        )

        task_id = create_task(task)

        # ✅ Se escolheu template → cria subtarefas automáticas
        if template_nome != "Nenhum":
            template_id = template_dict[template_nome]
            create_subtasks_from_template(task_id, template_id)

        st.success("Tarefa criada com sucesso!")


# ================= LISTAR =================
elif menu == "Listar Tarefas":
    st.title("📋 Tarefas")

    # 🔹 1. BUSCAR DADOS
    tasks = get_tasks()

    # 🔹 2. CRIAR FILTROS (ANTES DE USAR)
    st.subheader("🔎 Filtros")

    col1, col2 = st.columns(2)

    prioridade_filtro = col1.selectbox(
        "Prioridade",
        ["Todas", "Baixa", "Média", "Alta"]
    )

    busca = col2.text_input("Buscar tarefa")
    # 🔹 3. APLICAR FILTROS
    tasks_filtradas = []

    for t in tasks:
        # 🚫 IGNORA CONCLUÍDAS
        if t[6] == "Concluída":
            continue

        # prioridade
        if prioridade_filtro != "Todas" and t[5] != prioridade_filtro:
            continue

        # busca
        if busca and busca.lower() not in t[1].lower():
            continue

        tasks_filtradas.append(t)
        
    # 🔹 4. MOSTRAR RESULTADOS
    for i, t in enumerate(tasks_filtradas):
        st.subheader(t[1])
        with st.container():
            st.subheader(f"{t[1]} ({t[5]})")

                # 🎨 Status com cor
            if t[6] == "Concluída":
                st.success("Concluída")
            elif t[6] == "Em andamento":
                st.warning("Em andamento")
            else:
                st.error("Pendente")

            st.write(t[2])
            novo_status = st.selectbox(
                "Status",
                ["Pendente", "Em andamento", "Concluída"],
                index=["Pendente", "Em andamento", "Concluída"].index(t[6]),
                key=f"status_{i}_{t[0]}"
            )

            if novo_status != t[6]:
                update_task_status(t[0], novo_status)
                st.rerun()

            subtasks = get_subtasks(t[0])

            progress = calculate_progress(subtasks)

            # ✅ Auto concluir tarefa
            if progress == 100 and t[6] != "Concluída":
                update_task_status(t[0], "Concluída")

            st.progress(progress / 100)
            st.write(f"{progress}% concluído")

            # Subtarefas
            st.write("Subtarefas:")

            for s in subtasks:
                checked = s[3] == "Concluída"

                if st.checkbox(s[2], value=checked, key=f"{s[0]}"):
                    update_subtask_status(s[0], "Concluída")
                else:
                    update_subtask_status(s[0], "Pendente")

            new_sub = st.text_input(f"Nova subtarefa {t[0]}")

            if st.button("Adicionar", key=f"btn_{t[0]}"):
                add_subtask(t[0], new_sub)

            if st.button("Excluir Tarefa", key=f"del_{t[0]}"):
                delete_task(t[0])
                st.warning("Tarefa excluída")