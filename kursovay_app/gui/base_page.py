import tkinter as tk
from tkinter import ttk
from .constants import PALETTE, FONT
from .widgets import GlassButton
#базові класи сторінки

#малює градієнтний фон
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
#створення картки
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
#мітка
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
#поле вводу
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

#розширює GradientPage
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

#використовується для сторінок вибору (мови/рівня)
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
#для відображення списку кнопок
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