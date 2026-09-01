from unittest.mock import patch

import pytest

from cronem.main import menu_slug, number_nutrition, select_foods


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
    result = number_nutrition({"Soup": {"calories": 50, "g_protein": 3}})
    assert result == {"Soup": {0: "50", 17: "3"}}


def test_select_foods_accepts_numbers_and_reports_misspellings(capsys):
    day = {"menu_items": [{"food": {"name": "Tomato Soup", "rounded_nutrition_info": {"calories": 50}}}]}
    with patch("builtins.input", return_value="1, Tomato Soop"):
        selected = select_foods(day)
    assert selected == {"Tomato Soup": {"calories": 50}}
    assert "Did you mean" in capsys.readouterr().out
