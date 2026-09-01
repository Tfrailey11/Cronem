from pathlib import Path
from unittest.mock import Mock, patch

from cronem import Kernel


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
        patch.object(Kernel, "collect_foods", return_value=("garnet-station", {"Soup": {0: "50"}})),
        patch.object(Kernel, "build_login_steps", return_value=""),
        patch.object(Kernel, "Kernel", return_value=kernel),
        patch.object(Kernel, "load_dotenv"),
        patch.object(Kernel.os, "getenv", return_value="key"),
    ):
        assert Kernel.run_add(assume_yes=True) == 1
        assert not Kernel.STATE_PATH.exists()
