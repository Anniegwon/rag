# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project structure

Single-file web app — the entire application lives in `index.html` (HTML + inline CSS + inline JS, ~1100 lines). No build step, no dependencies, no server required.

```
mindmap/
  index.html                          ← entire app
  .claude/skills/run-mindmap/
    SKILL.md                          ← how to drive the app headlessly
    driver.py                         ← Playwright automation script
```

## Running and testing

Open directly in a browser — no server needed:
```bash
open index.html
```

For headless automation and screenshots (requires `pip3 install playwright && python3 -m playwright install chromium`):
```bash
python3 .claude/skills/run-mindmap/driver.py
python3 .claude/skills/run-mindmap/driver.py --screenshot-dir /tmp/my-shots
```

After making UI changes, run the driver and inspect the screenshots to verify nothing broke visually.

## Architecture

The app uses an SVG canvas inside a `<g id="canvas">` element with a `translate/scale` transform for pan/zoom. All nodes and edges are SVG elements rendered into two sublayers: `<g id="edges-layer">` and `<g id="nodes-layer">`.

**State (all module-level `let` variables):**
- `nodes` — `[{id, parentId, x, y, text}]` — the only persistent data structure
- `selectedIds` — `Set` of selected node IDs
- `collapsedIds` — `Set` of node IDs whose children are hidden
- `panX`, `panY`, `scale` — viewport transform
- `quizScope` — `Set` of L1 node IDs selected for quiz; empty = all included
- `quizWrong` — `[{parentText, chosen, answer, options, ancestorPath}]` — wrong answers for current session

**Key rendering functions:**
- `render()` — calls `renderEdges()` + `renderNodes()` + `updateToolbar()` + `saveToStorage()`
- `renderNodes()` skips nodes where `isVisible(id)` is false (collapsed subtree); appends a `−/+` collapse toggle button for nodes with children
- `moveNodeInPlace(id, x, y)` — updates SVG attributes directly without a full re-render; used during drag to avoid destroying DOM elements mid-drag (which would break browser click tracking)
- `applyTransform()` — writes `translate(panX,panY) scale(scale)` to the canvas group

**Coordinate system:** `getCanvasPoint(e)` converts screen coordinates to canvas-space using `canvas.getScreenCTM().inverse()`.

**Quiz flow:**
1. `openScopeScreen()` — builds L1 checkbox list; initialises `quizScope` with all L1 IDs that have at least one quiz-eligible descendant
2. `generateQuestions()` — finds `(parent, leafChild)` pairs where the parent's ancestor chain intersects `quizScope`; distractors are sibling leaf nodes of the correct answer, with fallback to map-wide leaves
3. `showQuestion()` — renders options and starts the 8-second `startTimer()`
4. `selectAnswer(chosen)` — `null` means timeout; stops timer, marks wrong/correct, shows `#quiz-next`
5. Result screen shows "오답만 재시험" button if `quizWrong.length > 0`; `startRetryWrong()` rebuilds `quizQuestions` from the stored wrong entries

**Persistence:** `saveToStorage()` / `loadFromStorage()` serialise `{nodes, nextId, panX, panY, scale, collapsed}` to `localStorage` key `mindmap-data`. Quiz history goes to `mindmap-quiz-history`.

**Colors:** Root node uses `ROOT_COLOR`. All other nodes inherit color from their L1 ancestor via `getRootChildIndex()` cycling through the `COLORS` array.

## Important constraints

- **No re-render during drag.** `mousemove` calls `moveNodeInPlace()` only; `render()` is called once on `mouseup`. Calling `render()` mid-drag destroys the dragged DOM element and breaks the browser's click detection.
- **`#btn-add` is disabled** until exactly one node is selected. After clicking it, the app immediately opens an inline `<foreignObject><input>` editor (30ms timeout) — type into that, don't try to dblclick the new node.
- **Quiz leaf detection** is recomputed fresh each time from `nodes` — a node is a leaf if no other node has it as `parentId`.
- **`quizScope` stores L1 IDs** (children of root), not eligible-parent IDs. `generateQuestions` uses an ancestor-walk (`isInScope`) to include any eligible node whose L1 ancestor is in scope.
