from db.db_connection import get_connection

class UserProgress:
    def __init__(self, id_user_progres, user_id, lang_id, level_id, xp, completed_tasks):
        self.id_user_progres = id_user_progres
        self.user_id = user_id
        self.lang_id = lang_id
        self.level_id = level_id
        self.xp = xp
        self.completed_tasks = completed_tasks

    #отримуємо або створюємо прогрес
    @staticmethod
    def get_or_create(user_id, lang_id, level_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user_progress WHERE user_id = %s AND lang_id = %s AND level_id = %s",
            (user_id, lang_id, level_id)
        )
        row = cursor.fetchone()
        if row:
            conn.close()
            return UserProgress(**row)
        #якщо нема, створюємо
        cursor.execute(
            "INSERT INTO user_progress (user_id, lang_id, level_id, xp, completed_tasks) VALUES (%s, %s, %s, 0, 0)",
            (user_id, lang_id, level_id)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return UserProgress(new_id, user_id, lang_id, level_id, 0, 0)

    #додаємо бали
    def add_xp(self, amount):
        self.xp += amount
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_progress SET xp = %s WHERE id_user_progres = %s",
            (self.xp, self.id_user_progres)
        )
        conn.commit()
        conn.close()

    #завершуємо завдання
    def complete_task(self):
        self.completed_tasks += 1
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_progress SET completed_tasks = %s WHERE id_user_progres = %s",
            (self.completed_tasks, self.id_user_progres)
        )
        conn.commit()
        conn.close()

    #перевірка завершення рівня
    def is_level_completed(self):
        return self.completed_tasks >= 10

    def __str__(self):
        return f"XP: {self.xp}, Completed: {self.completed_tasks}"