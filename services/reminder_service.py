class ReminderService:
    def __init__(self, database):
        self.database = database

    def get_tasks_with_deadlines(self, user_id: int) -> list:
        tasks = self.database.get_tasks(user_id)
        return [task for task in tasks if task.deadline and not task.completed]

    def show_reminders(self, user_id: int) -> str:
        tasks = self.get_tasks_with_deadlines(user_id)

        if not tasks:
            return "Немає активних задач з дедлайнами."

        result = ["Нагадування про задачі:"]
        for task in tasks:
            result.append(task.get_info())

        return "\n\n".join(result)
