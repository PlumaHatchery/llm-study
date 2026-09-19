# Repository Guidelines

## Project Structure & Module Organization
This repository is a static study hub/PWA for G検定 learning. Core UI files live at the repository root:

- `index.html` defines the tabbed app shell.
- `css/style.css` contains the mobile-first styling, dark mode, and bottom tab bar.
- `js/app.js` handles screen routing, Markdown loading, localStorage records, and flashcard SRS.
- `content/plan.md` is the study plan displayed in the Plan tab. It is a **step queue, not a calendar**: each task is a `## S01|40分|タイトル` heading, and the app advances to the next step only when the user marks one done or skipped (progress in `localStorage` under `mystudy.steps.v1`). Never reintroduce date-keyed headings — a passed date must not move a task anywhere. Optional lines inside a step: `⏰ **期限**: 8/28` (surfaces a deadline banner), `📝 **問い**:`, `📚 参照:` (note titles in 「」, deck ids in backticks). Step titles follow `分類: 範囲` (e.g. `G検定インプット 1/10: AIの歴史`) — `quizScope()` in `js/app.js` takes the text after the first `:` as the quiz subject, so keep the colon and put the study subject on its right. A `🔵` in the title marks the step as skippable.
- `content/manifest.json` lists Markdown notes in `content/notes/*.md`.
- `data/manifest.json` lists flashcard decks in `data/decks/*.json`.
- `manifest.webmanifest`, `sw.js`, and `icons/` provide PWA/offline support.

## Build, Test, and Development Commands
There is no package manager or build step. Run the site through a local HTTP server because `file://` cannot load fetched Markdown/JSON:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000` and verify all tabs, note loading, flashcards, and offline behavior after relevant changes.

## Coding Style & Naming Conventions
Use plain HTML, CSS, and vanilla JavaScript. Keep JavaScript in strict mode and follow the existing style in `js/app.js`: two-space indentation, small helper functions, `const`/`let`, and descriptive camelCase names. Keep content IDs stable and URL-safe, for example `ml-methods` or `english-reading`. JSON deck cards should use unique `id`, `front`, and `back` fields.

## Testing Guidelines
No automated tests are configured. Validate changes manually in a browser. For content changes, confirm the relevant manifest entry points to an existing file and that Markdown renders correctly. For deck changes, confirm valid JSON and test at least one flashcard study session. For PWA changes, reload the service worker and verify cached assets still work.

## Commit & Pull Request Guidelines
Recent commits use concise Japanese summaries that state the user-facing change, for example `ノートに図（Mermaid）を追加してビジュアライズ`. Keep commits focused and descriptive. Pull requests should include a short summary, affected files or content areas, manual verification steps, and screenshots for visible UI changes.

## Security & Configuration Tips
Do not commit personal study records exported from localStorage unless intentionally adding a shared `log.md`. Avoid external CDN dependencies; this app is designed to work offline with bundled assets such as `js/marked.min.js` and `js/mermaid.min.js`.
