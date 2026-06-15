"""Graphical calculator UI with clickable number and symbol buttons."""

import tkinter as tk
from tkinter import font as tkfont

from calculator import CalculatorEngine, CalculatorError


class CalculatorUI:
    """Tkinter calculator that builds expressions from button clicks."""

    BG = "#1e1e2e"
    DISPLAY_BG = "#2a2a3c"
    BTN_BG = "#3b3b52"
    BTN_OP_BG = "#5c5c8a"
    BTN_FN_BG = "#4a6fa5"
    BTN_EQ_BG = "#6c9bcf"
    BTN_CLEAR_BG = "#c75c5c"
    FG = "#ececec"
    FG_DIM = "#a0a0b8"

    DISPLAY_HEIGHT = 96

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = CalculatorEngine()
        self.expression = ""
        self._last_expression = ""

        root.title("Expert Calculator")
        root.configure(bg=self.BG)
        root.resizable(False, False)
        root.geometry("340x520")

        self._build_display()
        self._build_buttons()

    def _build_display(self) -> None:
        display_frame = tk.Frame(self.root, bg=self.BG, padx=12, pady=12)
        display_frame.pack(fill="x")

        panel = tk.Frame(
            display_frame,
            bg=self.DISPLAY_BG,
            height=self.DISPLAY_HEIGHT,
        )
        panel.pack(fill="x")
        panel.pack_propagate(False)

        expr_font = tkfont.Font(family="Consolas", size=14)
        result_font = tkfont.Font(family="Consolas", size=28, weight="bold")

        self.expr_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="0")

        tk.Label(
            panel,
            textvariable=self.expr_var,
            anchor="e",
            bg=self.DISPLAY_BG,
            fg=self.FG_DIM,
            font=expr_font,
            padx=16,
            pady=8,
            height=1,
            wraplength=300,
        ).pack(fill="x")

        tk.Label(
            panel,
            textvariable=self.result_var,
            anchor="e",
            bg=self.DISPLAY_BG,
            fg=self.FG,
            font=result_font,
            padx=16,
            pady=8,
            height=1,
            wraplength=300,
        ).pack(fill="x")

    def _build_buttons(self) -> None:
        pad = tk.Frame(self.root, bg=self.BG, padx=12, pady=12)
        pad.pack()

        btn_font = tkfont.Font(family="Segoe UI", size=13)

        # (label, action) — action is text to append, or a special command name
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

        for row_idx, row in enumerate(rows):
            for col_idx, (label, action) in enumerate(row):
                bg = self._button_color(label, action)
                tk.Button(
                    pad,
                    text=label,
                    font=btn_font,
                    width=4,
                    height=2,
                    bg=bg,
                    fg=self.FG,
                    activebackground=bg,
                    activeforeground=self.FG,
                    relief="flat",
                    borderwidth=0,
                    command=lambda a=action: self._on_button(a),
                ).grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

    def _button_color(self, label: str, action: str) -> str:
        if action == "CLEAR":
            return self.BTN_CLEAR_BG
        if action == "EQUALS":
            return self.BTN_EQ_BG
        if action in {"BACK"}:
            return self.BTN_OP_BG
        if action in {"+", "-", "*", "/", "%", "^", "(", ")"}:
            return self.BTN_OP_BG
        if label in {"sin", "cos", "tan", "sqrt", "log", "ln", "pi", "e"}:
            return self.BTN_FN_BG
        return self.BTN_BG

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

        # After a result, digits and "." start a fresh number.
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
