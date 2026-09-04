from decimal import Decimal
from unittest.mock import patch

import pytest

from cronem.main import SelectedFood, menu_slug, number_nutrition, review_servings, select_foods, serving_scale


@pytest.mark.parametrize(
    ("hour", "meal"),
    [
        (0, "dinner"),
        (5, "dinner"),
        (6, "breakfast"),
        (11, "breakfast"),
        (12, "lunch"),
        (17, "lunch"),
        (18, "dinner"),
        (23, "dinner"),
    ],
)
def test_menu_boundaries(hour, meal):
    assert menu_slug(hour) == meal


def test_menu_slug_rejects_invalid_hour():
    with pytest.raises(ValueError):
        menu_slug(24)


def test_number_nutrition_preserves_cronometer_positions():
    food = SelectedFood({"calories": 50, "g_protein": 3}, Decimal(1), "cup", Decimal(1), "cup")
    result = number_nutrition({"Soup": food})
    assert result == {"Soup": {"nutrition": {0: "50", 17: "3"}, "serving": "1 cup"}}


def test_select_foods_accepts_numbers_and_reports_misspellings(capsys):
    day = {"menu_items": [{"food": {"name": "Tomato Soup", "rounded_nutrition_info": {"calories": 50}}}]}
    with patch("builtins.input", return_value="1, Tomato Soop"):
        selected = select_foods(day)
    assert selected["Tomato Soup"].nutrition == {"calories": 50}
    assert selected["Tomato Soup"].serving_label == "1 serving"
    assert "Did you mean" in capsys.readouterr().out


def test_serving_scale_converts_ounces_to_pounds():
    assert serving_scale(Decimal(1), "lbs", Decimal(2), "oz") == Decimal("0.125")


def test_serving_scale_rejects_incompatible_units():
    with pytest.raises(ValueError, match="cannot convert"):
        serving_scale(Decimal(1), "quart", Decimal(2), "oz")


def test_review_servings_scales_all_nutrients(capsys):
    food = SelectedFood(
        {"calories": 1600, "g_protein": 80}, Decimal(1), "lbs", Decimal(1), "lbs"
    )
    with patch("builtins.input", return_value="2 oz"):
        reviewed = review_servings({"Pepperoni": food})
    assert reviewed["Pepperoni"].nutrition == {"calories": 200.0, "g_protein": 10.0}
    assert reviewed["Pepperoni"].serving_label == "2 oz"
    assert "Nutrislice serving 1 lbs" in capsys.readouterr().out
