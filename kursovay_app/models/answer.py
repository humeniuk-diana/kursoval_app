class Answer:
    def __init__(self, id_answer, task_id, answer_text, is_correct):
        self.id_answer = id_answer
        self.task_id = task_id
        self.answer_text = answer_text
        self.is_correct = bool(is_correct)
#валідація ("  Hello   World  " - "hello world")
    def normalize(self, text):
        return " ".join(text.strip().lower().split())

#перевірка, чи співпадає відповідь користувача з цбою відповидю (" 4 " == "4" → True)
    def is_match(self, user_input):
        return self.normalize(self.answer_text) == self.normalize(user_input)

    def __str__(self):
        return f"{self.answer_text}"
