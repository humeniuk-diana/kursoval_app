from db.db_connection import get_connection
from models.answer import Answer

class Task:
    def __init__(self, id_task, lang_id, level_id, task_type, question):
        self.id_task = id_task
        self.lang_id = lang_id
        self.level_id = level_id
        self.task_type = task_type
        self.question = question
        self.answers = []
#завантажує відповідь з бд
    def load_answers(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM answers WHERE task_id = %s",
            (self.id_task,)
        )
        rows = cursor.fetchall()
        conn.close()
        #список відповідей
        self.answers = [
            Answer(
                row["id_answer"],
                row["task_id"],
                row["answer_text"],
                row["is_correct"]
            )
            for row in rows
        ]
#перевірка відповіді користувача, допустимо ввод текста, ввод номер відповіді
    def check_answer(self, user_input):
        user_input = user_input.strip()
        #номер варіанта
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(self.answers):
                return self.answers[index].is_correct
        #текстова відповідь
        for answer in self.answers:
            if answer.is_match(user_input) and answer.is_correct:
                return True
        return False

    def __str__(self):
        return f"Task: {self.question}"
