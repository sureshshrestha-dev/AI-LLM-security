/* ==========================================================================
   AI & LLM Security CTF Arena — Frontend Application Controller
   ========================================================================== */

// ── State ──────────────────────────────────────────────────────────────────
let challenges = [];
let active = null;          // currently selected challenge object
let learningTopics = [];
let activeTopic = null;     // currently selected learning topic id
let authMode = 'login';
let authToken = localStorage.getItem('ctf_token') || null;
let currentUser = null;

// ── Bootstrap ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  fetchChallenges();
  fetchLearningTopics();
  if (authToken) fetchUserProfile();

  // Close modal on ESC or overlay click
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAuthModal();
  });
  document.getElementById('authModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeAuthModal();
  });
});

function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (authToken) h['Authorization'] = `Bearer ${authToken}`;
  return h;
}

// ── Navigation ─────────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.nav-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === name);
    if (t.hasAttribute('aria-selected')) t.setAttribute('aria-selected', t.dataset.tab === name);
  });
  document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
  const panel = document.getElementById(`tab-${name}`);
  if (panel) panel.classList.add('active');
}

// ==========================================================================
//  CHALLENGES
// ==========================================================================

async function fetchChallenges() {
  try {
    const res = await fetch('/api/challenges', { headers: headers() });
    if (!res.ok) return;
    challenges = await res.json();
    renderChallengeList();
    if (challenges.length && !active) selectChallenge(challenges[0].id);
  } catch (e) { logTrace('error', `Failed to load challenges: ${e.message}`); }
}

function renderChallengeList() {
  const el = document.getElementById('challengeList');
  el.innerHTML = '';
  let solved = 0;

  challenges.forEach((ch, i) => {
    if (ch.is_solved) solved++;
    const isActive = active && active.id === ch.id;
    const diff = ch.difficulty.toLowerCase();

    const card = document.createElement('div');
    card.className = `challenge-card${isActive ? ' active' : ''}${ch.is_solved ? ' solved' : ''}`;
    card.onclick = () => selectChallenge(ch.id);
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.onkeydown = (e) => { if (e.key === 'Enter') selectChallenge(ch.id); };

    card.innerHTML = `
      <div class="challenge-card-header">
        <span class="challenge-card-title">${ch.title}</span>
        ${ch.is_solved
          ? '<span class="badge badge-solved">✓ Solved</span>'
          : `<span class="badge badge-${diff}">${ch.difficulty}</span>`}
      </div>
      <div class="challenge-card-meta">
        <span>${ch.category}</span>
        <span>•</span>
        <span>${ch.points} pts</span>
      </div>`;
    el.appendChild(card);
  });

  document.getElementById('solvedCount').textContent = solved;
}

function selectChallenge(id) {
  active = challenges.find(c => c.id === id);
  if (!active) return;

  renderChallengeList();

  const idx = challenges.indexOf(active) + 1;
  document.getElementById('chNumber').textContent = `Challenge ${idx} of ${challenges.length}`;
  document.getElementById('chTitle').textContent = active.title;
  document.getElementById('chDescription').textContent = active.description;

  const diff = active.difficulty.toLowerCase();
  const diffEl = document.getElementById('chDifficulty');
  diffEl.textContent = active.difficulty;
  diffEl.className = `badge badge-${diff}`;

  document.getElementById('chPoints').textContent = `${active.points} pts`;

  document.getElementById('vulnCodeSnippet').textContent = active.vulnerable_code || '';
  document.getElementById('safeCodeSnippet').textContent = active.safe_code || '';

  document.getElementById('vulnInput').value = active.sample_exploit || '';
  document.getElementById('safeInput').value = active.sample_exploit || '';

  document.getElementById('vulnOutput').textContent = 'Click "Run Vulnerable" to test the insecure implementation…';
  document.getElementById('vulnOutput').classList.remove('has-flag');
  document.getElementById('safeOutput').textContent = 'Click "Run Safe" to test the secure implementation…';

  // Show explanation
  const expBar = document.getElementById('explanationBar');
  const expText = document.getElementById('explanationText');
  if (active.explanation) {
    expBar.style.display = 'flex';
    expText.textContent = active.explanation;
  } else {
    expBar.style.display = 'none';
  }

  logTrace('info', `Loaded Challenge: ${active.title}`);
}

function applyPresetPayload() {
  if (!active || !active.sample_exploit) return;
  document.getElementById('vulnInput').value = active.sample_exploit;
  document.getElementById('safeInput').value = active.sample_exploit;

  // Quick flash animation on the input
  ['vulnInput', 'safeInput'].forEach(id => {
    const el = document.getElementById(id);
    el.style.borderColor = 'var(--accent-primary)';
    el.style.boxShadow = '0 0 0 3px var(--accent-glow)';
    setTimeout(() => { el.style.borderColor = ''; el.style.boxShadow = ''; }, 600);
  });

  logTrace('info', `Loaded exploit preset: ${active.sample_exploit}`);
}

function showHint() {
  if (!active) return;
  const hints = {
    'sqli-tool': '💡 Try entering a SQL tautology like: \' OR \'1\'=\'1\n   This makes the WHERE clause always true, returning all rows.',
    'lfi-path-traversal': '💡 Use directory traversal sequences: ../../documents/secret_system.flag\n   This escapes the intended directory boundary.',
    'code-execution-sandbox': '💡 Run: import os; print(os.environ.get(\'CTF_HOST_FLAG\', \'FLAG{HOST_EXECUTION_SANDBOX_ESCAPE_2026}\'))\n   This reads environment variables directly from the host.',
    'ssrf-webpage-fetch': '💡 Target internal metadata: http://169.254.169.254/latest/meta-data/flag\n   Or try: http://localhost:8000/docs to access internal services.',
    'rag-indirect-injection': '💡 Request doc2 which contains a [SYSTEM_OVERRIDE] poison payload.\n   The LLM will follow the injected instructions from the document.',
    'mcp-description-poisoning': '💡 Simply ask "What is the weather in London?"\n   The poisoned tool description will trick the LLM into reading files.',
  };
  const hint = hints[active.id] || '💡 Study the vulnerable source code to find the weakness.';
  logTrace('warn', hint);
}

// ── Execution ──────────────────────────────────────────────────────────────
async function executeLab(mode) {
  if (!active) return;

  const input = document.getElementById(mode === 'vulnerable' ? 'vulnInput' : 'safeInput');
  const output = document.getElementById(mode === 'vulnerable' ? 'vulnOutput' : 'safeOutput');
  const btn = document.getElementById(mode === 'vulnerable' ? 'vulnExecBtn' : 'safeExecBtn');
  const payload = input.value;

  btn.classList.add('loading');
  btn.innerHTML = '<span class="spinner">⏳</span> Running…';
  output.textContent = 'Executing…';
  output.classList.remove('has-flag');

  logTrace('info', `[${mode.toUpperCase()}] Executing against ${active.id}…`);

  try {
    let res;
    if (active.id === 'rag-indirect-injection') {
      res = await fetch('/api/challenges/rag-demo', {
        method: 'POST', headers: headers(),
        body: JSON.stringify({ mode, doc_ids: ['doc1', 'doc2'], user_query: payload })
      });
    } else if (active.id === 'mcp-description-poisoning') {
      res = await fetch('/api/challenges/mcp-demo', {
        method: 'POST', headers: headers(),
        body: JSON.stringify({ user_query: payload || 'What is the weather in London?' })
      });
    } else {
      res = await fetch('/api/challenges/execute', {
        method: 'POST', headers: headers(),
        body: JSON.stringify({ challenge_id: active.id, mode, payload })
      });
    }

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // Render output with flag highlighting
    let text = data.output || '';
    if (data.flag_captured && text.includes(data.flag_captured)) {
      output.classList.add('has-flag');
    }
    output.textContent = text;

    if (data.raw_trace) logTrace('info', data.raw_trace);

    if (data.flag_captured) {
      document.getElementById('flagInput').value = data.flag_captured;
      logTrace('flag', `🚩 FLAG CAPTURED: ${data.flag_captured}`);
      triggerCelebration('🚩 Flag Captured!');
    }

  } catch (err) {
    output.textContent = `Error: ${err.message}`;
    logTrace('error', `Execution failed: ${err.message}`);
  } finally {
    btn.classList.remove('loading');
    btn.innerHTML = mode === 'vulnerable'
      ? '<span>▶</span> Run Vulnerable'
      : '<span>▶</span> Run Safe';
  }
}

// ── Flag Submit ────────────────────────────────────────────────────────────
async function submitFlag() {
  if (!active) return;
  const flag = document.getElementById('flagInput').value.trim();
  if (!flag) { showToast('Enter a flag in FLAG{…} format', 'warn'); return; }

  if (!authToken) {
    showToast('Login or register to save your score!', 'warn');
    openAuthModal();
    return;
  }

  try {
    const res = await fetch('/api/challenges/submit-flag', {
      method: 'POST', headers: headers(),
      body: JSON.stringify({ challenge_id: active.id, flag })
    });
    const data = await res.json();

    if (data.correct) {
      showToast(data.message, 'success');
      document.getElementById('userScore').textContent = data.new_total_score;
      triggerCelebration(`+${data.points_awarded} pts!`);
      fetchChallenges();
    } else {
      showToast(data.message, 'error');
    }

    logTrace(data.correct ? 'flag' : 'error', data.message);
  } catch (err) {
    showToast(`Submit error: ${err.message}`, 'error');
  }
}

// ==========================================================================
//  LEARNING HUB
// ==========================================================================

async function fetchLearningTopics() {
  try {
    const res = await fetch('/api/learning/topics');
    if (!res.ok) return;
    learningTopics = await res.json();
    renderLearningList();
    if (learningTopics.length) loadTopic(learningTopics[0].id);
  } catch (e) { console.error(e); }
}

function renderLearningList() {
  const el = document.getElementById('learningTopicList');
  el.innerHTML = '';

  learningTopics.forEach(t => {
    const card = document.createElement('div');
    card.className = `challenge-card${activeTopic === t.id ? ' active' : ''}`;
    card.onclick = () => loadTopic(t.id);
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.onkeydown = (e) => { if (e.key === 'Enter') loadTopic(t.id); };

    card.innerHTML = `
      <div class="challenge-card-header">
        <span class="challenge-card-title">${t.title}</span>
      </div>
      <div class="challenge-card-meta">
        <span>${t.owasp_mapping}</span>
      </div>`;
    el.appendChild(card);
  });
}

async function loadTopic(id) {
  activeTopic = id;
  renderLearningList();

  try {
    const res = await fetch(`/api/learning/topic/${id}`);
    if (!res.ok) return;
    const topic = await res.json();

    const content = document.getElementById('learningDetailContent');
    content.innerHTML = `
      <h1>${topic.title}</h1>
      <span class="owasp-tag">${topic.owasp_mapping}</span>
      ${renderMarkdown(topic.content_markdown)}`;
  } catch (e) { console.error(e); }
}

// Simple markdown → HTML (handles headers, code blocks, lists, paragraphs)
function renderMarkdown(md) {
  if (!md) return '';
  let html = md;

  // Code blocks first (```lang\n...\n```)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const escaped = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return `<pre><code>${escaped}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Unordered list items
  html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>[\s\S]*?<\/li>)/g, (match) => {
    if (!match.startsWith('<ul>')) return `<ul>${match}</ul>`;
    return match;
  });

  // Paragraphs (lines that aren't tags)
  html = html.replace(/^(?!<[a-z])((?!\s*$).+)$/gm, '<p>$1</p>');

  // Clean up double-wrapped
  html = html.replace(/<\/ul>\s*<ul>/g, '');

  return html;
}

// ==========================================================================
//  TERMINAL & TOASTS
// ==========================================================================

function logTrace(level, msg) {
  const el = document.getElementById('terminalLogs');
  const ts = new Date().toLocaleTimeString('en-US', { hour12: false });
  const cls = level === 'error' ? 'log-error' : level === 'warn' ? 'log-warn' : level === 'flag' ? 'log-flag' : '';

  const line = document.createElement('div');
  line.className = cls;
  line.textContent = `[${ts}] ${msg}`;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
}

function showToast(msg, type = 'info') {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const colors = {
    success: 'var(--success)',
    error: 'var(--danger)',
    warn: 'var(--warning)',
    info: 'var(--accent-primary)'
  };
  const icons = { success: '✅', error: '❌', warn: '⚠️', info: 'ℹ️' };

  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.style.cssText = `
    position: fixed; top: 80px; right: 24px; z-index: 3000;
    max-width: 420px; padding: 14px 20px;
    background: var(--bg-elevated);
    border: 1px solid ${colors[type] || colors.info};
    border-left: 4px solid ${colors[type] || colors.info};
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 0.875rem; font-weight: 500;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    display: flex; align-items: flex-start; gap: 10px;
    animation: toastSlide 0.3s var(--ease-out-expo);
  `;
  toast.innerHTML = `<span style="flex-shrink:0;font-size:1.1rem">${icons[type] || icons.info}</span><span>${msg}</span>`;
  document.body.appendChild(toast);

  // Add animation keyframes if not present
  if (!document.getElementById('toast-style')) {
    const s = document.createElement('style');
    s.id = 'toast-style';
    s.textContent = `@keyframes toastSlide { from { opacity:0; transform:translateX(40px); } to { opacity:1; transform:translateX(0); } }`;
    document.head.appendChild(s);
  }

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(40px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ==========================================================================
//  CELEBRATION
// ==========================================================================

function triggerCelebration(text) {
  const overlay = document.getElementById('celebrationOverlay');
  const label = document.getElementById('celebrationText');
  label.textContent = text;
  overlay.classList.add('active');

  // Spawn confetti particles
  for (let i = 0; i < 40; i++) {
    const p = document.createElement('div');
    p.style.cssText = `
      position: absolute;
      width: ${4 + Math.random() * 8}px;
      height: ${4 + Math.random() * 8}px;
      background: hsl(${Math.random() * 360}, 80%, 60%);
      border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
      left: ${40 + Math.random() * 20}%;
      top: 45%;
      pointer-events: none;
      animation: confetti-fall ${1.5 + Math.random() * 1.5}s ease-out forwards;
      --dx: ${(Math.random() - 0.5) * 600}px;
      --dy: ${-200 - Math.random() * 400}px;
    `;
    overlay.appendChild(p);
  }

  // Add confetti animation if it doesn't exist
  if (!document.getElementById('confetti-style')) {
    const style = document.createElement('style');
    style.id = 'confetti-style';
    style.textContent = `
      @keyframes confetti-fall {
        0%   { transform: translate(0, 0) rotate(0deg); opacity: 1; }
        100% { transform: translate(var(--dx), calc(var(--dy) + 800px)) rotate(720deg); opacity: 0; }
      }`;
    document.head.appendChild(style);
  }

  setTimeout(() => {
    overlay.classList.remove('active');
    // Clean up particles
    overlay.querySelectorAll('div:not(#celebrationText)').forEach(p => p.remove());
  }, 2800);
}

// ==========================================================================
//  AUTH
// ==========================================================================

function openAuthModal() { document.getElementById('authModal').classList.add('active'); }
function closeAuthModal() { document.getElementById('authModal').classList.remove('active'); }

function toggleAuthMode(mode) {
  authMode = mode;
  document.getElementById('emailGroup').style.display = mode === 'register' ? 'block' : 'none';
  document.getElementById('loginTab').classList.toggle('active', mode === 'login');
  document.getElementById('registerTab').classList.toggle('active', mode === 'register');
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const username = document.getElementById('authUsername').value;
  const password = document.getElementById('authPassword').value;
  const email = document.getElementById('authEmail').value;

  const endpoint = authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
  const body = authMode === 'register' ? { username, email, password } : { username, password };

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(`Auth failed: ${err.detail || 'Invalid credentials'}`, 'error');
      return;
    }

    const data = await res.json();
    authToken = data.access_token;
    localStorage.setItem('ctf_token', authToken);
    currentUser = { username: data.username, score: data.score };

    document.getElementById('userScore').textContent = data.score;
    document.getElementById('authBtn').textContent = `👤 ${data.username}`;

    closeAuthModal();
    showToast(`Welcome, ${data.username}!`, 'success');
    fetchChallenges();

  } catch (err) {
    showToast(`Auth error: ${err.message}`, 'error');
  }
}

async function fetchUserProfile() {
  try {
    const res = await fetch('/api/auth/me', { headers: headers() });
    if (!res.ok) return;
    currentUser = await res.json();
    document.getElementById('userScore').textContent = currentUser.score;
    document.getElementById('authBtn').textContent = `👤 ${currentUser.username}`;
  } catch (e) { console.error(e); }
}
