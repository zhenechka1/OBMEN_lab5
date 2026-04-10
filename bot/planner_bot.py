import telebot

from models.user import User
from services.database import Database
from services.reminder_service import ReminderService
from services.task_manager import TaskManager


class PlannerBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.database = Database()
        self.task_manager = TaskManager(self.database)
        self.reminder_service = ReminderService(self.database)

        self.register_handlers()

    def register_user(self, message) -> User:
// Назва `register_user` трохи збиває з пантелику, бо метод також повертає вже існуючих юзерів. Краще було б щось типу`get_or_create_user`.
        telegram_user = message.from_user
        user = self.database.get_user(telegram_user.id)

        if user is None:
            user = User(
                user_id=telegram_user.id,
                username=telegram_user.username,
                chat_id=message.chat.id,
            )
            self.database.save_user(user)

        return user

    def register_handlers(self) -> None:
        @self.bot.message_handler(commands=["start"])
// Тут забули дописати тип повернення. Додай -> None: для повноти типізації, будь ласка.
        def start_handler(message):
            user = self.register_user(message)
            // Цей рядок дублюється абсолютно в кожному хендлері (порушуємо DRY). Треба зробити простенький декоратор, у який вже буде приходити готовий об'єкт user.
            text = (
                f"Вітаю, {user.username}!\n"
                "Я PlannerBot — бот для повсякденних задач.\n\n"
                "Введіть /help, щоб побачити список команд."
            )
            self.bot.send_message(message.chat.id, text)

        @self.bot.message_handler(commands=["help"])
        def help_handler(message):
            self.register_user(message)
            text = (
                "Доступні команди:\n"
                "/start - запуск бота\n"
                "/help - список команд\n"
                "/add назва задачі\n"
                "/add назва задачі ; дедлайн\n"
                "/list - показати всі задачі\n"
                "/done id - позначити задачу як виконану\n"
                "/delete id - видалити задачу\n"
                "/remind - показати задачі з дедлайнами"
            )
            self.bot.send_message(message.chat.id, text)

        @self.bot.message_handler(commands=["add"])
//Трохи завеликий хендлер. Давай винесемо парсинг тексту (спліт по `;`) в окрему акуратну функцію (напр. parse_task(text)). Так буде набагато легше писати тести потім :)
        def add_handler(message):
            user = self.register_user(message)

            text = message.text.replace("/add", "", 1).strip()
            if not text:
                self.bot.send_message(
                    message.chat.id,
                    "Помилка: введіть назву задачі.\n"
                    "Приклад:\n"
                    "/add Купити молоко\n"
                    "/add Зробити звіт ; 2026-04-15",
                )
                return
// Тут юзер цілком може ввести "післязавтра" замість дати, і бот це проковтне. Додай, будь ласка, валідацію через datetime.strptime.

            if ";" in text:
                title, deadline = text.split(";", 1)
                title = title.strip()
                deadline = deadline.strip()
            else:
                title = text
                deadline = None

            if not title:
                self.bot.send_message(
                    message.chat.id, "Помилка: назва задачі не може бути порожньою."
                )
                return

            task = self.task_manager.add_task(user.user_id, title, deadline)
            self.bot.send_message(
                message.chat.id, f"Задачу додано:\n\n{task.get_info()}"
            )

        @self.bot.message_handler(commands=["list"])
        def list_handler(message):
            user = self.register_user(message)
            tasks = self.task_manager.get_all_tasks(user.user_id)

            if not tasks:
                self.bot.send_message(message.chat.id, "Список задач порожній.")
                return

            result = ["Ваші задачі:"]
            for task in tasks:
                result.append(task.get_info())

            self.bot.send_message(message.chat.id, "\n\n".join(result))

        @self.bot.message_handler(commands=["done"])
        def done_handler(message):
            user = self.register_user(message)

            text = message.text.replace("/done", "", 1).strip()
            if not text.isdigit():
                self.bot.send_message(
                    message.chat.id,
                    "Помилка: введіть коректний ID задачі.\nПриклад: /done 1",
                )
                return

            task_id = int(text)
            success = self.task_manager.mark_task_done(user.user_id, task_id)

            if success:
                self.bot.send_message(
                    message.chat.id, f"Задачу {task_id} позначено як виконану."
                )
            else:
                self.bot.send_message(
                    message.chat.id, "Помилка: задачу з таким ID не знайдено."
                )

        @self.bot.message_handler(commands=["delete"])
        def delete_handler(message):
            user = self.register_user(message)

            text = message.text.replace("/delete", "", 1).strip()
            if not text.isdigit():
                self.bot.send_message(
                    message.chat.id,
                    "Помилка: введіть коректний ID задачі.\nПриклад: /delete 1",
                )
                return

            task_id = int(text)
            success = self.task_manager.delete_task(user.user_id, task_id)

            if success:
                self.bot.send_message(message.chat.id, f"Задачу {task_id} видалено.")
            else:
                self.bot.send_message(
  //  Команда називається `/remind`, але фактично бот сам ні про що не нагадує, а просто фільтрує таски. Може перейменуємо на `/deadlines`? 
                    message.chat.id, "Помилка: задачу з таким ID не знайдено."
                )

        @self.bot.message_handler(commands=["remind"])
        def remind_handler(message):
            user = self.register_user(message)
            result = self.reminder_service.show_reminders(user.user_id)
            self.bot.send_message(message.chat.id, result)

        @self.bot.message_handler(func=lambda message: True)
        def unknown_handler(message):
            self.register_user(message)
            self.bot.send_message(
                message.chat.id,
                "Невідома команда. Введіть /help для перегляду списку команд.",
            )
// Здається, в нас ніде не відловлюються винятки (try/except). Якщо у хендлері щось впаде (наприклад помилка парсингу), бот може просто крашнутись. Варто додати глобальний обробник помилок.
    def run(self) -> None:
        print("PlannerBot is running...")
        self.bot.infinity_polling()
