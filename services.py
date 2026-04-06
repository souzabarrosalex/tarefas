def calculate_progress(subtasks):
    if not subtasks:
        return 0

    total = len(subtasks)
    done = sum(1 for s in subtasks if s[3] == "Concluída")

    return int((done / total) * 100)