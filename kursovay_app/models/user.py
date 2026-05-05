from db.db_connection import get_connection
from datetime import datetime
from models.attempt import Attempt
from models.user_progress import UserProgress
import re

class User:
    def __init__(self, id_user, name_user, email, password, date_reg=None):
        self.id_user = id_user
        self.name_user = name_user
        self.email = email
        self.password = password
        self.date_reg = date_reg
#валідаця
    def validate(self):
        if not self.name_user or len(self.name_user) < 2:
            raise ValueError("The name must be at least 2 characters long.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Incorrect email.")
        if len(self.password) < 4:
            raise ValueError("The password must be at least 4 characters long.")

    # перевірка чи існує така пошта
    def email_exists(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (self.email,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None

    #регістрація
    def register(self):
        self.validate()
        if self.email_exists():
            raise ValueError("A user with this email already exists.")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name_user, email, password, date_reg) VALUES (%s, %s, %s, NOW())",
            (self.name_user, self.email, self.password)
        )
        self.id_user = cursor.lastrowid
        #отримуємо дату з бд
        cursor.execute(
            "SELECT date_reg FROM users WHERE id_user = %s",
            (self.id_user,)
        )
        self.date_reg = cursor.fetchone()[0]
        conn.commit()
        conn.close()

    #авторизація
    @staticmethod
    def login(email, password):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, password)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(
                row["id_user"],
                row["name_user"],
                row["email"],
                row["password"],
                row["date_reg"]
            )
        else:
            return None
#користувач намагається виконати завданння
    def attempt_task(self, task, user_input):
        # перевірка відповіді
        result = task.check_answer(user_input)
        #зберігаємо спробу
        attempt = Attempt(
            None,
            self.id_user,
            task.id_task,
            user_input,
            result
        )
        attempt.save()
        #отримуємо або створюємо прогрес
        progress = UserProgress.get_or_create(
            self.id_user,
            task.lang_id,
            task.level_id
        )
        #оновлюємо прогрес
        if result:
            progress.add_xp(10)
            progress.complete_task()
        return result

    def get_progress(self, lang_id, level_id):
        return UserProgress.get_or_create(self.id_user, lang_id, level_id)

    def __str__(self):
        return f"User: {self.name_user}"