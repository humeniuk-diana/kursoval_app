from db.db_connection import get_connection
from models.task import Task

class Language:
    def __init__(self, id_lang, name_lang, info_lang):
        self.id_lang = id_lang
        self.name_lang = name_lang
        self.info_lang = info_lang
    @staticmethod
    def get_all_languages():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM languages")
        rows = cursor.fetchall()
        conn.close()
        return [Language(**row) for row in rows]
#отримує завдання по мові та рівню складності
    def get_tasks(self, level_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM tasks WHERE lang_id = %s AND level_id = %s",
            (self.id_lang, level_id)
        )
        rows = cursor.fetchall()
        conn.close()
        return [Task(**row) for row in rows]

    def __str__(self):
        return f"{self.name_lang}"