"""Nutrislice menu access and dining hall selection."""

from __future__ import annotations

from collections.abc import Callable

import requests

HALLS = {
    "1": "garnet-station",
    "2": "fresh-greenes",
    "3": "gibbes-court-bistro",
    "4": "honeycomb-cafe",
    "5": "the-community-table",
    "6": "the-pavillion",
}


class MenuAPIError(RuntimeError):
    """Raised when a dining menu cannot be retrieved or decoded."""


def select_hall(input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print) -> str:
    output_fn("USC Dining Halls:")
    for number, slug in HALLS.items():
        output_fn(f"{number}: {slug.replace('-', ' ').title()}")
    while True:
        choice = input_fn("Enter the number of the dining hall you ate at: ").strip()
        if choice in HALLS:
            return HALLS[choice]
        output_fn(f"Please enter a number from 1 to {len(HALLS)}.")


def fetch_menu(
    hall: str, menu_slug: str, year: str, month: str, day: str, *, timeout: float = 15.0, session=requests
) -> dict:
    if hall not in HALLS.values():
        raise ValueError(f"Unknown dining hall: {hall!r}")
    if menu_slug not in {"breakfast", "lunch", "dinner"}:
        raise ValueError(f"Unknown meal: {menu_slug!r}")
    url = (
        f"https://sc.api.nutrislice.com/menu/api/weeks/school/{hall}/"
        f"menu-type/{menu_slug}/{year}/{month}/{day}/?format=json"
    )
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise MenuAPIError(f"Could not retrieve the dining menu: {exc}") from exc
    except ValueError as exc:
        raise MenuAPIError("The dining service returned invalid menu data.") from exc
    if not isinstance(data, dict):
        raise MenuAPIError("The dining service returned an unexpected response.")
    return data


def get_today(data: dict, date: str) -> dict | None:
    return next((day for day in data.get("days", []) if day.get("date") == date), None)


Hallsel = select_hall
