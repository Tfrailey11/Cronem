"""Menu selection and nutrition transformation."""

from __future__ import annotations

from datetime import datetime
from difflib import get_close_matches

from .API import fetch_menu, get_today, select_hall


def menu_slug(hour: int) -> str:
    if not 0 <= hour <= 23:
        raise ValueError("hour must be between 0 and 23")
    if 6 <= hour < 12:
        return "breakfast"
    if 12 <= hour < 18:
        return "lunch"
    return "dinner"


def choose_meal(default: str) -> str:
    choice = input(f"Meal [breakfast/lunch/dinner] ({default}): ").strip().lower()
    if not choice:
        return default
    while choice not in {"breakfast", "lunch", "dinner"}:
        choice = input("Please enter breakfast, lunch, or dinner: ").strip().lower()
    return choice


def select_foods(today: dict) -> dict[str, dict]:
    menu_items = [item for item in today.get("menu_items", []) if item.get("food")]
    names = [item["food"]["name"].title() for item in menu_items]
    for index, name in enumerate(names, start=1):
        print(f"{index}: {name}")
    if not names:
        return {}
    raw = input("Select item numbers or names, separated with commas: ").strip()
    selected: dict[str, dict] = {}
    for value in (part.strip() for part in raw.split(",") if part.strip()):
        if value.isdigit() and 1 <= int(value) <= len(menu_items):
            item = menu_items[int(value) - 1]
        else:
            matches = [item for item in menu_items if item["food"]["name"].casefold() == value.casefold()]
            if not matches:
                suggestions = get_close_matches(value.title(), names, n=3, cutoff=0.5)
                suffix = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
                print(f"No menu item matched {value!r}.{suffix}")
                continue
            if len(matches) > 1:
                print(f"Multiple entries named {value!r}; using the first menu entry.")
            item = matches[0]
        selected[item["food"]["name"].title()] = item["food"]["rounded_nutrition_info"]
    return selected


# Intentionally mirrors Cronometer's stable custom-food field order.
api_to_page_label = {
    "calories": "Calories",
    "g_fat": "Total Fat: g",
    "g_saturated_fat": "Saturated Fat: g",
    "g_trans_fat": "Trans Fat: g",
    "mg_cholesterol": "Cholesterol: g",
    "g_carbs": "Total Carbohydrate: g",
    "g_added_sugar": "Added Sugars: g",
    "g_sugar": "Total Sugars: g",
    "mg_potassium": "Potassium: g",
    "mg_sodium": "Sodium: g",
    "g_fiber": "Dietary Fiber: g",
    "g_protein": "Protein: g",
    "mg_iron": "Iron: g",
    "mg_calcium": "Calcium: g",
    "mcg_vitamin_d": "Vitamin D: g",
}

page_order = [
    "Calories",
    "Total Fat: g",
    "Total Fat: dv",
    "Saturated Fat: g",
    "Saturated Fat: dv",
    "Trans Fat: g",
    "Cholesterol: g",
    "Cholesterol: dv",
    "Sodium: g",
    "Sodium: dv",
    "Total Carbohydrate: g",
    "Total Carbohydrate: dv",
    "Dietary Fiber: g",
    "Dietary Fiber: dv",
    "Total Sugars: g",
    "Added Sugars: g",
    "Added Sugars: dv",
    "Protein: g",
    "Vitamin D: g",
    "Vitamin D: dv",
    "Calcium: g",
    "Calcium: dv",
    "Iron: g",
    "Iron: dv",
    "Potassium: g",
    "Potassium: dv",
]


def number_nutrition(food_info: dict[str, dict]) -> dict[str, dict[int, str]]:
    all_numbered_food_info = {}
    for food_name, nutrition in food_info.items():
        numbered = {}
        for api_key, page_label in api_to_page_label.items():
            if api_key in nutrition and page_label in page_order:
                page_index = page_order.index(page_label)
                numbered[page_index] = str(nutrition[api_key])
        all_numbered_food_info[food_name] = numbered
    return all_numbered_food_info


def collect_foods(now: datetime | None = None) -> tuple[str, dict[str, dict[int, str]]]:
    now = now or datetime.now()
    hall = select_hall()
    meal = choose_meal(menu_slug(now.hour))
    date = now.strftime("%Y-%m-%d")
    data = fetch_menu(hall, meal, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
    today = get_today(data, date)
    if not today:
        print(f"No {meal} menu was found for {date}.")
        return hall, {}
    return hall, number_nutrition(select_foods(today))
