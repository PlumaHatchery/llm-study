'use strict';

/* ================================================================== *
 * G検定 学習ハブ
 *  - 計画 / 記録 / コンテンツ を「置いて表示」する個人用サイト
 *  - データはブラウザ内(localStorage)に保存。サーバー不要
 * ================================================================== */

const EXAM_DATE = new Date(2026, 6, 4);   // 2026-07-04 G検定本番
const LOG_KEY = 'mystudy.log.v1';
const SRS_KEY = 'mystudy.progress.v1';
const TODAY_KEY = 'mystudy.today.v1';
const NEW_PER_SESSION = 20;
const DAY = 86400000;

/* ---------- 汎用 ---------- */
const $ = (id) => document.getElementById(id);
function jload(key) { try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; } }
function jsave(key, v) { localStorage.setItem(key, JSON.stringify(v)); }
async function fetchText(url) {
  const r = await fetch(url, { cache: 'no-cache' });
  if (!r.ok) throw new Error(r.status + ' ' + url);
  return r.text();
}
async function fetchJSON(url) { return JSON.parse(await fetchText(url)); }

function startOfDay(ms) { const d = new Date(ms); d.setHours(0,0,0,0); return d.getTime(); }
function dateKey(d) { return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; }
function mdKey(d) { return `${d.getMonth()+1}/${d.getDate()}`; }   // "6/24"
const WD = ['日','月','火','水','木','金','土'];

/* ================================================================== *
 * 画面遷移（下部タブ）
 * ================================================================== */
const SCREENS = {
  home: $('home-screen'), plan: $('plan-screen'), log: $('log-screen'),
  content: $('content-screen'), note: $('note-screen'),
  study: $('study-screen'), done: $('done-screen'),
};
const SCREEN_TAB = { home:'home', plan:'plan', log:'log', content:'content', note:'content', study:'content', done:'content' };
const SUBSCREENS = new Set(['note','study','done']);

function showScreen(name) {
  for (const k in SCREENS) SCREENS[k].hidden = (k !== name);
  $('back-btn').hidden = !SUBSCREENS.has(name);
  const tab = SCREEN_TAB[name];
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  const titles = { home:'学習ハブ', plan:'計画', log:'記録', content:'コンテンツ', note:'ノート', study:'暗記カード', done:'完了' };
  $('app-title').textContent = titles[name] || '学習ハブ';
  window.scrollTo(0, 0);
}
let currentTab = 'home';
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => { currentTab = tab.dataset.tab; openTab(currentTab); });
});
function openTab(name) {
  if (name === 'plan') renderPlan();
  else if (name === 'log') renderLog();
  else if (name === 'content') renderContent();
  else renderHome();
}
$('back-btn').addEventListener('click', () => openTab(currentTab));

/* ================================================================== *
 * ホーム
 * ================================================================== */
let planText = '';

function renderHome() {
  showScreen('home');
  const now = new Date();
  $('hero-date').textContent = `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日（${WD[now.getDay()]}）`;

  const days = Math.ceil((startOfDay(EXAM_DATE.getTime()) - startOfDay(now.getTime())) / DAY);
  const cd = $('hero-countdown');
  if (days > 0) cd.textContent = `G検定本番まで あと ${days} 日`;
  else if (days === 0) cd.textContent = '🎯 今日が本番！';
  else cd.textContent = 'G検定 おつかれさまでした';

  // 今日のタスク（G検定＋英語を一括チェックリスト化）
  buildTodayChecklist(now);

  // 統計
  const log = jload(LOG_KEY);
  $('stat-streak').textContent = streak(log);
  $('stat-total').textContent = Object.keys(log).length;
  const todayEntry = log[dateKey(now)];
  $('stat-done').textContent = todayEntry ? (todayEntry.status === '達成' ? '達成' : todayEntry.status) : '未';
}

/* 今日のタスク = G検定（計画から）＋ 英語（毎日ルーティン）を一括表示。
   各タスクから、対応するノート/暗記カードを直接開けるボタンを付ける。 */
function buildTodayChecklist(now) {
  const items = [];

  // G検定
  const gkenSection = todaysTask(now);
  const hasGken = !gkenSection.startsWith('_');   // 見つからない時は斜体プレースホルダ
  if (hasGken) {
    const { time, title } = parseGkenTitle(gkenSection.split('\n')[0]);
    const { noteIds, deckIds } = refsFromSection(gkenSection);
    const actions = [];
    noteIds.forEach(id => actions.push({ type: 'note', id, label: '📖 ' + noteTitle(id) }));
    deckIds.forEach(id => actions.push({ type: 'deck', id, label: '🃏 ' + deckName(id) }));
    if (actions.length === 0) actions.push({ type: 'tab', id: 'content', label: '📚 コンテンツを開く' });
    items.push({ id: 'gken', main: 'G検定' + (time ? `（${time}）` : ''), sub: title, actions });
  }

  // 英語（毎日ルーティン）
  const en = contentManifest && contentManifest.english;
  if (en && en.active) {
    const ramped = en.rampDate && dateKey(now) >= en.rampDate;
    const daily = (ramped && en.rampDaily) ? en.rampDaily : en.daily;
    const mins = ramped ? '本格' : (en.minutes || '');
    const actions = [{ type: 'note', id: 'english', label: '📖 英語ノート' }];
    if (decks.find(d => d.id === 'english')) actions.push({ type: 'deck', id: 'english', label: '🃏 英単語カード' });
    items.push({ id: 'english', main: (en.label || '英語') + (mins ? `（${mins}）` : ''), sub: daily, actions });
  }

  const state = (jload(TODAY_KEY))[dateKey(now)] || {};
  const box = $('today-checklist');
  box.innerHTML = items.length ? items.map(it => `
    <div class="check-item ${state[it.id] ? 'done' : ''}" data-id="${it.id}">
      <label class="ci-check">
        <input type="checkbox" ${state[it.id] ? 'checked' : ''} />
        <span class="ci-body"><span class="ci-main">${escapeHtml(it.main)}</span><span class="ci-sub">${escapeHtml(it.sub)}</span></span>
      </label>
      ${it.actions.length ? `<div class="ci-actions">${it.actions.map(a =>
        `<button class="ci-btn" data-act="${a.type}" data-aid="${a.id}">${escapeHtml(a.label)}</button>`).join('')}</div>` : ''}
    </div>`).join('') : '<p class="dim">今日のタスクはありません。</p>';

  // チェックボックス（消し込み）
  box.querySelectorAll('.ci-check input').forEach(inp => {
    inp.addEventListener('change', () => {
      const id = inp.closest('.check-item').dataset.id;
      const all = jload(TODAY_KEY); const day = all[dateKey(now)] || {};
      day[id] = inp.checked; all[dateKey(now)] = day; jsave(TODAY_KEY, all);
      inp.closest('.check-item').classList.toggle('done', inp.checked);
      updateDoneBadge(items, now);
    });
  });

  // コンテンツへのジャンプボタン
  box.querySelectorAll('.ci-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const { act, aid } = btn.dataset;
      if (act === 'note') openNoteById(aid);
      else if (act === 'deck') { const d = decks.find(x => x.id === aid); if (d) { currentTab = 'content'; startStudy(d); } }
      else if (act === 'tab') { currentTab = aid; openTab(aid); }
    });
  });

  // G検定の手順詳細
  const det = $('gken-detail');
  if (hasGken) { det.hidden = false; $('today-gken-detail').innerHTML = renderMarkdown(gkenSection); }
  else det.hidden = true;

  updateDoneBadge(items, now);
}

/* 計画の「📚 参照:」行から、ノートid・デッキidを取り出す */
function refsFromSection(section) {
  const line = section.split('\n').find(l => l.includes('📚')) || '';
  const noteFrags = [...line.matchAll(/「([^」]+)」/g)].map(m => m[1]);
  const deckIds = [...line.matchAll(/`([^`]+)`/g)].map(m => m[1]).filter(id => decks.some(d => d.id === id));
  const notes = (contentManifest && contentManifest.notes) || [];
  const noteIds = [];
  noteFrags.forEach(frag => {
    const n = notes.find(n => n.title.startsWith(frag) || frag.startsWith(n.title) || sameLead(n.title, frag));
    if (n && !noteIds.includes(n.id)) noteIds.push(n.id);
  });
  return { noteIds, deckIds };
}
function sameLead(a, b) { const c = (a.trim()[0] || ''); return '①②③④⑤⑥⑦⑧'.includes(c) && b.trim()[0] === c; }
function noteTitle(id) { const n = ((contentManifest && contentManifest.notes) || []).find(n => n.id === id); return n ? n.title : 'ノート'; }
function deckName(id) { const d = decks.find(d => d.id === id); return d ? d.name : 'カード'; }
function openNoteById(id) {
  const n = ((contentManifest && contentManifest.notes) || []).find(n => n.id === id);
  if (n) { currentTab = 'content'; openNote(n); }
}

function updateDoneBadge(items, now) {
  const state = (jload(TODAY_KEY))[dateKey(now)] || {};
  $('today-done-badge').hidden = !(items.length > 0 && items.every(it => state[it.id]));
}

function parseGkenTitle(headingLine) {
  const s = headingLine.replace(/^#+\s*/, '').trim();
  const parts = s.split('|');
  if (parts.length >= 3) return { time: parts[1].trim(), title: parts.slice(2).join('|').trim() };
  const m = s.match(/^\d{1,2}\/\d{1,2}\([^)]*\)\s*(.*)$/);
  return { time: '', title: (m ? m[1] : s).trim() };
}

function todaysTask(d) {
  if (!planText) return '_計画を読み込み中…_';
  const key = mdKey(d);
  const lines = planText.split('\n');
  // 1) "## 6/24..." 見出しセクション（コードフェンス内は無視）
  let inFence = false;
  for (let i = 0; i < lines.length; i++) {
    if (/^```/.test(lines[i])) { inFence = !inFence; continue; }
    if (inFence) continue;
    const m = lines[i].match(/^##\s+(\d{1,2})\/(\d{1,2})/);
    if (m && `${+m[1]}/${+m[2]}` === key) {
      const out = [lines[i]];
      for (let j = i+1; j < lines.length; j++) {
        if (/^(#|##|---)/.test(lines[j])) break;
        out.push(lines[j]);
      }
      return out.join('\n').trim();
    }
  }
  // 2) 本番週の箇条書き "- **6/29(月)** ..."
  const esc = key.replace('/', '\\/');
  const re = new RegExp(`\\*\\*${esc}\\(`);
  for (const ln of lines) if (re.test(ln)) return ln.replace(/^-\s*/, '');
  return '_今日のタスクは計画に見つかりませんでした。「計画」タブを確認してください。_';
}

/* 連続記録日数（今日 or 昨日から遡る） */
function streak(log) {
  let d = new Date(); d.setHours(0,0,0,0);
  if (!log[dateKey(d)]) d = new Date(d.getTime() - DAY);
  let n = 0;
  while (log[dateKey(d)]) { n++; d = new Date(d.getTime() - DAY); }
  return n;
}

$('quick-log').addEventListener('click', () => { currentTab = 'log'; openTab('log'); });

/* ================================================================== *
 * 計画
 * ================================================================== */
function renderPlan() {
  showScreen('plan');
  $('plan-content').innerHTML = planText
    ? highlightToday(renderMarkdown(planText))
    : '<p class="dim">計画を読み込めませんでした。</p>';
  // 今日のセクションへスクロール
  const el = $('plan-content').querySelector('.today-marker');
  if (el) el.scrollIntoView({ block: 'start' });
}
// 今日の見出しに目印クラスを付ける
function highlightToday(html) {
  const key = mdKey(new Date()).replace('/', '\\/');
  return html.replace(
    new RegExp(`(<h2[^>]*>\\s*${key}\\b)`),
    '<span class="today-marker"></span>$1'
  ).replace(/<h2([^>]*)>(\s*\d{1,2}\/\d{1,2}\b[^<]*今日?)/, '<h2$1 class="is-today">$2');
}

/* ================================================================== *
 * 記録
 * ================================================================== */
let logStatus = '';

function renderLog() {
  showScreen('log');
  const now = new Date();
  $('log-date').textContent = mdKey(now) + '（' + WD[now.getDay()] + '）';
  const log = jload(LOG_KEY);
  const e = log[dateKey(now)];

  logStatus = e ? e.status : '';
  document.querySelectorAll('#log-status button').forEach(b =>
    b.classList.toggle('on', b.dataset.v === logStatus));
  $('log-answer').value = e ? (e.answer || '') : '';
  $('log-quiz-correct').value = e && e.quizCorrect != null ? e.quizCorrect : '';
  $('log-quiz-total').value = e && e.quizTotal != null ? e.quizTotal : '';
  $('log-saved-msg').hidden = true;

  renderHistory(log);
}

document.querySelectorAll('#log-status button').forEach(b => {
  b.addEventListener('click', () => {
    logStatus = b.dataset.v;
    document.querySelectorAll('#log-status button').forEach(x => x.classList.toggle('on', x === b));
  });
});

function currentLogEntry() {
  const c = $('log-quiz-correct').value, t = $('log-quiz-total').value;
  return {
    status: logStatus || '未着手',
    answer: $('log-answer').value.trim(),
    quizCorrect: c === '' ? null : Number(c),
    quizTotal: t === '' ? null : Number(t),
    ts: Date.now(),
  };
}

$('log-save').addEventListener('click', () => {
  const log = jload(LOG_KEY);
  log[dateKey(new Date())] = currentLogEntry();
  jsave(LOG_KEY, log);
  const msg = $('log-saved-msg');
  msg.textContent = '✓ 保存しました（連続 ' + streak(log) + ' 日）';
  msg.hidden = false;
  renderHistory(log);
});

$('log-copy').addEventListener('click', async () => {
  const text = logToMd(new Date(), currentLogEntry());
  try { await navigator.clipboard.writeText(text); $('log-copy').textContent = '✓ コピーしました'; }
  catch { prompt('コピーしてください:', text); }
  setTimeout(() => { $('log-copy').textContent = 'log.md形式でコピー'; }, 1500);
});

function logToMd(d, e) {
  const quiz = (e.quizCorrect != null && e.quizTotal != null) ? `${e.quizCorrect}/${e.quizTotal}` : '_/10';
  return `## ${mdKey(d)}\n🏁: ${e.status}\n📝の答え: ${e.answer || ''}\nクイズ正答: ${quiz}`;
}

function renderHistory(log) {
  const keys = Object.keys(log).sort().reverse();
  const box = $('log-history');
  if (keys.length === 0) { box.innerHTML = '<p class="dim">まだ記録がありません。</p>'; return; }
  box.innerHTML = keys.map(k => {
    const e = log[k];
    const [y,m,da] = k.split('-').map(Number);
    const cls = e.status === '達成' ? 'ok' : e.status === '一部' ? 'half' : 'no';
    const quiz = (e.quizCorrect != null && e.quizTotal != null) ? `<span class="h-quiz">${e.quizCorrect}/${e.quizTotal}</span>` : '';
    return `<div class="h-row">
      <div class="h-date">${m}/${da}</div>
      <span class="h-badge ${cls}">${e.status}</span>
      ${quiz}
      <div class="h-ans">${escapeHtml(e.answer || '')}</div>
    </div>`;
  }).join('');
}
function escapeHtml(s){ return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

/* ================================================================== *
 * コンテンツ（ノート + 暗記カード）
 * ================================================================== */
let contentManifest = null;
let decks = [];

function renderContent() {
  showScreen('content');
  // ノート一覧
  const nl = $('note-list');
  const notes = (contentManifest && contentManifest.notes) || [];
  nl.innerHTML = notes.length ? notes.map((n,i) => `
    <li class="list-card" data-note="${i}">
      <div class="lc-info"><div class="lc-title"></div><div class="lc-desc"></div></div>
      <div class="lc-go">›</div>
    </li>`).join('') : '<li class="dim" style="padding:8px">ノートがありません。</li>';
  notes.forEach((n,i) => {
    const li = nl.querySelector(`[data-note="${i}"]`);
    if (!li) return;
    li.querySelector('.lc-title').textContent = n.title;
    li.querySelector('.lc-desc').textContent = n.desc || '';
    li.addEventListener('click', () => openNote(n));
  });

  // 暗記カード一覧
  const dl = $('deck-list');
  dl.innerHTML = decks.length ? decks.map((dk,i) => {
    const c = deckCounts(dk);
    return `<li class="list-card" data-deck="${i}">
      <div class="lc-info"><div class="lc-title"></div>
        <div class="deck-badges">
          ${c.due?`<span class="badge due">復習 ${c.due}</span>`:''}
          ${c.new?`<span class="badge new">新規 ${c.new}</span>`:''}
          <span class="badge">全 ${c.total}</span>
        </div></div>
      <div class="lc-go">›</div></li>`;
  }).join('') : '<li class="dim" style="padding:8px">カードデッキがありません。</li>';
  decks.forEach((dk,i) => {
    const li = dl.querySelector(`[data-deck="${i}"]`);
    if (!li) return;
    li.querySelector('.lc-title').textContent = dk.name;
    li.addEventListener('click', () => startStudy(dk));
  });
}

async function openNote(n) {
  showScreen('note');
  $('note-content').innerHTML = '<p class="dim">読み込み中…</p>';
  try {
    const md = await fetchText('content/' + n.file);
    $('note-content').innerHTML = renderMarkdown(md);
  } catch (e) {
    $('note-content').innerHTML = '<p class="dim">読み込みエラー：' + e.message + '</p>';
  }
}

/* ================================================================== *
 * フラッシュカード（SRS・補助機能）
 * ================================================================== */
let progress = jload(SRS_KEY);
function cardState(k){ return progress[k] || { ease:2.5, interval:0, reps:0, due:0, isNew:true }; }

function schedule(state, q) {
  let { ease, interval, reps } = state;
  if (q === 0) { reps=0; interval=0; ease=Math.max(1.3, ease-0.2); }
  else {
    if (q===1) ease=Math.max(1.3, ease-0.15);
    if (q===3) ease=ease+0.15;
    if (reps===0) interval = q===3?2:1;
    else if (reps===1) interval = q===1?3:6;
    else interval = Math.round(interval * (q===1?1.2:(q===3?ease*1.3:ease)));
    reps += 1;
  }
  const due = interval===0 ? Date.now() : startOfDay(Date.now()+interval*DAY);
  return { ease, interval, reps, due, isNew:false };
}
function previewLabel(state, q) {
  const n = schedule(state, q);
  if (n.interval===0) return 'すぐ';
  if (n.interval===1) return '1日';
  if (n.interval<30) return n.interval+'日';
  if (n.interval<365) return Math.round(n.interval/30)+'ヶ月';
  return (n.interval/365).toFixed(1)+'年';
}
function deckCounts(deck) {
  const now = Date.now(); let due=0, fresh=0;
  for (const c of deck.cards) {
    const st = cardState(deck.id+':'+c.id);
    if (st.isNew) fresh++; else if (st.due<=now) due++;
  }
  return { due, new: Math.min(fresh, NEW_PER_SESSION), total: deck.cards.length };
}

let session = null;
function startStudy(deck) {
  const now = Date.now(), dueC=[], newC=[];
  for (const c of deck.cards) {
    const st = cardState(deck.id+':'+c.id);
    if (st.isNew) newC.push(c); else if (st.due<=now) dueC.push(c);
  }
  let queue = dueC.concat(newC.slice(0, NEW_PER_SESSION));
  if (queue.length === 0) queue = deck.cards.slice();  // 全部終わってたら通し復習
  session = { deck, queue, total: queue.length, reviewed:0, again:0, answered:false };
  showScreen('study');
  nextCard();
}

function shuffle(a) { for (let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; }

/* 同一デッキの他カードの裏をダミー選択肢にして4択を作る */
function buildChoices(deck, card) {
  const others = shuffle(deck.cards.filter(c => c.id !== card.id && c.back !== card.back));
  const distract = others.slice(0, 3).map(c => c.back);
  const opts = shuffle([card.back, ...distract]);
  return { opts, correct: opts.indexOf(card.back) };
}

function nextCard() {
  if (!session || session.queue.length === 0) return finishStudy();
  session.current = session.queue[0];
  session.answered = false;
  session.choices = buildChoices(session.deck, session.current);

  $('card-front').textContent = session.current.front;
  $('study-count').textContent = `${session.deck.name}　${session.total - session.queue.length + 1} / ${session.total}`;

  const box = $('mc-options');
  box.innerHTML = session.choices.opts.map((t, i) =>
    `<button class="mc-opt" data-i="${i}"><span class="mc-key">${i+1}</span><span>${escapeHtml(t)}</span></button>`).join('');

  $('mc-result').hidden = true;
  $('mc-explain').hidden = true;
  $('mc-next').hidden = true;
  $('progress-fill').style.width = Math.round((session.total - session.queue.length)/session.total*100)+'%';
}

function selectOption(idx) {
  if (!session || session.answered) return;
  session.answered = true;
  const correct = idx === session.choices.correct;

  $('mc-options').querySelectorAll('.mc-opt').forEach(b => {
    const i = +b.dataset.i;
    b.disabled = true;
    if (i === session.choices.correct) b.classList.add('correct');
    else if (i === idx) b.classList.add('wrong');
  });

  const res = $('mc-result');
  res.className = 'mc-result ' + (correct ? 'ok' : 'ng');
  res.textContent = correct ? '✓ 正解' : '✗ 不正解（正解は緑）';
  res.hidden = false;

  // 解説（背景つき）
  const ex = $('mc-explain');
  if (session.current.explain) {
    ex.innerHTML = '<div class="ex-label">解説</div><div class="ex-body"></div>';
    ex.querySelector('.ex-body').textContent = session.current.explain;
    ex.hidden = false;
  } else { ex.hidden = true; }

  $('mc-next').hidden = false;
  $('mc-next').focus();

  // SRS反映：正解=ふつう(2) / 不正解=もう一度(0)
  const q = correct ? 2 : 0;
  const key = session.deck.id+':'+session.current.id;
  progress[key] = schedule(cardState(key), q); jsave(SRS_KEY, progress);
  session.queue.shift();
  if (q === 0) { session.again++; session.queue.splice(Math.min(session.queue.length,4),0,session.current); }
  else session.reviewed++;
}

function finishStudy() {
  showScreen('done');
  const total = session.reviewed + session.again;
  const acc = total ? Math.round(session.reviewed/total*100) : 0;
  $('done-stats').textContent = `正解 ${session.reviewed} / 出題 ${total}（正答率 ${acc}%）` + (session.again?`　再出題 ${session.again}回`:'');
}

$('mc-options').addEventListener('click', (e) => { const b = e.target.closest('.mc-opt'); if (b && !b.disabled) selectOption(+b.dataset.i); });
$('mc-next').addEventListener('click', nextCard);
$('done-back').addEventListener('click', () => openTab('content'));
document.addEventListener('keydown', (e) => {
  if (SCREENS.study.hidden) return;
  if (!session.answered && ['1','2','3','4'].includes(e.key)) {
    const b = $('mc-options').querySelector(`.mc-opt[data-i="${+e.key-1}"]`);
    if (b) selectOption(+e.key-1);
  } else if (session.answered && (e.code === 'Enter' || e.code === 'Space')) {
    e.preventDefault(); nextCard();
  }
});

/* ================================================================== *
 * Markdown
 * ================================================================== */
function renderMarkdown(md) {
  if (window.marked) { marked.setOptions({ breaks:true, gfm:true }); return marked.parse(md); }
  return '<pre>' + escapeHtml(md) + '</pre>';
}

/* ================================================================== *
 * テーマ
 * ================================================================== */
function initTheme() {
  const saved = localStorage.getItem('mystudy.theme');
  setTheme(saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
}
function setTheme(t) { document.documentElement.setAttribute('data-theme', t); localStorage.setItem('mystudy.theme', t); }
$('theme-btn').addEventListener('click', () => {
  setTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});

/* ================================================================== *
 * 起動
 * ================================================================== */
initTheme();
Promise.all([
  fetchText('content/plan.md').then(t => planText = t).catch(()=>{}),
  fetchJSON('content/manifest.json').then(m => contentManifest = m).catch(()=>{}),
  fetchJSON('data/manifest.json')
    .then(m => Promise.all(m.decks.map(p => fetchJSON('data/'+p).catch(()=>null))))
    .then(ds => decks = ds.filter(Boolean)).catch(()=>{}),
]).then(renderHome);

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(()=>{}));
}
