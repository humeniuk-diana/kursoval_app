import os
import sys
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.level import Level

try:
    from models.user_progress import UserProgress
except Exception:
    class UserProgress:
        _memory = {}

        def __init__(self, id_user_progres, user_id, lang_id, level_id, xp, completed_tasks):
            self.id_user_progres = id_user_progres
            self.user_id = user_id
            self.lang_id = lang_id
            self.level_id = level_id
            self.xp = xp
            self.completed_tasks = completed_tasks

        @staticmethod
        def get_or_create(user_id, lang_id, level_id):
            key = (user_id, lang_id, level_id)
            if key not in UserProgress._memory:
                UserProgress._memory[key] = UserProgress(len(UserProgress._memory) + 1, user_id, lang_id, level_id, 0, 0)
            return UserProgress._memory[key]

        def add_xp(self, amount):
            self.xp += amount

        def complete_task(self):
            self.completed_tasks += 1

        def is_level_completed(self):
            return self.completed_tasks >= 10

from gui.constants import PALETTE, FONT
from gui.utils import get_model_id
from gui.pages_auth import StartPage, LoginPage, RegisterPage
from gui.pages_learning import LanguagePage, LevelPage, DashboardPage, AccountPage
from gui.pages_task import TaskPage


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TailCode")
        self.geometry("980x720")
        self.minsize(980, 720)
        self.configure(bg=PALETTE["bg_top"])

        try:
            icon = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "assets", "icon.png"))
            self.iconphoto(True, icon)
        except Exception:
            pass

        self.current_user = None
        self.selected_lang = None
        self.selected_level = None
        self.current_progress = None
        self.selected_task = None
        self.selected_task_index = 0
        self.progress_records = {}
        self.completed_language_ids = set()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        self.container = tk.Frame(self, bg=PALETTE["bg_top"], highlightthickness=0)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for page in (StartPage, LoginPage, RegisterPage, LanguagePage, LevelPage, DashboardPage, AccountPage, TaskPage):
            frame = page(self.container, self)
            self.frames[page] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(StartPage)

    def _configure_styles(self):
        self.style.configure("CardTitle.TLabel", background=PALETTE["card"], foreground=PALETTE["text"], font=(FONT, 24, "bold"))
        self.style.configure("CardText.TLabel", background=PALETTE["card"], foreground=PALETTE["muted"], font=(FONT, 11))
        self.style.configure("FieldLabel.TLabel", background=PALETTE["card"], foreground=PALETTE["muted"], font=(FONT, 10, "bold"))

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def logout(self):
        self.current_user = None
        self.selected_lang = None
        self.selected_level = None
        self.current_progress = None
        self.selected_task = None
        self.selected_task_index = 0
        self.show_frame(LoginPage)

    def get_all_levels(self):
        return Level.get_all_levels()

    def get_next_level(self):
        if not self.selected_level:
            return None
        levels = self.get_all_levels()
        current_id = get_model_id(self.selected_level, ["id_level", "level_id", "id"])
        for index, level in enumerate(levels):
            if get_model_id(level, ["id_level", "level_id", "id"]) == current_id:
                if index + 1 < len(levels):
                    return levels[index + 1]
                return None
        return None

    def is_last_level(self):
        return self.get_next_level() is None

    def mark_language_completed(self, lang=None):
        target = lang or self.selected_lang
        lang_id = get_model_id(target, ["id_lang", "lang_id", "id"])
        if lang_id is not None:
            self.completed_language_ids.add(lang_id)

    def is_language_completed(self, lang):
        lang_id = get_model_id(lang, ["id_lang", "lang_id", "id"])
        return lang_id in self.completed_language_ids

    def get_cached_progress_values(self):
        return list(self.progress_records.values())

    def sync_progress(self):
        if not self.current_user or not self.selected_lang or not self.selected_level:
            self.current_progress = None
            return None
        user_id = get_model_id(self.current_user, ["id_user", "user_id", "id"])
        lang_id = get_model_id(self.selected_lang, ["id_lang", "lang_id", "id"])
        level_id = get_model_id(self.selected_level, ["id_level", "level_id", "id"])
        if user_id is None or lang_id is None or level_id is None:
            self.current_progress = None
            return None
        self.current_progress = UserProgress.get_or_create(user_id, lang_id, level_id)
        self.progress_records[(user_id, lang_id, level_id)] = self.current_progress
        return self.current_progress

if __name__ == "__main__":
    app = App()
    app.mainloop()