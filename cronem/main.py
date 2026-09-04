"""Menu selection and nutrition transformation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
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


@dataclass
class SelectedFood:
    """Nutrition and serving information for one selected menu food."""

    nutrition: dict[str, float]
    serving_amount: Decimal
    serving_unit: str
    source_serving_amount: Decimal
    source_serving_unit: str

    @property
    def serving_label(self) -> str:
        return f"{self.serving_amount:g} {self.serving_unit}"


def _serving(food: dict) -> tuple[Decimal, str]:
    info = food.get("serving_size_info") or {}
    raw_amount = info.get("serving_size_amount", 1)
    unit = str(info.get("serving_size_unit") or "serving").strip()
    try:
        amount = Decimal(str(raw_amount))
    except InvalidOperation:
        amount = Decimal(1)
    if amount <= 0:
        amount = Decimal(1)
    return amount, unit


def select_foods(today: dict) -> dict[str, SelectedFood]:
    menu_items = [item for item in today.get("menu_items", []) if item.get("food")]
    names = [item["food"]["name"].title() for item in menu_items]
    for index, (name, item) in enumerate(zip(names, menu_items, strict=True), start=1):
        amount, unit = _serving(item["food"])
        calories = item["food"].get("rounded_nutrition_info", {}).get("calories", "unknown")
        print(f"{index}: {name} — serving: {amount:g} {unit}; calories: {calories}")
    if not names:
        return {}
    raw = input("Select item numbers or names, separated with commas: ").strip()
    selected: dict[str, SelectedFood] = {}
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
        food = item["food"]
        amount, unit = _serving(food)
        selected[food["name"].title()] = SelectedFood(
            nutrition=food.get("rounded_nutrition_info", {}),
            serving_amount=amount,
            serving_unit=unit,
            source_serving_amount=amount,
            source_serving_unit=unit,
        )
    return selected


UNIT_GROUPS = {
    "weight": {"mg": Decimal("0.001"), "g": Decimal(1), "oz": Decimal("28.349523125"), "lb": Decimal("453.59237")},
    "volume": {"tsp": Decimal(1), "tbsp": Decimal(3), "fl oz": Decimal(6), "cup": Decimal(48), "pint": Decimal(96), "quart": Decimal(192)},
}
UNIT_ALIASES = {
    "milligram": "mg", "milligrams": "mg", "gram": "g", "grams": "g", "ounce": "oz", "ounces": "oz",
    "lbs": "lb", "pound": "lb", "pounds": "lb", "fluid ounce": "fl oz", "fluid ounces": "fl oz",
    "teaspoon": "tsp", "teaspoons": "tsp", "tablespoon": "tbsp", "tablespoons": "tbsp", "cups": "cup",
    "pints": "pint", "quarts": "quart",
}


def _canonical_unit(unit: str) -> str:
    normalized = " ".join(unit.strip().casefold().split())
    return UNIT_ALIASES.get(normalized, normalized)


def serving_scale(old_amount: Decimal, old_unit: str, new_amount: Decimal, new_unit: str) -> Decimal:
    """Return the nutrient multiplier between compatible serving sizes."""
    if new_amount <= 0:
        raise ValueError("serving amount must be greater than zero")
    old = _canonical_unit(old_unit)
    new = _canonical_unit(new_unit)
    if old == new:
        return new_amount / old_amount
    for conversions in UNIT_GROUPS.values():
        if old in conversions and new in conversions:
            return (new_amount * conversions[new]) / (old_amount * conversions[old])
    raise ValueError(f"cannot convert {old_unit!r} to {new_unit!r}")


def review_servings(foods: dict[str, SelectedFood]) -> dict[str, SelectedFood]:
    """Interactively show and optionally replace each source serving size."""
    print("\nServing-size review (nutrition is scaled when you change a serving):")
    for name, food in foods.items():
        calories = food.nutrition.get("calories", "unknown")
        print(f"{name}: Nutrislice serving {food.serving_label}, {calories} calories")
        while True:
            replacement = input("  New serving (for example '2 oz', or Enter to keep): ").strip()
            if not replacement:
                break
            amount_text, separator, unit = replacement.partition(" ")
            try:
                new_amount = Decimal(amount_text)
                if not separator or not unit.strip():
                    raise ValueError("include both an amount and unit")
                scale = serving_scale(food.source_serving_amount, food.source_serving_unit, new_amount, unit)
            except (InvalidOperation, ValueError) as exc:
                print(f"  Invalid serving: {exc}.")
                continue
            food.nutrition = {
                key: float(Decimal(str(value)) * scale) if value is not None else value
                for key, value in food.nutrition.items()
            }
            food.serving_amount = new_amount
            food.serving_unit = unit.strip()
            print(f"  Adjusted to {food.serving_label}; {food.nutrition.get('calories', 'unknown'):g} calories.")
            break
    return foods


# Intentionally mirrors Cronometer's stable custom-food field order.
api_to_page_label = {
    "calories": "Calories",
    "g_fat": "Total Fat: g",
    "g_saturated_fat": "Saturated Fat: g",
    "g_trans_fat": "Trans Fat: g",
    "mg_cholesterol": "Cholesterol: mg",
    "g_carbs": "Total Carbohydrate: g",
    "g_added_sugar": "Added Sugars: g",
    "g_sugar": "Total Sugars: g",
    "mg_potassium": "Potassium: mg",
    "mg_sodium": "Sodium: mg",
    "g_fiber": "Dietary Fiber: g",
    "g_protein": "Protein: g",
    "mg_iron": "Iron: mg",
    "mg_calcium": "Calcium: mg",
    "mcg_vitamin_d": "Vitamin D: mcg",
}

page_order = [
    "Calories",
    "Total Fat: g",
    "Total Fat: dv",
    "Saturated Fat: g",
    "Saturated Fat: dv",
    "Trans Fat: g",
    "Cholesterol: mg",
    "Cholesterol: dv",
    "Sodium: mg",
    "Sodium: dv",
    "Total Carbohydrate: g",
    "Total Carbohydrate: dv",
    "Dietary Fiber: g",
    "Dietary Fiber: dv",
    "Total Sugars: g",
    "Added Sugars: g",
    "Added Sugars: dv",
    "Protein: g",
    "Vitamin D: mcg",
    "Vitamin D: dv",
    "Calcium: mg",
    "Calcium: dv",
    "Iron: mg",
    "Iron: dv",
    "Potassium: mg",
    "Potassium: dv",
]


def number_nutrition(food_info: dict[str, SelectedFood]) -> dict[str, dict]:
    all_numbered_food_info = {}
    for food_name, food in food_info.items():
        numbered = {}
        for api_key, page_label in api_to_page_label.items():
            if api_key in food.nutrition and food.nutrition[api_key] is not None and page_label in page_order:
                page_index = page_order.index(page_label)
                numbered[page_index] = f"{food.nutrition[api_key]:g}"
        all_numbered_food_info[food_name] = {"nutrition": numbered, "serving": food.serving_label}
    return all_numbered_food_info


def collect_foods(now: datetime | None = None, *, review_serving_sizes: bool = False) -> tuple[str, dict[str, dict]]:
    now = now or datetime.now()
    hall = select_hall()
    meal = choose_meal(menu_slug(now.hour))
    date = now.strftime("%Y-%m-%d")
    data = fetch_menu(hall, meal, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
    today = get_today(data, date)
    if not today:
        print(f"No {meal} menu was found for {date}.")
        return hall, {}
    selected = select_foods(today)
    if review_serving_sizes:
        selected = review_servings(selected)
    return hall, number_nutrition(selected)
