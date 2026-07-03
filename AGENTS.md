# Repository Guidelines

## Project Structure & Module Organization
This repository is a static study hub/PWA for G検定 learning. Core UI files live at the repository root:

- `index.html` defines the tabbed app shell.
- `css/style.css` contains the mobile-first styling, dark mode, and bottom tab bar.
- `js/app.js` handles screen routing, Markdown loading, localStorage records, and flashcard SRS.
- `content/plan.md` is the study plan displayed in the Plan tab.
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
