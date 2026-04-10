from models.task import Task


class TaskManager:
// Додай сюди докстрінги (docstrings), хоча б швиденько розпиши за що відповідає клас. Буде набагато простіше читати.
    def __init__(self, database):
        self.database = database

    def add_task(self, user_id: int, title: str, deadline: str | None = None) -> Task:
        task_id = self.database.get_next_task_id(user_id)
        task = Task(task_id, title, deadline)
        self.database.save_task(user_id, task)
        return task

    def get_all_tasks(self, user_id: int) -> list:
        return self.database.get_tasks(user_id)

    def mark_task_done(self, user_id: int, task_id: int) -> bool:
        task = self.database.get_task_by_id(user_id, task_id)
        if task is None:
            return False
        task.mark_done()
        return True

    def delete_task(self, user_id: int, task_id: int) -> bool:
        return self.database.delete_task(user_id, task_id)
