from datetime import datetime
from db.db_connection import get_connection

class Attempt:
    def __init__(self, id_attempt, user_id, task_id, user_answer, is_correct, date_attempt=None):
        self.id_attempt = id_attempt
        self.user_id = user_id
        self.task_id = task_id
        self.user_answer = user_answer
        self.is_correct = bool(is_correct)
        self.date_attempt = date_attempt

#зберігаємо спробу
    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attempts (user_id, task_id, user_answer, is_correct, date_attempt) VALUES (%s, %s, %s, %s, NOW())",
            (self.user_id, self.task_id, self.user_answer, int(self.is_correct))
        )
        self.id_attempt = cursor.lastrowid
        conn.commit()
        conn.close()

#отримуємо всі спроби користувача
    @staticmethod
    def get_user_attempts(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM attempts WHERE user_id = %s",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [Attempt(**row) for row in rows]

    def __str__(self):
        status = "Correct" if self.is_correct else "Wrong"
        return f"Attempt: {self.user_answer} ({status})"