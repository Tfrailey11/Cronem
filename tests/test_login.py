from unittest.mock import Mock, patch

from cronem.Login import build_login_steps, login


def test_login_waits_for_authentication_before_opening_custom_foods():
    with patch("cronem.Login.load_credentials", return_value=("user@example.com", "secret")):
        steps = build_login_steps()

    assert steps.index("waitForURL") < steps.index("#custom-foods")
    assert "!url.pathname.startsWith('/login')" in steps


def test_login_executes_login_steps_for_session():
    playwright = Mock()
    playwright.execute.return_value = type("Response", (), {"error": None})()

    login(playwright, "session", "login steps")

    playwright.execute.assert_called_once_with(id="session", code="login steps")
