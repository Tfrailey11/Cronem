from pathlib import Path
from unittest.mock import Mock, patch

from cronem import Kernel


def test_each_food_run_returns_to_foods_list_and_types_name():
    steps = Kernel._food_steps("Dining Hall Soup (1 cup)", {0: "50"}, False)

    assert "page.goto" not in steps
    assert "await nameInput.click();" in steps
    assert "await nameInput.fill('');" in steps
    assert "await nameInput.pressSequentially(foodName, { delay: 50 });" in steps
    assert steps.index("BACK TO FOODS LIST") < steps.rindex("CREATE FOOD")


def test_failed_browser_run_does_not_update_state(tmp_path):
    response = type("Response", (), {"error": "failed", "stderr": "", "result": None})()
    browser = type("Browser", (), {"session_id": "session"})()
    kernel = type("Client", (), {})()
    kernel.browsers = type("Browsers", (), {})()
    kernel.browsers.create = lambda: browser
    kernel.browsers.delete_by_id = lambda _id: None
    kernel.browsers.playwright = Mock()
    kernel.browsers.playwright.execute.return_value = response

    with (
        patch.object(Kernel, "STATE_PATH", Path(tmp_path) / "names.txt"),
        patch.object(
            Kernel,
            "collect_foods",
            return_value=("garnet-station", {"Soup": {"nutrition": {0: "50"}, "serving": "1 cup"}}),
        ),
        patch.object(Kernel, "build_login_steps", return_value="login steps"),
        patch.object(Kernel, "login", side_effect=RuntimeError("Cronometer login failed: failed")),
        patch.object(Kernel, "Kernel", return_value=kernel),
        patch.object(Kernel, "load_dotenv"),
        patch.object(Kernel.os, "getenv", return_value="key"),
    ):
        assert Kernel.run_add(assume_yes=True) == 1
        assert not Kernel.STATE_PATH.exists()


def test_batch_reuses_one_browser_session(tmp_path):
    ok = type("Response", (), {"error": None, "stderr": "", "result": None})()
    browser = type("Browser", (), {"session_id": "session"})()
    kernel = type("Client", (), {})()
    kernel.browsers = type("Browsers", (), {})()
    kernel.browsers.create = Mock(return_value=browser)
    kernel.browsers.delete_by_id = Mock()
    kernel.browsers.playwright = Mock()
    kernel.browsers.playwright.execute.return_value = ok
    foods = {
        "Soup": {"nutrition": {0: "50"}, "serving": "1 cup"},
        "Bread": {"nutrition": {0: "100"}, "serving": "1 slice"},
    }

    with (
        patch.object(Kernel, "STATE_PATH", Path(tmp_path) / "names.txt"),
        patch.object(Kernel, "collect_foods", return_value=("garnet-station", foods)),
        patch.object(Kernel, "build_login_steps", return_value="login steps") as build_login_steps,
        patch.object(Kernel, "login") as login,
        patch.object(Kernel, "Kernel", return_value=kernel),
        patch.object(Kernel, "load_dotenv"),
        patch.object(Kernel.os, "getenv", return_value="key"),
    ):
        assert Kernel.run_add(assume_yes=True) == 0

    kernel.browsers.create.assert_called_once_with()
    build_login_steps.assert_called_once_with()
    login.assert_called_once_with(kernel.browsers.playwright, "session", "login steps")
    assert kernel.browsers.playwright.execute.call_count == 2
    kernel.browsers.delete_by_id.assert_called_once_with("session")
