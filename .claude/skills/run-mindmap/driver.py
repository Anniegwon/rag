#!/usr/bin/env python3
"""
Playwright driver for mindmap/index.html.
Usage:
  python3 driver.py                          # default flow, screenshots to /tmp/mindmap-screenshots/
  python3 driver.py --screenshot-dir DIR     # custom output dir
"""

import sys
import os
import argparse
from playwright.sync_api import sync_playwright

# Locate index.html by walking up from this script
_here = os.path.dirname(os.path.abspath(__file__))
_base = _here
HTML = None
for _ in range(8):
    candidate = os.path.join(_base, "index.html")
    if os.path.exists(candidate):
        HTML = f"file://{candidate}"
        break
    _base = os.path.dirname(_base)

if HTML is None:
    sys.exit("ERROR: could not find index.html — run from within the mindmap project")


def click_node(page, index=1):
    """Click the Nth node (1-based) to select it. Closes any open edit box first."""
    # Press Escape to close any open edit box before clicking
    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    page.locator("g.node").nth(index - 1).click()
    page.wait_for_timeout(200)


def add_named_node(page, text):
    """Click Add Node button and type name. App auto-opens edit mode after add."""
    page.click("#btn-add")
    page.wait_for_timeout(150)  # wait for 30ms setTimeout + render
    page.locator("#edit-fo input").wait_for(state="visible", timeout=3000)
    page.locator("#edit-fo input").fill(text)
    page.keyboard.press("Enter")
    page.wait_for_timeout(300)


def start_edit(page, index):
    """Double-click Nth node to enter edit mode."""
    # Close any open editor first
    page.keyboard.press("Escape")
    page.wait_for_timeout(100)
    page.locator("g.node").nth(index - 1).dblclick()
    page.wait_for_timeout(300)


def run(screenshot_dir="/tmp/mindmap-screenshots", headless=True):
    os.makedirs(screenshot_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(HTML)
        page.wait_for_timeout(800)

        page.screenshot(path=f"{screenshot_dir}/01-initial.png")
        print(f"[01] initial state → {screenshot_dir}/01-initial.png")

        # Select root node (index=1), then add child "역사"
        click_node(page, 1)
        add_named_node(page, "역사")
        page.screenshot(path=f"{screenshot_dir}/02-added-역사.png")
        print(f"[02] added 역사 → {screenshot_dir}/02-added-역사.png")

        # Select 역사 (index=2) and add child "조선시대"
        click_node(page, 2)
        add_named_node(page, "조선시대")
        page.screenshot(path=f"{screenshot_dir}/03-added-조선시대.png")
        print(f"[03] added 조선시대 → {screenshot_dir}/03-added-조선시대.png")

        # Select 역사 (index=2) and add child "고려시대"
        click_node(page, 2)
        add_named_node(page, "고려시대")
        page.screenshot(path=f"{screenshot_dir}/04-added-고려시대.png")
        print(f"[04] added 고려시대 → {screenshot_dir}/04-added-고려시대.png")

        # Open quiz scope selector
        page.click("#btn-quiz")
        page.wait_for_timeout(600)
        page.screenshot(path=f"{screenshot_dir}/05-quiz-scope.png")
        print(f"[05] quiz scope screen → {screenshot_dir}/05-quiz-scope.png")

        # Start quiz (all nodes selected by default)
        page.click("#btn-scope-start")
        page.wait_for_timeout(600)
        page.screenshot(path=f"{screenshot_dir}/06-quiz-question.png")
        print(f"[06] quiz question → {screenshot_dir}/06-quiz-question.png")

        # Answer first option
        options = page.locator("#quiz-options button").all()
        if options:
            options[0].click()
            page.wait_for_timeout(500)
        page.screenshot(path=f"{screenshot_dir}/07-answered.png")
        print(f"[07] answered → {screenshot_dir}/07-answered.png")

        # Cycle through remaining questions: next → answer → repeat until result
        for i in range(10):
            next_btn = page.locator("#quiz-next")
            if not next_btn.is_visible():
                break
            next_btn.click()
            page.wait_for_timeout(400)
            # If options are hidden we've moved to the result screen
            if not page.locator("#quiz-options").is_visible():
                break
            opts = page.locator("#quiz-options button:not([disabled])").all()
            if not opts:
                break
            opts[0].click()
            page.wait_for_timeout(400)

        page.screenshot(path=f"{screenshot_dir}/08-result.png")
        print(f"[08] result screen → {screenshot_dir}/08-result.png")

        browser.close()

    count = len(os.listdir(screenshot_dir))
    print(f"\nDone. {count} screenshots in: {screenshot_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshot-dir", default="/tmp/mindmap-screenshots")
    parser.add_argument("--no-headless", action="store_true")
    args = parser.parse_args()
    run(screenshot_dir=args.screenshot_dir, headless=not args.no_headless)
