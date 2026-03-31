from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Usage: python -m template [cli|web|gui|airflow|lib|telegram] ...")
        return 1

    command = args.pop(0)
    if command == "cli":
        from template.app.cli.main import run as run_cli

        return run_cli(args)
    if command == "web":
        from template.app.web.main import run as run_web

        return run_web(args)
    if command == "gui":
        from template.app.gui.main import run as run_gui

        return run_gui(args)
    if command == "airflow":
        from template.app.airflow.dag import run as run_airflow

        return run_airflow(args)
    if command == "lib":
        from template.app.lib.main import run as run_lib

        return run_lib(args)
    if command == "telegram":
        from template.app.telegram.main import run as run_telegram

        return run_telegram(args)

    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
