"""Kernel browser automation for creating and logging custom foods."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from kernel import Kernel

from .Login import ENV_PATH, build_login_steps
from .main import collect_foods

STATE_PATH = Path.home() / ".cronem" / "stored_names.txt"


def _stored_names() -> set[str]:
    if not STATE_PATH.exists():
        return set()
    return {line.strip() for line in STATE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()}


def _remember_name(name: str) -> None:
    STATE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if name not in _stored_names():
        with STATE_PATH.open("a", encoding="utf-8") as file:
            file.write(f"{name}\n")


def _food_steps(food_name: str, food_values: dict[int, str], cache_hint: bool) -> str:
    return f"""
        const foodName = {json.dumps(food_name)};
        const searchInput = page.locator('input[placeholder="Search your foods..."]');
        await searchInput.fill(foodName);
        const result = page.locator('div[role="button"]', {{ hasText: foodName }}).first();
        let exists = false;
        try {{
            await result.waitFor({{ state: 'visible', timeout: {4000 if cache_hint else 2000} }});
            exists = true;
        }} catch (_) {{ exists = false; }}
        if (exists) {{
            await result.click();
        }} else {{
            await page.locator('text=CREATE FOOD').click();
            const xpath = 'xpath=//div[contains(@class,"gwt-Label") and text()="Food Name"]' +
                '/following-sibling::div[1]//input';
            await page.locator(xpath).fill(foodName);
            const boxes = page.locator('.GHL1WBHBGJ.admin-edit-box');
            const values = {json.dumps(food_values)};
            for (const [i, val] of Object.entries(values)) {{
                const input = boxes.nth(Number(i));
                await input.locator('xpath=preceding-sibling::div[1]').click();
                await input.fill(val);
                await page.keyboard.press('Tab');
            }}
            await page.locator('text=SAVE CHANGES').click();
        }}
        const addToDiary = page.locator('button:has-text("ADD TO DIARY")');
        await addToDiary.first().waitFor({{ state: 'visible', timeout: 15000 }});
        await addToDiary.first().click();
        await addToDiary.last().waitFor({{ state: 'visible', timeout: 10000 }});
        await addToDiary.last().click();
    """


def run_add(
    *, dry_run: bool = False, assume_yes: bool = False, verbose: bool = False, review_serving_sizes: bool = False
) -> int:
    hall, values = collect_foods(review_serving_sizes=review_serving_sizes)
    if not values:
        print("No foods selected; nothing was changed.")
        return 0
    print(f"\n{hall.replace('-', ' ').title()}:")
    for food, details in values.items():
        print(f"  {food} — {details['serving']}")
    if dry_run:
        print(json.dumps(values, indent=2))
        return 0
    if not assume_yes and input("Add these foods to Cronometer? [y/N]: ").strip().lower() not in {"y", "yes"}:
        print("Cancelled.")
        return 0
    load_dotenv(ENV_PATH)
    api_key = os.getenv("KERNEL_API_KEY")
    if not api_key:
        raise RuntimeError("Kernel API key is missing. Run 'Cronem login' first.")
    kernel = Kernel(api_key=api_key, max_retries=1, timeout=120.0)
    known_names = _stored_names()
    failures = 0
    browser = kernel.browsers.create()
    try:
        login_response = kernel.browsers.playwright.execute(id=browser.session_id, code=build_login_steps())
        if login_response.error:
            raise RuntimeError(f"Cronometer login failed: {login_response.error}")
        for food, details in values.items():
            # Cronometer's custom-food editor defaults to one serving. Keep the
            # reviewed quantity in the name so that "one serving" remains clear.
            full_name = f"{hall.replace('-', ' ').title()} {food} ({details['serving']})"
            print(f"Adding {full_name}...")
            response = None
            try:
                response = kernel.browsers.playwright.execute(
                    id=browser.session_id,
                    code=_food_steps(full_name, details["nutrition"], full_name in known_names),
                )
                if response.error:
                    raise RuntimeError(str(response.error))
                _remember_name(full_name)
                print(f"Added {full_name}.")
                if verbose:
                    print(response.result)
            except Exception as exc:  # noqa: BLE001 - isolate failures so remaining foods can continue.
                failures += 1
                print(f"Could not add {full_name}: {exc}")
                if verbose and response and response.stderr:
                    print(response.stderr)
    except Exception as exc:  # noqa: BLE001 - provide a useful CLI failure for session/login errors.
        failures = len(values)
        print(f"Could not start Cronometer import: {exc}")
    finally:
        kernel.browsers.delete_by_id(browser.session_id)
    return 1 if failures else 0
