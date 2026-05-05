import os
import re
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from .constants import PALETTE, FONT
from .base_page import GradientPage, AuthPage
from .widgets import GlassButton
#сторінки до входу в систему

#стартовий екран із логотипом і кнопкою початку
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
            os.path.join(os.path.dirname(__file__), "assets", "sticker.webp"),
            os.path.join("assets", "sticker.webp"),
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

#форма входу (email і пароль)
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
        from models.user import User
        email = self.email.get().strip()
        password = self.password.get()
        user = User.login(email, password)
        if user:
            self.controller.current_user = user
            self.status.config(text="", fg=PALETTE["success"])
            from .pages_learning import LanguagePage
            self.controller.show_frame(LanguagePage)
        else:
            self.status.config(text="Wrong email or password", fg=PALETTE["danger"])

    def on_show(self):
        self.password.delete(0, tk.END)
        self.status.config(text="")

#форма реєстрації з валідацією даних
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
        from models.user import User
        from .pages_learning import LanguagePage
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