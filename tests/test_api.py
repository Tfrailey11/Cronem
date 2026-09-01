from unittest.mock import Mock

import pytest
import requests

from cronem.API import MenuAPIError, fetch_menu, get_today, select_hall


def test_select_hall_reprompts_invalid_input():
    answers = iter(["nope", "2"])
    messages = []
    assert select_hall(lambda _: next(answers), messages.append) == "fresh-greenes"
    assert any("Please enter" in message for message in messages)


def test_fetch_menu_uses_timeout_and_returns_json():
    response = Mock()
    response.json.return_value = {"days": []}
    session = Mock()
    session.get.return_value = response
    assert fetch_menu("garnet-station", "lunch", "2026", "09", "01", session=session) == {"days": []}
    session.get.assert_called_once_with(
        "https://sc.api.nutrislice.com/menu/api/weeks/school/garnet-station/menu-type/lunch/2026/09/01/?format=json",
        timeout=15.0,
    )
    response.raise_for_status.assert_called_once()


def test_fetch_menu_wraps_network_errors():
    session = Mock()
    session.get.side_effect = requests.Timeout("slow")
    with pytest.raises(MenuAPIError, match="Could not retrieve"):
        fetch_menu("garnet-station", "lunch", "2026", "09", "01", session=session)


def test_get_today_handles_empty_and_matching_days():
    assert get_today({}, "2026-09-01") is None
    expected = {"date": "2026-09-01"}
    assert get_today({"days": [expected]}, "2026-09-01") is expected
