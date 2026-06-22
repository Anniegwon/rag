---
name: run-mindmap
description: Run, screenshot, and interact with the mindmap web app. Use this to launch the app, take screenshots, add nodes, run a quiz, or verify UI changes.
---

A single-file SVG mind map web app at `index.html`. Driven headlessly via Python Playwright — no dev server needed (loaded as a `file://` URL).

## Prerequisites

```bash
pip3 install playwright
python3 -m playwright install chromium
```

Both commands were verified on macOS (Darwin 21.6.0) with Python 3.

## Run (agent path)

```bash
cd /Users/annie/mindmap
python3 .claude/skills/run-mindmap/driver.py
```

Screenshots land in `/tmp/mindmap-screenshots/` by default:

| File | What it shows |
|---|---|
| `01-initial.png` | App on load — root node "중심 주제" in center |
| `02-add-node.png` | After clicking Add Node |
| `03-renamed.png` | After double-click renaming node to "역사" |
| `04-child-node.png` | After adding and naming a child "조선시대" |
| `05-quiz-scope.png` | Quiz scope selection modal |
| `06-quiz-question.png` | Active quiz question |
| `07-answered.png` | After selecting an answer option |

Override screenshot dir:
```bash
python3 .claude/skills/run-mindmap/driver.py --screenshot-dir /tmp/my-screenshots
```

## Run (human path)

Open `index.html` directly in any browser:
```bash
open /Users/annie/mindmap/index.html   # macOS
```

This is the normal interactive mode. The driver is useless for this.

## Key interactions in the driver

The driver uses standard Playwright selectors:

```python
page.click("#btn-add")                    # add child to selected node (node must be selected first)
# after btn-add, app auto-opens edit mode → type directly into the input:
page.locator("#edit-fo input").fill("text"); page.keyboard.press("Enter")
page.click("#btn-quiz")                   # open quiz scope screen
page.click("#btn-scope-start")            # start quiz after scope selection
page.locator("#quiz-next").click()        # advance to next question (appears after answering)
```

Node rects have class `node-rect`; select by XPath index to target specific nodes.

## Gotchas

- **`file://` URL, no server**: The app uses `localStorage` for save/load — this works fine with `file://` in Chromium headless.
- **Node XPath indices**: Nodes are rendered in DOM order (root first, then children). After adding nodes, re-query `page.query_selector_all(".node-rect")` — the index shifts if you add multiple nodes.
- **Quiz requires leaf nodes**: The quiz only generates questions for leaf nodes (nodes with no children). If no leaf exists in the selected scope, the quiz scope screen shows no options. Add at least one grandchild node before running quiz flow.
- **Auto-edit mode after add**: Clicking `#btn-add` immediately opens inline edit mode (30ms setTimeout). Do NOT try to dblclick the new node — instead wait for `#edit-fo input` and `.fill()` / `Enter` directly.
- **Quiz "다음 →" required**: After answering a question, options become disabled. Click `#quiz-next` to advance. When the last question is answered, `#quiz-next` shows "결과 보기" — click it to reach the result screen.
- **`chromium-cli` not available**: This project uses `playwright` (Python) instead of `chromium-cli` — install via the prerequisites above.

## Troubleshooting

**`ModuleNotFoundError: No module named 'playwright'`**
→ `pip3 install playwright`

**`Error: Executable doesn't exist at ...`**
→ `python3 -m playwright install chromium`

**Screenshot is blank / gray**
→ Increase `page.wait_for_timeout(ms)` after `page.goto()` — the SVG renders after a short JS tick.
