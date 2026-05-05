import tkinter as tk
from tkinter import ttk

from .constants import PALETTE, FONT
from .base_page import GradientPage, ChoicePage
from .widgets import GlassButton, ProgressBar
from .utils import get_model_id, get_model_name
#сторінки навчального процесу

#вибір мови програмування
class LanguagePage(ChoicePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="Choose language", subtitle="Pick what you want to study first. You can keep the flow playful and focused.")

    def on_show(self):
        from models.language import Language
        languages = Language.get_all_languages()
        self.render_choices(
            items=languages,
            label_getter=lambda lang: lang.name_lang,
            command_getter=lambda lang: lambda: self.select(lang),
            empty_text="No languages found yet.",
            kind_getter=lambda lang: "completed" if self.controller.is_language_completed(lang) else "task",
        )
        self.footer.config(
            text=f"Available now: {len(languages)} • completed courses: {len(self.controller.completed_language_ids)}"
        )

    def select(self, lang):
        self.controller.selected_lang = lang
        self.controller.show_frame(LevelPage)

#вибір рівня складності
class LevelPage(ChoicePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="Choose level", subtitle="Select your pace. Start easy or jump to a more confident stage.")

    def on_show(self):
        from models.level import Level
        levels = Level.get_all_levels()
        self.render_choices(
            items=levels,
            label_getter=lambda lvl: lvl.name_level,
            command_getter=lambda lvl: lambda: self.select(lvl),
            empty_text="No levels found yet.",
        )
        lang_name = getattr(self.controller.selected_lang, "name_lang", "language")
        self.footer.config(text=f"Chosen language: {lang_name}")

    def select(self, level):
        self.controller.selected_level = level
        self.controller.sync_progress()
        self.controller.show_frame(DashboardPage)

#головний екран навчання: прогрес, список завдань, навігація
class DashboardPage(GradientPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.card = self.make_card(width=820, height=720)
        self.body = tk.Frame(self.card, bg=PALETTE["card_glass"])
        self.body.pack(fill="both", expand=True, padx=34, pady=28)

        top = tk.Frame(self.body, bg=PALETTE["card_glass"])
        top.pack(fill="x")

        title_wrap = tk.Frame(top, bg=PALETTE["card_glass"])
        title_wrap.pack(side="left", fill="x", expand=True)
        self.create_badge(title_wrap, "learning map").pack(anchor="w", pady=(0, 12))
        ttk.Label(title_wrap, text="Your course", style="CardTitle.TLabel").pack(anchor="w")
        self.subtitle = tk.Label(title_wrap, text="", bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 11))
        self.subtitle.pack(anchor="w", pady=(8, 0))

        actions = tk.Frame(top, bg=PALETTE["card_glass"])
        actions.pack(side="right")
        GlassButton(actions, "Account", lambda: controller.show_frame(AccountPage), kind="secondary", height=46, width=160, font=(FONT, 10, "bold")).pack(pady=(0, 10))
        GlassButton(actions, "Change language", lambda: controller.show_frame(LanguagePage), kind="secondary", height=46, width=160, font=(FONT, 10, "bold")).pack(pady=(0, 10))
        GlassButton(actions, "Change level", lambda: controller.show_frame(LevelPage), kind="secondary", height=46, width=160, font=(FONT, 10, "bold")).pack(pady=(0, 10))
        GlassButton(actions, "Log out", controller.logout, kind="danger", height=46, width=160, font=(FONT, 10, "bold")).pack()

        stats = tk.Frame(self.body, bg=PALETTE["primary_soft"], highlightbackground=PALETTE["glass_border"], highlightthickness=1)
        stats.pack(fill="x", pady=(24, 22))
        stats_inner = tk.Frame(stats, bg=PALETTE["primary_soft"])
        stats_inner.pack(fill="x", padx=18, pady=16)
        self.progress_title = tk.Label(stats_inner, text="Progress", bg=PALETTE["primary_soft"], fg=PALETTE["text"], font=(FONT, 12, "bold"))
        self.progress_title.pack(anchor="w")
        self.progress_text = tk.Label(stats_inner, text="", bg=PALETTE["primary_soft"], fg=PALETTE["muted"], font=(FONT, 10))
        self.progress_text.pack(anchor="w", pady=(4, 10))
        self.progress_bar = ProgressBar(stats_inner)
        self.progress_bar.pack(fill="x")

        self.status = tk.Label(self.body, text="", bg=PALETTE["card_glass"], fg=PALETTE["danger"], font=(FONT, 10))
        self.status.pack(anchor="w", pady=(0, 10))

        self.level_action_wrap = tk.Frame(self.body, bg=PALETTE["card_glass"])
        self.level_action_wrap.pack(fill="x", pady=(0, 12))

        self.road_wrap = tk.Frame(self.body, bg=PALETTE["card_glass"])
        self.road_wrap.pack(fill="both", expand=True)
        self.road_canvas = tk.Canvas(self.road_wrap, bg=PALETTE["card_glass"], highlightthickness=0, bd=0)
        self.road_canvas.pack(side="left", fill="both", expand=True)
        self.road_scroll = tk.Scrollbar(self.road_wrap, orient="vertical", command=self.road_canvas.yview)
        self.road_scroll.pack(side="right", fill="y")
        self.road_canvas.configure(yscrollcommand=self.road_scroll.set)
        self.road = tk.Frame(self.road_canvas, bg=PALETTE["card_glass"])
        self.road_window = self.road_canvas.create_window((0, 0), anchor="nw", window=self.road)
        self.road.bind("<Configure>", lambda _e: self.road_canvas.configure(scrollregion=self.road_canvas.bbox("all")))
        self.road_canvas.bind("<Configure>", lambda event: self.road_canvas.itemconfigure(self.road_window, width=event.width))
        self.road_canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        if self.winfo_ismapped():
            self.road_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_show(self):
        self.render_dashboard()
#
    def render_dashboard(self):
        from .pages_task import TaskPage
        for child in self.road.winfo_children():
            child.destroy()
        for child in self.level_action_wrap.winfo_children():
            child.destroy()

        progress = self.controller.sync_progress()
        lang_name = getattr(self.controller.selected_lang, "name_lang", "Language")
        level_name = getattr(self.controller.selected_level, "name_level", "Level")
        self.subtitle.config(text=f"{lang_name} • {level_name}")

        if progress is None:
            self.progress_text.config(text="Progress is unavailable for the selected data.")
            self.progress_bar.set(0)
        else:
            total_for_level = 10
            ratio = progress.completed_tasks / max(total_for_level, 1)
            self.progress_text.config(text=f"XP: {progress.xp}   Completed tasks: {progress.completed_tasks}/{total_for_level}")
            self.progress_bar.set(ratio)
            if progress.is_level_completed():
                next_level = self.controller.get_next_level()
                if next_level is not None:
                    GlassButton(
                        self.level_action_wrap,
                        "Go to next level",
                        lambda lvl=next_level: self.open_next_level(lvl),
                        kind="primary",
                        height=50,
                        width=220,
                    ).pack(anchor="w")
                else:
                    tk.Label(
                        self.level_action_wrap,
                        text="This is the last level of the course.",
                        bg=PALETTE["card_glass"],
                        fg=PALETTE["success"],
                        font=(FONT, 10, "bold"),
                    ).pack(anchor="w")

        tasks = self._get_tasks()
        if not tasks:
            tk.Label(self.road, text="No tasks found for this level.", bg=PALETTE["card_glass"], fg=PALETTE["danger"], font=(FONT, 11)).pack(anchor="w")
            return

        for index, task in enumerate(tasks):
            row = tk.Frame(self.road, bg=PALETTE["card_glass"])
            row.pack(fill="x", pady=6)
            side_pad = 40 if index % 2 == 0 else 210
            inner = tk.Frame(row, bg=PALETTE["card_glass"])
            inner.pack(anchor="w", padx=(side_pad, 0))
            if progress is None:
                unlocked = True
            else:
                #progress.completed_tasks зберігає скільки завдань користувач все пройшов
                unlocked = index <= progress.completed_tasks
            label = f"Task {index + 1}"
            kind = "task" if unlocked else "locked"
            command = (lambda i=index, t=task: self.open_task(i, t)) if unlocked else (lambda: self.status.config(text="This task is still locked. Finish the previous one first."))
            GlassButton(inner, label, command, kind=kind, width=180, height=54).pack(anchor="w")
            tk.Label(inner, text=getattr(task, "title", "Tap to open practice"), bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 9)).pack(anchor="w", padx=12, pady=(4, 0))

        self.status.config(text="")
        self.road_canvas.yview_moveto(0)
        self.road_canvas.configure(scrollregion=self.road_canvas.bbox("all"))

    def _get_tasks(self):
        selected_lang = self.controller.selected_lang
        selected_level = self.controller.selected_level
        if not selected_lang or not selected_level:
            return []
        level_id = get_model_id(selected_level, ["id_level", "level_id", "id"])
        return selected_lang.get_tasks(level_id)

    def open_task(self, index, task):
        from .pages_task import TaskPage
        self.controller.selected_task_index = index
        self.controller.selected_task = task
        self.controller.show_frame(TaskPage)

    def open_next_level(self, level):
        self.controller.selected_level = level
        self.controller.sync_progress()
        self.controller.show_frame(DashboardPage)

#профіль користувача з інформацією про прогрес
class AccountPage(GradientPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.card = self.make_card(width=700, height=600)
        self.body = tk.Frame(self.card, bg=PALETTE["card_glass"])
        self.body.pack(fill="both", expand=True, padx=36, pady=30)

        top = tk.Frame(self.body, bg=PALETTE["card_glass"])
        top.pack(fill="x")
        left = tk.Frame(top, bg=PALETTE["card_glass"])
        left.pack(side="left", fill="x", expand=True)
        self.create_badge(left, "player account").pack(anchor="w", pady=(0, 14))
        ttk.Label(left, text="Your profile", style="CardTitle.TLabel").pack(anchor="w")
        self.profile_hint = tk.Label(left, text="", bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 11))
        self.profile_hint.pack(anchor="w", pady=(8, 0))
        GlassButton(top, "Back to course", lambda: controller.show_frame(DashboardPage), kind="secondary", height=46, width=150, font=(FONT, 10, "bold")).pack(side="right")

        self.info_card = tk.Frame(self.body, bg=PALETTE["primary_soft"], highlightbackground=PALETTE["glass_border"], highlightthickness=1)
        self.info_card.pack(fill="x", pady=(24, 18))
        self.name_label = tk.Label(self.info_card, text="", bg=PALETTE["primary_soft"], fg=PALETTE["text"], font=(FONT, 14, "bold"))
        self.name_label.pack(anchor="w", padx=18, pady=(16, 6))
        self.email_label = tk.Label(self.info_card, text="", bg=PALETTE["primary_soft"], fg=PALETTE["muted"], font=(FONT, 11))
        self.email_label.pack(anchor="w", padx=18, pady=(0, 16))

        self.stats_frame = tk.Frame(self.body, bg=PALETTE["card_glass"])
        self.stats_frame.pack(fill="x")
        self.total_xp = tk.Label(self.stats_frame, text="", bg=PALETTE["card_glass"], fg=PALETTE["text"], font=(FONT, 11, "bold"))
        self.total_xp.pack(anchor="w", pady=(0, 10))
        self.total_tasks = tk.Label(self.stats_frame, text="", bg=PALETTE["card_glass"], fg=PALETTE["text"], font=(FONT, 11, "bold"))
        self.total_tasks.pack(anchor="w", pady=(0, 10))
        self.total_languages = tk.Label(self.stats_frame, text="", bg=PALETTE["card_glass"], fg=PALETTE["text"], font=(FONT, 11, "bold"))
        self.total_languages.pack(anchor="w", pady=(0, 10))
        self.current_course = tk.Label(self.stats_frame, text="", bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 10))
        self.current_course.pack(anchor="w", pady=(6, 0))

    def on_show(self):
        user = self.controller.current_user
        progress_items = self.controller.get_cached_progress_values()
        total_xp = sum(getattr(item, "xp", 0) for item in progress_items)
        total_tasks = sum(getattr(item, "completed_tasks", 0) for item in progress_items)
        completed_languages = len(self.controller.completed_language_ids)

        self.name_label.config(text=get_model_name(user, ["name_user", "name", "user_name", "username"], "Player"))
        self.email_label.config(text=get_model_name(user, ["email", "user_email"], "No email"))
        self.profile_hint.config(text="A quick look at your learning progress.")
        self.total_xp.config(text=f"Total XP: {total_xp}")
        self.total_tasks.config(text=f"Completed tasks: {total_tasks}")
        self.total_languages.config(text=f"Finished languages: {completed_languages}")
        lang_name = get_model_name(self.controller.selected_lang, ["name_lang", "name"], "No language selected")
        level_name = get_model_name(self.controller.selected_level, ["name_level", "name"], "No level selected")
        self.current_course.config(text=f"Current focus: {lang_name} • {level_name}")