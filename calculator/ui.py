"""Graphical calculator UI with clickable number and symbol buttons."""

import sys
import tkinter as tk
from tkinter import font as tkfont

from calculator import CalculatorEngine, CalculatorError


class CalculatorUI:
    """Tkinter calculator that builds expressions from button clicks."""

    # Clean white theme
    BG = "#ffffff"
    DISPLAY_BG = "#ffffff"
    BORDER = "#e8e8e8"
    TEXT = "#111827"
    TEXT_MUTED = "#6b7280"
    BTN_NUM_BG = "#f9fafb"
    BTN_NUM_ACTIVE = "#f3f4f6"
    BTN_OP_BG = "#f9fafb"
    BTN_OP_ACTIVE = "#f3f4f6"
    BTN_FN_BG = "#f9fafb"
    BTN_FN_ACTIVE = "#f3f4f6"
    BTN_FN_FG = "#4b5563"
    BTN_OP_FG = "#2563eb"
    BTN_EQ_BG = "#2563eb"
    BTN_EQ_ACTIVE = "#1d4ed8"
    BTN_EQ_FG = "#ffffff"
    BTN_CLEAR_FG = "#dc2626"
    BTN_CLEAR_ACTIVE = "#fee2e2"

    DISPLAY_HEIGHT = 100
    BTN_PAD = 2
    MARGIN = 4

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = CalculatorEngine()
        self.expression = ""
        self._last_expression = ""

        root.title("Calculator")
        root.configure(bg=self.BG)
        root.resizable(False, False)
        root.geometry("336x520")
        self._remove_title_bar_icon(root)

        self.content = tk.Frame(self.root, bg=self.BG, padx=self.MARGIN, pady=self.MARGIN)
        self.content.pack(fill="both", expand=True)

        self._build_display()
        self._build_separator()
        self._build_buttons()

    @staticmethod
    def _remove_title_bar_icon(root: tk.Tk) -> None:
        """Hide the default Python/tk icon beside the window title."""
        try:
            blank = tk.PhotoImage(width=16, height=16)
            root.iconphoto(True, blank)
            root._blank_icon = blank  # keep reference alive
        except tk.TclError:
            pass

        if sys.platform == "win32":
            try:
                import ctypes

                hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
                ctypes.windll.user32.SetClassLongPtrW(hwnd, -34, 0)  # GCLP_HICONSM
                ctypes.windll.user32.SetClassLongPtrW(hwnd, -14, 0)  # GCLP_HICON
            except (AttributeError, OSError):
                pass

    def _build_display(self) -> None:
        panel = tk.Frame(
            self.content,
            bg=self.DISPLAY_BG,
            height=self.DISPLAY_HEIGHT,
        )
        panel.pack(fill="x")
        panel.pack_propagate(False)

        self.expr_font = tkfont.Font(family="Segoe UI", size=14)
        self.result_font = tkfont.Font(family="Segoe UI", size=28, weight="normal")

        self.expr_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="0")

        tk.Label(
            panel,
            textvariable=self.expr_var,
            anchor="e",
            bg=self.DISPLAY_BG,
            fg=self.TEXT_MUTED,
            font=self.expr_font,
            height=1,
            wraplength=328,
        ).pack(fill="x", pady=2)

        tk.Label(
            panel,
            textvariable=self.result_var,
            anchor="e",
            bg=self.DISPLAY_BG,
            fg=self.TEXT,
            font=self.result_font,
            height=1,
            wraplength=328,
        ).pack(fill="x", pady=2)

    def _build_separator(self) -> None:
        tk.Frame(self.content, bg=self.BORDER, height=1).pack(fill="x")

    def _build_buttons(self) -> None:
        pad = tk.Frame(self.content, bg=self.BG)
        pad.pack(fill="x")

        self.btn_font = tkfont.Font(family="Segoe UI", size=14)
        self.btn_font_sm = tkfont.Font(family="Segoe UI", size=12)

        rows = [
            [
                ("sin", "sin("),
                ("cos", "cos("),
                ("tan", "tan("),
                ("sqrt", "sqrt("),
                ("^", "^"),
            ],
            [
                ("log", "log("),
                ("ln", "ln("),
                ("(", "("),
                (")", ")"),
                ("%", "%"),
            ],
            [
                ("7", "7"),
                ("8", "8"),
                ("9", "9"),
                ("/", "/"),
                ("C", "CLEAR"),
            ],
            [
                ("4", "4"),
                ("5", "5"),
                ("6", "6"),
                ("*", "*"),
                ("⌫", "BACK"),
            ],
            [
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("-", "-"),
                ("pi", "pi"),
            ],
            [
                ("0", "0"),
                (".", "."),
                ("e", "e"),
                ("+", "+"),
                ("=", "EQUALS"),
            ],
        ]

        for col in range(5):
            pad.grid_columnconfigure(col, weight=1, uniform="col")
        for row in range(len(rows)):
            pad.grid_rowconfigure(row, weight=1, uniform="row")

        for row_idx, row in enumerate(rows):
            for col_idx, (label, action) in enumerate(row):
                style = self._button_style(label, action)
                self._make_button(pad, label, action, style).grid(
                    row=row_idx,
                    column=col_idx,
                    padx=self.BTN_PAD,
                    pady=self.BTN_PAD,
                    sticky="nsew",
                )

    def _button_style(self, label: str, action: str) -> dict[str, str]:
        if action == "CLEAR":
            return {
                "bg": self.BTN_NUM_BG,
                "active_bg": self.BTN_CLEAR_ACTIVE,
                "fg": self.BTN_CLEAR_FG,
                "active_fg": self.BTN_CLEAR_FG,
                "font": self.btn_font,
            }
        if action == "EQUALS":
            return {
                "bg": self.BTN_EQ_BG,
                "active_bg": self.BTN_EQ_ACTIVE,
                "fg": self.BTN_EQ_FG,
                "active_fg": self.BTN_EQ_FG,
                "font": self.btn_font,
            }
        if action in {"BACK", "+", "-", "*", "/", "%", "^", "(", ")"}:
            return {
                "bg": self.BTN_OP_BG,
                "active_bg": self.BTN_OP_ACTIVE,
                "fg": self.BTN_OP_FG,
                "active_fg": self.BTN_OP_FG,
                "font": self.btn_font,
            }
        if label in {"sin", "cos", "tan", "sqrt", "log", "ln", "pi", "e"}:
            return {
                "bg": self.BTN_FN_BG,
                "active_bg": self.BTN_FN_ACTIVE,
                "fg": self.BTN_FN_FG,
                "active_fg": self.TEXT,
                "font": self.btn_font_sm,
            }
        return {
            "bg": self.BTN_NUM_BG,
            "active_bg": self.BTN_NUM_ACTIVE,
            "fg": self.TEXT,
            "active_fg": self.TEXT,
            "font": self.btn_font,
        }

    def _make_button(
        self,
        parent: tk.Frame,
        label: str,
        action: str,
        style: dict[str, str],
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=label,
            font=style["font"],
            width=4,
            height=2,
            bg=style["bg"],
            fg=style["fg"],
            activebackground=style["active_bg"],
            activeforeground=style["active_fg"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.BORDER,
            cursor="hand2",
            command=lambda a=action: self._on_button(a),
        )

    def _on_button(self, action: str) -> None:
        if action == "CLEAR":
            self.expression = ""
            self._last_expression = ""
            self.expr_var.set("")
            self.result_var.set("0")
            return

        if action == "BACK":
            self.expression = self.expression[:-1]
            self.expr_var.set(self.expression)
            return

        if action == "EQUALS":
            self._evaluate()
            return

        if (
            self._last_expression
            and self.expression == self._last_expression
            and (action in {".",} or (len(action) == 1 and action.isdigit()))
        ):
            self.expression = ""
            self._last_expression = ""

        self.expression += action
        self.expr_var.set(self.expression)

    def _evaluate(self) -> None:
        if not self.expression.strip():
            return

        submitted = self.expression
        try:
            result = self.engine.evaluate(submitted)
            formatted = self._format_result(result)
            self.expr_var.set(submitted)
            self.result_var.set(formatted)
            self.expression = str(result)
            self._last_expression = self.expression
        except CalculatorError as exc:
            self.expr_var.set(submitted)
            self.result_var.set(f"Error: {exc}")
            self.expression = ""
            self._last_expression = ""

    @staticmethod
    def _format_result(value: float) -> str:
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return str(value)


def run_gui() -> None:
    root = tk.Tk()
    CalculatorUI(root)
    root.mainloop()
