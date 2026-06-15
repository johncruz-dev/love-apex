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


def _run_interactive(engine: CalculatorEngine) -> None:
    print("Expert Calculator (type 'help', 'history', or 'quit')")
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
        if command == "history":
            _print_history(engine)
            continue
        if command == "clear":
            engine.clear_history()
            print("History cleared.")
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
        help="Expression to evaluate (omit for interactive mode)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start interactive CLI mode",
    )
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help="Open graphical calculator window",
    )
    args = parser.parse_args(argv)

    if args.gui:
        from calculator.ui import run_gui

        run_gui()
        return 0

    engine = CalculatorEngine()

    if args.interactive or not args.expression:
        _run_interactive(engine)
        return 0

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
