"""Command-line interface for Cronem."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from datetime import date as date_type

import keyring
from dotenv import load_dotenv

from .API import HALLS, MenuAPIError, fetch_menu, get_today
from .Login import APP_DIR, ENV_PATH, KEYRING_SERVICE, load_credentials


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="Cronem", description="Cronometer automation CLI for UofSC dining halls")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("login", help="securely save Kernel and Cronometer credentials")
    add = commands.add_parser("add", help="add menu foods to Cronometer")
    add.add_argument("--dry-run", action="store_true")
    add.add_argument("--yes", action="store_true")
    add.add_argument("--verbose", action="store_true")
    commands.add_parser("halls", help="list supported dining halls")
    menu = commands.add_parser("menu", help="show a dining menu")
    menu.add_argument("--hall", choices=HALLS.values(), required=True)
    menu.add_argument("--meal", choices=("breakfast", "lunch", "dinner"), required=True)
    menu.add_argument("--date", default=date_type.today().isoformat(), help="YYYY-MM-DD")
    commands.add_parser("doctor", help="check configuration and credentials")
    return parser


def run_login() -> int:
    APP_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    APP_DIR.chmod(0o700)
    api_key = getpass.getpass("Enter your Kernel API key: ").strip()
    username = input("Enter your Cronometer email: ").strip()
    password = getpass.getpass("Enter your Cronometer password: ")
    if not api_key or not username or not password:
        raise ValueError("API key, email, and password are all required.")
    ENV_PATH.write_text(
        f"KERNEL_API_KEY={json.dumps(api_key)}\nCRONOMETER_USERNAME={json.dumps(username)}\n", encoding="utf-8"
    )
    ENV_PATH.chmod(0o600)
    keyring.set_password(KEYRING_SERVICE, username, password)
    print(f"Configuration saved to {ENV_PATH}; password saved in the system keyring.")
    return 0


def run_menu(hall: str, meal: str, requested_date: str) -> int:
    parsed = date_type.fromisoformat(requested_date)
    data = fetch_menu(hall, meal, str(parsed.year), f"{parsed.month:02d}", f"{parsed.day:02d}")
    day = get_today(data, parsed.isoformat())
    if not day:
        print("No menu found.")
        return 0
    for item in day.get("menu_items", []):
        if item.get("food"):
            print(item["food"]["name"])
    return 0


def run_doctor() -> int:
    load_dotenv(ENV_PATH)
    checks = {
        "configuration directory is private": APP_DIR.exists() and (APP_DIR.stat().st_mode & 0o077) == 0,
        "credential file is private": ENV_PATH.exists() and (ENV_PATH.stat().st_mode & 0o077) == 0,
        "Kernel API key is configured": bool(os.getenv("KERNEL_API_KEY")),
    }
    try:
        load_credentials()
        checks["Cronometer credentials are configured"] = True
    except (RuntimeError, OSError, keyring.errors.KeyringError):
        checks["Cronometer credentials are configured"] = False
    for label, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {label}")
    return 0 if all(checks.values()) else 1


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "login":
            return run_login()
        if args.command == "add":
            from .Kernel import run_add

            return run_add(dry_run=args.dry_run, assume_yes=args.yes, verbose=args.verbose)
        if args.command == "halls":
            for number, hall in HALLS.items():
                print(f"{number}: {hall}")
            return 0
        if args.command == "menu":
            return run_menu(args.hall, args.meal, args.date)
        return run_doctor()
    except (MenuAPIError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
