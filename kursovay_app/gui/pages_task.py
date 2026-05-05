import tkinter as tk
from tkinter import ttk

from .constants import PALETTE, FONT
from .base_page import GradientPage
from .widgets import GlassButton
from .utils import get_model_name, get_answer_text
#сторінка виконання завдання

#відображає завдання, перевіряє відповідь користувача та оновлює прогрес
#Обробляє завершення рівня та переходи між етапами
class TaskPage(GradientPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.answer_mode = "entry"
        self.choice_var = tk.StringVar(value="")
        self.choice_buttons = []

        self.card = self.make_card(width=620, height=610)
        body = tk.Frame(self.card, bg=PALETTE["card_glass"])
        body.pack(fill="both", expand=True, padx=36, pady=30)

        top = tk.Frame(body, bg=PALETTE["card_glass"])
        top.pack(fill="x")
        left = tk.Frame(top, bg=PALETTE["card_glass"])
        left.pack(side="left", fill="x", expand=True)
        self.create_badge(left, "practice mode").pack(anchor="w", pady=(0, 14))
        ttk.Label(left, text="Solve the task", style="CardTitle.TLabel").pack(anchor="w")
        right = tk.Frame(top, bg=PALETTE["card_glass"])
        right.pack(side="right")
        GlassButton(right, "Back to map", lambda: controller.show_frame(DashboardPage), kind="secondary", height=46, width=140, font=(FONT, 10, "bold")).pack()

        self.meta = tk.Label(body, text="", bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 10))
        self.meta.pack(anchor="w", pady=(10, 18))

        self.question = tk.Label(
            body,
            text="",
            bg=PALETTE["primary_soft"],
            fg=PALETTE["text"],
            font=(FONT, 12),
            justify="left",
            wraplength=470,
            padx=18,
            pady=18,
        )
        self.question.pack(fill="x", pady=(0, 16))

        self.answer_label = ttk.Label(body, text="Your answer", style="FieldLabel.TLabel")
        self.answer_label.pack(anchor="w", pady=(0, 6))

        self.answer_area = tk.Frame(body, bg=PALETTE["card_glass"])
        self.answer_area.pack(fill="x", pady=(0, 16))
        self.answer_wrap, self.answer = self.create_entry(self.answer_area)
        self.answer_wrap.pack(fill="x")
        self.choice_wrap = tk.Frame(self.answer_area, bg=PALETTE["card_glass"])

        self.result = tk.Label(body, text="", bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 11, "bold"))
        self.result.pack(anchor="w", pady=(0, 18))
        GlassButton(body, "Check answer", self.check, kind="primary").pack(fill="x")

    def on_show(self):
        self.load_task()

    def load_task(self):
        task = self.controller.selected_task
        if not task:
            self.meta.config(text="No task selected.")
            self.question.config(text="Choose a task from the course map first.")
            self.result.config(text="", fg=PALETTE["muted"])
            return
        if hasattr(task, "load_answers"):
            task.load_answers()
        task_index = self.controller.selected_task_index + 1
        progress = self.controller.sync_progress()
        completed = progress.completed_tasks if progress else 0
        options = self._extract_options(task)
        self.meta.config(text=f"Task {task_index} • completed before this: {completed}")
        self.question.config(text=getattr(task, "question", "Question is unavailable."))
        self.answer.delete(0, tk.END)
        self.choice_var.set("")
        self.result.config(text="", fg=PALETTE["muted"])
        self._set_answer_mode(options)
#збільшується прогрес
    def check(self):
        user = self.controller.current_user
        task = self.controller.selected_task
        progress = self.controller.sync_progress()
        if not user or not task:
            self.result.config(text="User or task is unavailable.", fg=PALETTE["danger"])
            return
        user_answer = self.choice_var.get().strip() if self.answer_mode == "choice" else self.answer.get().strip()
        if not user_answer:
            self.result.config(text="Choose or enter an answer first.", fg=PALETTE["danger"])
            return
        is_correct = user.attempt_task(task, user_answer)
        if not is_correct:
            self.result.config(text="Wrong answer. Try again.", fg=PALETTE["danger"])
            return
        if progress and self.controller.selected_task_index == progress.completed_tasks:
            progress.complete_task()
            progress.add_xp(10)
        if progress and progress.is_level_completed():
            next_level = self.controller.get_next_level()
            if next_level is not None:
                self.result.config(text="Level completed. You can move to the next level.", fg=PALETTE["success"])
                self.after(900, lambda: self.controller.show_frame(DashboardPage))
                return
            lang_name = get_model_name(self.controller.selected_lang, ["name_lang", "name"], "this course")
            self.controller.mark_language_completed()
            self.result.config(text=f"Congratulations! You completed {lang_name}.", fg=PALETTE["success"])
            self.after(2000, lambda: self.controller.show_frame(LanguagePage))
            return
        self.result.config(text="Correct. Progress saved.", fg=PALETTE["success"])
        self.after(800, lambda: self.controller.show_frame(DashboardPage))

    def _extract_options(self, task):
        raw_answers = getattr(task, "answers", None)
        if not raw_answers:
            return []
        options = []
        for answer in raw_answers:
            text = get_answer_text(answer)
            if text:
                options.append(text)
        unique_options = []
        seen = set()
        for option in options:
            if option not in seen:
                seen.add(option)
                unique_options.append(option)
        return unique_options if len(unique_options) >= 2 else []

    def _set_answer_mode(self, options):
        for child in self.choice_wrap.winfo_children():
            child.destroy()
        self.choice_buttons.clear()
        if options:
            self.answer_mode = "choice"
            self.answer_wrap.pack_forget()
            self.choice_wrap.pack(fill="x")
            self.answer_label.config(text="Choose the correct answer")
            for option in options:
                button = tk.Button(
                    self.choice_wrap,
                    text=option,
                    command=lambda value=option: self._select_option(value),
                    relief="flat",
                    activebackground=PALETTE["primary_soft"],
                    activeforeground=PALETTE["text"],
                    bg=PALETTE["glass"],
                    fg=PALETTE["text"],
                    highlightthickness=1,
                    highlightbackground=PALETTE["glass_border"],
                    highlightcolor=PALETTE["field_focus"],
                    bd=0,
                    padx=14,
                    pady=12,
                    font=(FONT, 11),
                    anchor="w",
                    justify="left",
                    wraplength=430,
                    cursor="hand2",
                )
                button.pack(fill="x", pady=5)
                self.choice_buttons.append((option, button))
            self._refresh_choice_buttons()
            return
        self.answer_mode = "entry"
        self.choice_wrap.pack_forget()
        self.answer_wrap.pack(fill="x")
        self.answer_label.config(text="Your answer")

    def _select_option(self, value):
        self.choice_var.set(value)
        self._refresh_choice_buttons()

    def _refresh_choice_buttons(self):
        selected = self.choice_var.get()
        for option, button in self.choice_buttons:
            is_selected = option == selected
            button.config(
                bg=PALETTE["primary_soft"] if is_selected else PALETTE["glass"],
                fg=PALETTE["text"],
                activebackground=PALETTE["primary_soft"],
                highlightbackground=PALETTE["field_focus"] if is_selected else PALETTE["glass_border"],
            )

from .pages_learning import DashboardPage, LanguagePage