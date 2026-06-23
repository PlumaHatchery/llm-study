# G検定 学習ハブ

自分専用の学習サイト。**計画・記録・コンテンツを「置いて表示」する**だけのシンプルな静的サイトです。
GitHub Pages で動き、スマホのホーム画面に追加すればアプリのように使えます（PWA・オフライン対応）。

> 方針：計画 v3 の「G検定アプリは作らない／Claudeクイズで代替」に沿って、本サイトは
> **学習の置き場**に徹しています。問題演習は引き続きチャットの **Claudeクイズ**で。

## 4つのタブ
- **🏠 ホーム** — 今日の日付・本番までの残り日数・**今日の予定（計画から自動抽出）**・連続記録日数・Claudeクイズの定型文
- **🗓 計画** — `content/plan.md`（計画 v3）を表示。今日の日付の見出しを強調
- **✍️ 記録** — ボタンで今日の記録（🏁到達度 / 📝の答え / クイズ正答 _/10）。連続日数と履歴。**log.md形式でコピー**も可
- **📚 コンテンツ** — Markdownノート（チートシート等）＋ 暗記カード（人名・略語の丸暗記、補助）

進捗・記録は**ブラウザ内（localStorage）に保存**。サーバー不要・あなたの端末に残ります。

## 中身を足す・直す

### 計画を更新する
`content/plan.md` を編集するだけ。`## 6/24(水)|…` の形式で日付見出しを書くと、その日の「今日の予定」に自動で出ます。

### ノートを追加する
1. `content/notes/xxx.md` を作る
2. `content/manifest.json` の `notes` に追加：
   ```json
   { "id": "xxx", "title": "タイトル", "file": "notes/xxx.md", "desc": "説明" }
   ```

### 暗記カードを追加する
`data/decks/abbr.json` の `cards` に追加。新デッキは `data/manifest.json` にパスを足す。
```json
{ "id": "一意のID", "front": "表（用語）", "back": "裏（説明）" }
```

### 記録（log）について
- サイトの「記録」タブでボタン入力 → localStorage に保存（端末ごと）
- **log.md形式でコピー**ボタンで、計画の3行フォーマットを取得 → リポジトリの `log.md` に貼れば、ファイルにも記録が残ります（端末をまたいで残したい場合に便利）

## ローカルで確認する
`file://` だと読み込めないので簡易サーバーを立てます：
```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## GitHub Pages へ公開する手順
1. GitHub で新規リポジトリを作成（計画では `llm-study` / Public）
2. push：
   ```bash
   git add -A
   git commit -m "学習ハブ 初版"
   git branch -M main
   git remote add origin https://github.com/<ユーザー名>/llm-study.git
   git push -u origin main
   ```
3. **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `(root)`** → Save
4. 数十秒〜数分で `https://<ユーザー名>.github.io/llm-study/` に公開
5. スマホでURLを開き「ホーム画面に追加」でアプリ化

## ファイル構成
```
index.html              4タブのUI（ホーム/計画/記録/コンテンツ）
css/style.css           スタイル（モバイル優先・ダークモード・下部タブバー）
js/app.js               画面制御・計画抽出・記録(localStorage)・暗記カードSRS
js/marked.min.js        Markdownレンダラ（同梱・オフライン動作のため）
content/plan.md         学習計画 v3
content/manifest.json   ノート一覧
content/notes/*.md      ノート（チートシート等）
data/manifest.json      暗記カードのデッキ一覧
data/decks/*.json       暗記カード
manifest.webmanifest    PWA設定
sw.js                   Service Worker（オフライン対応）
icons/                  アプリアイコン
```
