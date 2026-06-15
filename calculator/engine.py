"""Safe expression evaluator for scientific calculations."""

import ast
import math
import operator
from typing import Any, Callable

class CalculatorError(Exception):
    """Raised when an expression cannot be evaluated."""


class _SafeEvaluator(ast.NodeVisitor):
    OPERATORS: dict[type, Callable[..., Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    FUNCTIONS: dict[str, Callable[..., Any]] = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "ln": math.log,
        "abs": abs,
        "factorial": math.factorial,
        "degrees": math.degrees,
        "radians": math.radians,
        "floor": math.floor,
        "ceil": math.ceil,
        "exp": math.exp,
        "pow": pow,
    }

    CONSTANTS: dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def visit(self, node: ast.AST) -> Any:
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise CalculatorError(f"Unsupported constant type: {type(node.value).__name__}")

    def visit_Num(self, node: ast.Num) -> Any:  # noqa: N802 — ast legacy node
        return node.n

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in self.CONSTANTS:
            return self.CONSTANTS[node.id]
        raise CalculatorError(f"Unknown name: {node.id}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.OPERATORS:
            raise CalculatorError(f"Unsupported operator: {op_type.__name__}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        try:
            return self.OPERATORS[op_type](left, right)
        except ZeroDivisionError:
            raise CalculatorError("Division by zero") from None
        except ValueError as exc:
            raise CalculatorError(str(exc)) from exc

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.OPERATORS:
            raise CalculatorError(f"Unsupported unary operator: {op_type.__name__}")
        return self.OPERATORS[op_type](self.visit(node.operand))

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise CalculatorError("Only simple function calls are supported")
        name = node.func.id
        if name not in self.FUNCTIONS:
            raise CalculatorError(f"Unknown function: {name}")
        if node.keywords:
            raise CalculatorError("Keyword arguments are not supported")
        args = [self.visit(arg) for arg in node.args]
        try:
            return self.FUNCTIONS[name](*args)
        except (ValueError, TypeError) as exc:
            raise CalculatorError(str(exc)) from exc

    def generic_visit(self, node: ast.AST) -> Any:
        raise CalculatorError(f"Unsupported syntax: {type(node).__name__}")


class CalculatorEngine:
    """Evaluates mathematical expressions with scientific functions."""

    HELP_TEXT = """
Expert Calculator — supported syntax

  Operators:  +  -  *  /  //  %  **  ( )
  Constants:  pi  e  tau
  Functions:  sin cos tan asin acos atan sinh cosh tanh
              sqrt log log10 ln abs factorial
              degrees radians floor ceil exp pow

Examples:
  2 + 3 * 4
  sqrt(16) + sin(pi / 2)
  log(100, 10)
  factorial(5)
  pow(2, 10)
""".strip()

    def __init__(self) -> None:
        self._history: list[tuple[str, float]] = []

    @property
    def history(self) -> list[tuple[str, float]]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()

    def evaluate(self, expression: str) -> float:
        """Evaluate a math expression and return the numeric result."""
        cleaned = expression.strip()
        if not cleaned:
            raise CalculatorError("Empty expression")

        # Allow ^ as power operator (common on calculators).
        cleaned = cleaned.replace("^", "**")

        try:
            tree = ast.parse(cleaned, mode="eval")
        except SyntaxError as exc:
            raise CalculatorError(f"Invalid syntax: {exc.msg}") from exc

        result = _SafeEvaluator().visit(tree)
        if not isinstance(result, (int, float)):
            raise CalculatorError("Expression did not produce a number")

        numeric = float(result)
        self._history.append((expression.strip(), numeric))
        return numeric
