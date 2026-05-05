import tkinter as tk
from .constants import PALETTE, FONT
#компоненти інтерфейсу

# кнопка із закругленими кутами
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


#горизонтальний прогрес-бар із закругленими краями
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