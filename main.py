"""Interactive CLI for the expert calculator."""

import argparse
import sys

from calculator import CalculatorEngine, CalculatorError


def _print_history(engine: CalculatorEngine) -> None:
    history = engine.history
    if not history:
        print("No calculations yet.")
        return
    for index, (expr, result) in enumerate(history, start=1):
        print(f"  {index}. {expr} = {result}")


def _looks_like_shell_command(line: str) -> bool:
    lowered = line.lower().strip()
    if lowered.startswith(("python ", "py ", "python.exe ")):
        return True
    if "gui.py" in lowered or "main.py" in lowered:
        return True
    return False


def _run_interactive(engine: CalculatorEngine) -> None:
    print("Expert Calculator CLI (type 'help', 'gui', 'history', or 'quit')")
    print("Tip: run 'python main.py --gui' from PowerShell to open the button UI.")
    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        command = line.lower()
        if command in {"quit", "exit", "q"}:
            break
        if command == "help":
            print(CalculatorEngine.HELP_TEXT)
            continue
        if command == "gui":
            from calculator.ui import run_gui

            run_gui()
            continue
        if command == "history":
            _print_history(engine)
            continue
        if command == "clear":
            engine.clear_history()
            print("History cleared.")
            continue
        if _looks_like_shell_command(line):
            print(
                "That looks like a shell command, not a math expression.\n"
                "  • Type 'gui' here to open the calculator window\n"
                "  • Or press Ctrl+C, then run: python main.py --gui"
            )
            continue

        try:
            result = engine.evaluate(line)
            print(result)
        except CalculatorError as exc:
            print(f"Error: {exc}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Expert calculator with scientific functions.",
    )
    parser.add_argument(
        "expression",
        nargs="*",
        help="Expression to evaluate",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start interactive CLI mode instead of the GUI",
    )
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help="Open graphical calculator window (default when no args)",
    )
    args = parser.parse_args(argv)

    if args.interactive:
        engine = CalculatorEngine()
        _run_interactive(engine)
        return 0

    if args.gui or not args.expression:
        from calculator.ui import run_gui

        run_gui()
        return 0

    engine = CalculatorEngine()

    expression = " ".join(args.expression)
    try:
        result = engine.evaluate(expression)
        print(result)
        return 0
    except CalculatorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
