"""Credential loading and Cronometer login automation."""

from __future__ import annotations

import json
import os
from pathlib import Path

import keyring
from dotenv import load_dotenv

APP_DIR = Path.home() / ".cronem"
ENV_PATH = APP_DIR / ".env"
KEYRING_SERVICE = "cronem"


def load_credentials() -> tuple[str, str]:
    load_dotenv(ENV_PATH)
    username = os.getenv("CRONOMETER_USERNAME", "").strip()
    password = keyring.get_password(KEYRING_SERVICE, username) if username else None
    password = password or os.getenv("CRONOMETER_PASSWORD")  # Migration fallback.
    if not username or not password:
        raise RuntimeError("Cronometer credentials are missing. Run 'Cronem login' first.")
    return username, password


def build_login_steps() -> str:
    username, password = load_credentials()
    return f"""
        await page.goto('https://cronometer.com/login/');
        await page.waitForLoadState('domcontentloaded');
        if (await page.locator('#username').isVisible()) {{
            await page.fill('#username', {json.dumps(username)});
            await page.fill('#password', {json.dumps(password)});
            await page.click('#login-button');
        }}
        await page.goto('https://cronometer.com/#custom-foods');
        await page.locator('text=CREATE FOOD').waitFor({{ state: 'visible', timeout: 15000 }});
    """
