class Database:
    def __init__(self):
        // Оскільки тут ми зберігаємо дані просто у словниках, при перезапуску бота всі таски користувачів зникнуть (In-Memory). Треба прикрутити сюди SQLite або щось подібне для постійного збереження.
        self.users = {}
// Додай сюди type hints, будь ласка (напр., dict[int, User]). Так mypy і IDE зможуть підказувати структуру.
        self.tasks = {}
        self.next_task_ids = {}

    def save_user(self, user) -> None:
        self.users[user.user_id] = user

    def get_user(self, user_id: int):
        return self.users.get(user_id)

    def get_next_task_id(self, user_id: int) -> int:
        if user_id not in self.next_task_ids:
            self.next_task_ids[user_id] = 1
        task_id = self.next_task_ids[user_id]
        self.next_task_ids[user_id] += 1
        return task_id

    def save_task(self, user_id: int, task) -> None:
        if user_id not in self.tasks:
            self.tasks[user_id] = []
        self.tasks[user_id].append(task)

    def get_tasks(self, user_id: int) -> list:
        return self.tasks.get(user_id, [])

    def get_task_by_id(self, user_id: int, task_id: int):
        for task in self.get_tasks(user_id):
            if task.task_id == task_id:
                return task
        return None

    def delete_task(self, user_id: int, task_id: int) -> bool:
        user_tasks = self.get_tasks(user_id)
        for task in user_tasks:
            if task.task_id == task_id:
                user_tasks.remove(task)
                return True
        return False
