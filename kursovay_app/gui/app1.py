import os
import re
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.language import Language
from models.level import Level
from models.user import User

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


PALETTE = {
    "bg_top": "#fdf9fc",
    "bg_bottom": "#f6edf2",
    "blob_1": "#f5dce7",
    "blob_2": "#f5ecd8",
    "blob_3": "#ece3f5",
    "card": "#fffdfd",
    "card_edge": "#eadde5",
    "card_glass": "#fff8fb",
    "text": "#352a33",
    "muted": "#7b7179",
    "primary": "#ead1dc",
    "primary_hover": "#e3c2d1",
    "primary_soft": "#f8eef3",
    "secondary": "#ffffff",
    "secondary_hover": "#faf4f7",
    "success": "#74a88f",
    "danger": "#bc7f95",
    "field": "#fffefe",
    "field_border": "#e7dbe2",
    "field_focus": "#d8b8c7",
    "pill": "#f7f0f4",
    "shadow": "#eadbe3",
    "glass": "#fdf7fa",
    "glass_border": "#efe2e8",
    "progress_bg": "#f2e9ef",
    "progress_fill": "#d9b3c5",
    "locked": "#efe8ec",
    "completed": "#e2e0e4",
}
FONT = "Helvetica"

def get_model_id(obj, candidates):
    for name in candidates:
        if hasattr(obj, name):
            return getattr(obj, name)
    return None
def get_model_name(obj, candidates, fallback):
    for name in candidates:
        if hasattr(obj, name):
            return str(getattr(obj, name))
    return fallback
def get_answer_text(answer):
    for name in ("answer_text", "text", "title", "name_answer", "value"):
        if hasattr(answer, name):
            value = getattr(answer, name)
            if value is not None:
                return str(value)
    if isinstance(answer, str):
        return answer
    return None
class GlassButton(tk.Frame):
    def __init__(
        self,
        parent,
        text,
        command,
        kind="primary",
        height=52,
        width=None,
        font=(FONT, 11, "bold"),
        state="normal",
    ):
        super().__init__(parent, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        self.command = command
        self.kind = kind
        self.state = state
        self.text = text
        self.height = height
        self.width = width
        self.font = font
        self.canvas = tk.Canvas(
            self,
            height=height,
            width=width or 260,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._redraw)
        for target in (self, self.canvas):
            target.bind("<Button-1>", self._handle_click)
            target.bind("<Enter>", self._handle_enter)
            target.bind("<Leave>", self._handle_leave)
        self.hover = False
        self._redraw()
    def _palette(self):
        if self.kind == "secondary":
            return PALETTE["glass"], PALETTE["secondary_hover"], PALETTE["glass_border"], PALETTE["text"]
        if self.kind == "danger":
            return "#f7e8ee", "#f2d7e1", "#e8c8d5", PALETTE["danger"]
        if self.kind == "task":
            return PALETTE["glass"], PALETTE["primary_soft"], PALETTE["glass_border"], PALETTE["text"]
        if self.kind == "completed":
            return PALETTE["completed"], PALETTE["completed"], PALETTE["field_border"], PALETTE["muted"]
        if self.kind == "locked":
            return PALETTE["locked"], PALETTE["locked"], PALETTE["field_border"], PALETTE["muted"]
        return PALETTE["primary"], PALETTE["primary_hover"], PALETTE["glass_border"], PALETTE["text"]
    def _draw_round_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=36,
            fill=fill,
            outline=outline,
            width=1,
        )
    def _redraw(self, event=None):
        width = event.width if event else (self.width or self.winfo_width() or 260)
        height = event.height if event else self.height
        self.canvas.config(width=width, height=height)
        self.canvas.delete("all")
        fill, hover_fill, border, text_color = self._palette()
        current_fill = hover_fill if self.hover and self.state == "normal" else fill
        radius = min(height // 2, 22)
        self._draw_round_rect(1, 1, width - 2, height - 2, radius, current_fill, border)
        self.canvas.create_text(
            width / 2,
            height / 2,
            text=self.text,
            fill=text_color,
            font=self.font,
        )
    def _handle_click(self, _event):
        if self.state == "normal" and callable(self.command):
            self.command()
    def _handle_enter(self, _event):
        if self.state == "normal":
            self.hover = True
            self._redraw()
    def _handle_leave(self, _event):
        self.hover = False
        self._redraw()
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TailCode")
        self.geometry("980x720")
        self.minsize(980, 720)
        self.configure(bg=PALETTE["bg_top"])
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
        for page in (
            StartPage,
            LoginPage,
            RegisterPage,
            LanguagePage,
            LevelPage,
            DashboardPage,
            AccountPage,
            TaskPage,
        ):
            frame = page(self.container, self)
            self.frames[page] = frame
            frame.place(relwidth=1, relheight=1)
        self.show_frame(StartPage)
    def _configure_styles(self):
        self.style.configure(
            "CardTitle.TLabel",
            background=PALETTE["card"],
            foreground=PALETTE["text"],
            font=(FONT, 24, "bold"),
        )
        self.style.configure(
            "CardText.TLabel",
            background=PALETTE["card"],
            foreground=PALETTE["muted"],
            font=(FONT, 11),
        )
        self.style.configure(
            "FieldLabel.TLabel",
            background=PALETTE["card"],
            foreground=PALETTE["muted"],
            font=(FONT, 10, "bold"),
        )
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
class GradientPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PALETTE["bg_top"])
        self.controller = controller
        self.canvas = tk.Canvas(self, bg=PALETTE["bg_top"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._redraw_background)
        self.content = tk.Frame(self.canvas, bg=PALETTE["bg_top"], highlightthickness=0)
        self.canvas_window = self.canvas.create_window(0, 0, anchor="nw", window=self.content)
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width, height=event.height),
            add="+",
        )
    def _redraw_background(self, event=None):
        width = self.canvas.winfo_width() or 980
        height = self.canvas.winfo_height() or 720
        self.canvas.delete("bg")
        steps = 42
        for i in range(steps):
            ratio = i / max(steps - 1, 1)
            color = self._mix(PALETTE["bg_top"], PALETTE["bg_bottom"], ratio)
            y0 = int(height * i / steps)
            y1 = int(height * (i + 1) / steps) + 1
            self.canvas.create_rectangle(0, y0, width, y1, fill=color, outline="", tags="bg")
        self.canvas.create_oval(-80, -60, 300, 250, fill=PALETTE["blob_2"], outline="", tags="bg")
        self.canvas.create_oval(width - 340, 40, width - 20, 320, fill=PALETTE["blob_3"], outline="", tags="bg")
        self.canvas.create_oval(width - 280, height - 240, width + 30, height + 30, fill=PALETTE["blob_1"], outline="", tags="bg")
    @staticmethod
    def _mix(color1, color2, ratio):
        rgb1 = [int(color1[i:i + 2], 16) for i in (1, 3, 5)]
        rgb2 = [int(color2[i:i + 2], 16) for i in (1, 3, 5)]
        mixed = [int(rgb1[i] + (rgb2[i] - rgb1[i]) * ratio) for i in range(3)]
        return "#{:02x}{:02x}{:02x}".format(*mixed)
    def make_card(self, width=430, height=470):
        shadow = tk.Frame(self.content, bg=PALETTE["shadow"], highlightthickness=0)
        shadow.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height, x=12, y=14)
        card = tk.Frame(
            self.content,
            bg=PALETTE["card_glass"],
            highlightbackground=PALETTE["card_edge"],
            highlightthickness=1,
            bd=0,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height)
        return card
    def create_badge(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            bg=PALETTE["primary_soft"],
            fg=PALETTE["danger"],
            font=(FONT, 9, "bold"),
            padx=12,
            pady=6,
        )
    def create_entry(self, parent, show=None):
        wrapper = tk.Frame(
            parent,
            bg=PALETTE["field"],
            highlightbackground=PALETTE["field_border"],
            highlightthickness=1,
            bd=0,
        )
        entry = tk.Entry(
            wrapper,
            relief="flat",
            bd=0,
            bg=PALETTE["field"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            font=(FONT, 12),
            show=show,
        )
        entry.pack(fill="x", padx=16, pady=13)
        entry.bind("<FocusIn>", lambda _e: wrapper.config(highlightbackground=PALETTE["field_focus"]))
        entry.bind("<FocusOut>", lambda _e: wrapper.config(highlightbackground=PALETTE["field_border"]))
        return wrapper, entry
class StartPage(GradientPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        card = self.make_card(width=500, height=560)
        tk.Frame(card, bg=PALETTE["primary_soft"], width=120, height=120).place(x=28, y=28)
        badge = self.create_badge(card, "playful coding journey")
        badge.pack(anchor="w", padx=36, pady=(34, 14))
        hero = tk.Frame(card, bg=PALETTE["card_glass"])
        hero.pack(fill="both", expand=True, padx=36, pady=(0, 30))
        self.logo = None
        image_box = tk.Frame(hero, bg=PALETTE["card_glass"])
        image_box.pack(pady=(10, 22))
        self._load_image(image_box)
        ttk.Label(hero, text="TailCode", style="CardTitle.TLabel").pack()
        ttk.Label(
            hero,
            text="A softer, friendlier way to learn programming step by step.",
            style="CardText.TLabel",
            justify="center",
            wraplength=340,
        ).pack(pady=(10, 22))
        tk.Label(
            hero,
            text="Start with your account, choose a language and level, then keep moving through a clear learning path.",
            bg=PALETTE["card_glass"],
            fg=PALETTE["muted"],
            font=(FONT, 11),
            justify="center",
            wraplength=340,
        ).pack(pady=(0, 34))
        tk.Frame(hero, bg=PALETTE["card_glass"], height=18).pack()
        GlassButton(hero, "Start learning", lambda: controller.show_frame(LoginPage), kind="primary").pack(fill="x")
    def _load_image(self, parent):
        asset_candidates = [
            os.path.join(os.path.dirname(__file__), "assets", "start.png"),
            os.path.join("assets", "start.png"),
        ]
        asset_path = next((path for path in asset_candidates if os.path.exists(path)), None)
        if asset_path:
            try:
                image = Image.open(asset_path).resize((220, 180))
                self.logo = ImageTk.PhotoImage(image)
                tk.Label(parent, image=self.logo, bg=PALETTE["card_glass"]).pack()
                return
            except Exception:
                pass
        tk.Label(
            parent,
            text="<>",
            bg=PALETTE["primary_soft"],
            fg=PALETTE["danger"],
            font=(FONT, 40, "bold"),
            width=6,
            height=2,
        ).pack()
class AuthPage(GradientPage):
    def __init__(self, parent, controller, title, subtitle, height=540):
        super().__init__(parent, controller)
        self.card = self.make_card(width=500, height=height)
        self.body = tk.Frame(self.card, bg=PALETTE["card_glass"])
        self.body.pack(fill="both", expand=True, padx=36, pady=30)
        self.create_badge(self.body, "secure access").pack(anchor="w", pady=(0, 14))
        ttk.Label(self.body, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(self.body, text=subtitle, style="CardText.TLabel", wraplength=360, justify="left").pack(anchor="w", pady=(10, 24))
    def add_field(self, label_text, show=None):
        ttk.Label(self.body, text=label_text, style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 6))
        wrapper, entry = self.create_entry(self.body, show=show)
        wrapper.pack(fill="x", pady=(0, 14))
        return entry
    def add_status(self):
        label = tk.Label(
            self.body,
            text="",
            bg=PALETTE["card_glass"],
            fg=PALETTE["danger"],
            font=(FONT, 10),
            anchor="w",
            justify="left",
            wraplength=360,
        )
        label.pack(fill="x", pady=(4, 14))
        return label
class LoginPage(AuthPage):
    def __init__(self, parent, controller):
        super().__init__(
            parent,
            controller,
            title="Welcome back",
            subtitle="Log in to continue your path and pick the language you want to practice today.",
            height=560,
        )
        self.email = self.add_field("Email")
        self.password = self.add_field("Password", show="*")
        self.status = self.add_status()
        GlassButton(self.body, "Log in", self.login, kind="primary").pack(fill="x", pady=(8, 12))
        GlassButton(self.body, "Registration", lambda: controller.show_frame(RegisterPage), kind="secondary").pack(fill="x")
    def login(self):
        email = self.email.get().strip()
        password = self.password.get()
        user = User.login(email, password)
        if user:
            self.controller.current_user = user
            self.status.config(text="", fg=PALETTE["success"])
            self.controller.show_frame(LanguagePage)
        else:
            self.status.config(text="Wrong email or password", fg=PALETTE["danger"])
    def on_show(self):
        self.password.delete(0, tk.END)
        self.status.config(text="")
class RegisterPage(AuthPage):
    def __init__(self, parent, controller):
        super().__init__(
            parent,
            controller,
            title="Create your account",
            subtitle="Fill in the fields below. When everything is valid, you will go straight to language selection.",
            height=640,
        )
        self.name = self.add_field("Name")
        self.email = self.add_field("Email")
        self.password = self.add_field("Password", show="*")
        self.status = self.add_status()
        GlassButton(self.body, "Create account", self.register, kind="primary").pack(fill="x", pady=(8, 12))
        GlassButton(self.body, "Back to login", lambda: controller.show_frame(LoginPage), kind="secondary").pack(fill="x")
    @staticmethod
    def validate(name, email, password):
        if len(name.strip()) < 2:
            return "Name must be at least 2 characters"
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email format"
        if len(password) < 6:
            return "Password must be at least 6 characters"
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            return "Password must contain letters and numbers"
        return None
    def register(self):
        name = self.name.get().strip()
        email = self.email.get().strip()
        password = self.password.get()
        error = self.validate(name, email, password)
        if error:
            self.status.config(text=error, fg=PALETTE["danger"])
            return
        try:
            user = User(None, name, email, password)
            user.register()
            self.controller.current_user = user
            self.status.config(text="Account created successfully", fg=PALETTE["success"])
            self.controller.after(700, lambda: self.controller.show_frame(LanguagePage))
        except Exception as exc:
            self.status.config(text=str(exc), fg=PALETTE["danger"])
    def on_show(self):
        self.status.config(text="")
class ChoicePage(GradientPage):
    def __init__(self, parent, controller, title, subtitle):
        super().__init__(parent, controller)
        self.card = self.make_card(width=560, height=580)
        self.body = tk.Frame(self.card, bg=PALETTE["card_glass"])
        self.body.pack(fill="both", expand=True, padx=36, pady=30)
        self.create_badge(self.body, "next step").pack(anchor="w", pady=(0, 14))
        ttk.Label(self.body, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(self.body, text=subtitle, style="CardText.TLabel", wraplength=410, justify="left").pack(anchor="w", pady=(10, 22))
        self.list_frame = tk.Frame(self.body, bg=PALETTE["card_glass"])
        self.list_frame.pack(fill="both", expand=True)
        self.footer = tk.Label(self.body, text="", bg=PALETTE["card_glass"], fg=PALETTE["muted"], font=(FONT, 10))
        self.footer.pack(anchor="w", pady=(10, 0))
    def render_choices(self, items, label_getter, command_getter, empty_text, kind_getter=None):
        for child in self.list_frame.winfo_children():
            child.destroy()
        if not items:
            tk.Label(
                self.list_frame,
                text=empty_text,
                bg=PALETTE["card_glass"],
                fg=PALETTE["danger"],
                font=(FONT, 11),
                wraplength=380,
                justify="left",
            ).pack(anchor="w", pady=8)
            return
        for item in items:
            kind = kind_getter(item) if kind_getter else "task"
            GlassButton(self.list_frame, label_getter(item), command_getter(item), kind=kind, height=54).pack(fill="x", pady=7)
class LanguagePage(ChoicePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="Choose language", subtitle="Pick what you want to study first. You can keep the flow playful and focused.")
    def on_show(self):
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
class LevelPage(ChoicePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="Choose level", subtitle="Select your pace. Start easy or jump to a more confident stage.")
    def on_show(self):
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
class ProgressBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=parent.cget("bg"))
        self.canvas = tk.Canvas(self, height=18, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        self.canvas.pack(fill="x", expand=True)
        self.value = 0
        self.canvas.bind("<Configure>", lambda _e: self.redraw())
    def set(self, value):
        self.value = max(0, min(1, value))
        self.redraw()
    def redraw(self):
        width = self.canvas.winfo_width() or 200
        height = self.canvas.winfo_height() or 18
        self.canvas.delete("all")
        radius = height // 2
        self._draw_bar(0, 0, width, height, radius, PALETTE["progress_bg"])
        fill_width = max(radius * 2, int(width * self.value)) if self.value > 0 else 0
        if fill_width > 0:
            self._draw_bar(0, 0, min(fill_width, width), height, radius, PALETTE["progress_fill"])
    def _draw_bar(self, x1, y1, x2, y2, r, fill):
        self.canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=180, fill=fill, outline=fill)
        self.canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=270, extent=180, fill=fill, outline=fill)
        self.canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=fill)
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
        self.road_canvas = tk.Canvas(
            self.road_wrap,
            bg=PALETTE["card_glass"],
            highlightthickness=0,
            bd=0,
        )
        self.road_canvas.pack(side="left", fill="both", expand=True)
        self.road_scroll = tk.Scrollbar(
            self.road_wrap,
            orient="vertical",
            command=self.road_canvas.yview,
        )
        self.road_scroll.pack(side="right", fill="y")
        self.road_canvas.configure(yscrollcommand=self.road_scroll.set)
        self.road = tk.Frame(self.road_canvas, bg=PALETTE["card_glass"])
        self.road_window = self.road_canvas.create_window((0, 0), anchor="nw", window=self.road)
        self.road.bind(
            "<Configure>",
            lambda _e: self.road_canvas.configure(scrollregion=self.road_canvas.bbox("all")),
        )
        self.road_canvas.bind(
            "<Configure>",
            lambda event: self.road_canvas.itemconfigure(self.road_window, width=event.width),
        )
        self.road_canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
    def _on_mousewheel(self, event):
        if self.winfo_ismapped():
            self.road_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def on_show(self):
        self.render_dashboard()
    def render_dashboard(self):
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
        self.controller.selected_task_index = index
        self.controller.selected_task = task
        self.controller.show_frame(TaskPage)
    def open_next_level(self, level):
        self.controller.selected_level = level
        self.controller.sync_progress()
        self.controller.show_frame(DashboardPage)
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
if __name__ == "__main__":
    app = App()
    app.mainloop()
    # разделить на части фалы