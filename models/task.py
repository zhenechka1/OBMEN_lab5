class Task:
    def __init__(self, task_id: int, title: str, deadline: str | None = None):
        self.task_id = task_id
        self.title = title
        self.deadline = deadline
        self.completed = False

    def mark_done(self) -> None:
        self.completed = True

    def get_info(self) -> str:
        status = "Виконано" if self.completed else "Активна"
        deadline_text = self.deadline if self.deadline else "не встановлено"
        return (
            f"[{self.task_id}] {self.title}\n"
            f"Дедлайн: {deadline_text}\n"
            f"Статус: {status}"
        )
