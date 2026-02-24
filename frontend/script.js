// Path: intelligent_summarizer/frontend/script.js

const HISTORY_KEY = "ai_history";

// ✅ STEP 1 — Add Emotion → Emoji Mapping
const emotionEmojiMap = {
  joy: "😊",
  sadness: "😢",
  anger: "😠",
  fear: "😨",
  disgust: "🤢",
  surprise: "😲",
  neutral: "😐",
  love: "❤️",
  excitement: "🤩"
};

/* ─── NAVIGATION ─── */
function showSection(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + id).classList.add('active');
}

/* ─── FILE SELECTION ─── */
document.getElementById('fileInput').addEventListener('change', function () {
  const f = this.files[0];
  if (!f) return;
  const lbl = document.getElementById('fileName');
  const zone = document.getElementById('dropZone');
  lbl.textContent = '📄 ' + f.name;
  zone.style.borderColor = 'var(--accent)';
  zone.style.background = 'var(--accent-dim)';
});

// Added: Emotion File selection display
document.getElementById('emotionFile')?.addEventListener('change', function () {
  const f = this.files[0];
  if (!f) return;
  const lbl = document.getElementById('emotionFileName');
  if (lbl) lbl.textContent = '📄 ' + f.name;
});

/* ─── LOADER ─── */
function setLoader(show) {
  const el = document.getElementById('summaryLoader');
  if (show) el.classList.add('show');
  else el.classList.remove('show');
  document.getElementById('summaryCard').style.opacity = show ? '.45' : '1';
  document.getElementById('analysisCard').style.opacity = show ? '.45' : '1';
}

/* ─── TOOL 1: FILE UPLOAD ─── */
async function uploadFile() {
  const file = document.getElementById('fileInput').files[0];
  if (!file) { toast('Select a PDF or DOCX file first.', 'warn'); return; }

  const fd = new FormData();
  fd.append('file', file);
  setLoader(true);

  try {
    const res = await fetch('http://127.0.0.1:8000/upload', { method: 'POST', body: fd });
    if (!res.ok) throw new Error();
    renderResults(await res.json());
  } catch {
    toast('Upload failed. Make sure the backend is running.', 'error');
  } finally {
    setLoader(false);
  }
}

/* ─── TOOL 2: TEXT SUMMARIZE ─── */
async function summarize() {
  const text = document.getElementById('textInput').value.trim();
  const mode = document.getElementById('mode').value;
  const customInput = document.getElementById('customWordCount');

  if (!text) {
    toast('Enter some text to analyze.', 'warn');
    return;
  }

  let payload = { text, mode };

  // ✅ HANDLE CUSTOM MODE PROPERLY
  if (mode === "custom") {
    const customWords = parseInt(customInput.value);

    if (!customWords || customWords < 20 || customWords > 500) {
      toast("Enter a valid custom word count (20–500).", "warn");
      return;
    }

    payload.custom_word_count = customWords;
  }

  setLoader(true);

  try {
    const res = await fetch('http://127.0.0.1:8000/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      toast(data.detail || "Summarization failed.", "error");
      return;
    }

    renderResults(data);

  } catch {
    toast('Analysis failed. Check backend connectivity.', 'error');
  } finally {
    setLoader(false);
  }
}

/* ─── RENDER RESULTS ─── */
function renderResults(data, skipHistory = false) {
  const sum = document.getElementById('summary');
  sum.classList.remove('empty');
  sum.textContent = data.summary || 'No summary generated.';

  const ana = document.getElementById('analysis');
  ana.dataset.raw = JSON.stringify(data.analysis || {});

  if (data.analysis) {
    ana.classList.remove('empty');

    const keywords = (data.analysis.keywords || [])
      .map(k => `<span class="tag">${k}</span>`).join('');

    const entities = (data.analysis.entities || [])
      .map(e => `${e[0]} (${e[1]})`).join(", ");

    const sentiment = data.analysis.sentiment || {};
    const emotion = data.analysis.emotion || {};
    const subjectivity = data.analysis.subjectivity || {};
    const readability = data.analysis.readability || {};

    ana.innerHTML = `
      <div class="intel-row">
        <div class="intel-label">Keywords</div>
        <div class="tags">${keywords}</div>
      </div>
      <div class="intel-row">
        <div class="intel-label">Entities</div>
        <div class="intel-value">${entities || "—"}</div>
      </div>
      <div class="intel-row">
        <div class="intel-label">Sentiment</div>
        <div class="intel-value">
          Compound: ${sentiment.compound ?? "—"} | Pos: ${sentiment.pos ?? "—"} | Neu: ${sentiment.neu ?? "—"} | Neg: ${sentiment.neg ?? "—"}
        </div>
      </div>
      <div class="intel-row">
        <div class="intel-label">Emotion</div>
        <div class="intel-value">${emotion.emotion ?? "—"} (Confidence: ${emotion.confidence ?? "—"})</div>
      </div>
      <div class="intel-row">
        <div class="intel-label">Subjectivity</div>
        <div class="intel-value">${subjectivity.type ?? "—"} (Score: ${subjectivity.subjectivity_score ?? "—"})</div>
      </div>
      <div class="intel-row">
        <div class="intel-label">Readability</div>
        <div class="intel-value">Grade: ${readability.grade_level ?? "—"} | Ease: ${readability.flesch_reading_ease ?? "—"}</div>
      </div>
    `;
  }

  document.getElementById('downloadWrapper').style.display = 'flex';

  if (!skipHistory && data.summary) {
    saveToHistory(data.summary, data.analysis);
  }
}

/* ─── HISTORY FUNCTIONS ─── */
function saveToHistory(summary, analysis) {
  let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  if (history.length > 0 && history[0].summary === summary) return;

  const entry = {
    timestamp: new Date().toLocaleString(),
    summary: summary,
    analysis: analysis
  };

  history.unshift(entry);
  if (history.length > 5) history = history.slice(0, 5);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  renderHistory();
}

function renderHistory() {
  const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  const container = document.getElementById("historyList");
  if (!container) return;

  if (!history.length) {
    container.innerHTML = `<p class="placeholder-text" style="color:var(--text-3); font-size:13px;">No recent analyses.</p>`;
    return;
  }

  container.innerHTML = "";
  history.forEach((item, index) => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.style.cssText = "cursor:pointer; margin-bottom:10px; padding:12px; border-radius:var(--r-md); background:var(--bg-input); border:1px solid var(--border-soft); transition:border-color var(--ease), background var(--ease);";

    div.onmouseover = () => { div.style.borderColor = "var(--accent)"; div.style.background = "var(--bg-hover)"; };
    div.onmouseout = () => { div.style.borderColor = "var(--border-soft)"; div.style.background = "var(--bg-input)"; };

    div.innerHTML = `
      <strong style="font-size:11px; color:var(--text-3); text-transform:uppercase; letter-spacing:0.05em;">${item.timestamp}</strong><br>
      <span style="font-size:13px; color:var(--text-1); display:block; margin-top:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
          ${item.summary.substring(0, 80)}...
      </span>
    `;
    div.onclick = () => loadHistoryItem(index);
    container.appendChild(div);
  });
}

function loadHistoryItem(index) {
  const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  if (!history[index]) return;
  renderResults({ summary: history[index].summary, analysis: history[index].analysis }, true);
  toast("History item loaded.", "info");
}

/* ─── EMOTION AI ─── */

async function analyzeEmotionText() {
  const text = document.getElementById("emotionInput").value.trim();
  if (!text) { toast("Please enter text first.", "warn"); return; }
  try {
    const res = await fetch("http://127.0.0.1:8000/emotion/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    displayEmotionDashboard(data);
  } catch {
    toast("Emotion analysis failed.", "error");
  }
}

async function analyzeEmotionFile() {
  const file = document.getElementById("emotionFile").files[0];
  if (!file) { toast("Please upload a document.", "warn"); return; }
  const fd = new FormData();
  fd.append("file", file);
  try {
    const res = await fetch("http://127.0.0.1:8000/emotion/file", { method: "POST", body: fd });
    if (!res.ok) throw new Error();
    const data = await res.json();
    displayEmotionDashboard(data);
  } catch {
    toast("Emotion analysis failed.", "error");
  }
}

function displayEmotionDashboard(analysis) {
  const emotion = analysis?.emotion || {};
  const subjectivity = analysis?.subjectivity || {};

  const confidencePercent = Math.round((emotion.confidence || 0) * 100);
  const subjectivityPercent = Math.round((subjectivity.subjectivity_score || 0) * 100);

  const box = document.getElementById("emotionDashboard");
  if (!box) return;

  box.classList.remove("empty");

  const emotionEmojiMap = {
    joy: "😊",
    sadness: "😢",
    anger: "😠",
    fear: "😨",
    disgust: "🤢",
    surprise: "😲",
    neutral: "😐",
    love: "❤️",
    excitement: "🤩"
  };

  const rawLabel = emotion?.emotion ?? "neutral";

  const emotionLabel = rawLabel
    .toString()
    .trim()
    .toLowerCase();

  const emoji = emotionEmojiMap[emotionLabel] ?? "😐";

  box.innerHTML = `
    <div class="intel-row">
      <div class="intel-label">Dominant Emotion</div>
      <div class="emotion-badge">
        ${emoji} ${emotionLabel.charAt(0).toUpperCase() + emotionLabel.slice(1)}
      </div>
    </div>

    <div class="intel-row">
      <div class="intel-label">Emotion Confidence</div>
      <div class="progress-track">
        <div class="progress-fill" style="width:${confidencePercent}%"></div>
      </div>
      <div class="intel-value">${confidencePercent}%</div>
    </div>

    <div class="intel-row">
      <div class="intel-label">Subjectivity</div>
      <div class="progress-track">
        <div class="progress-fill" style="width:${subjectivityPercent}%"></div>
      </div>
      <div class="intel-value">
        ${subjectivity.type || "—"} (${subjectivityPercent}%)
      </div>
    </div>
  `;
}/* ─── TOOL: DOWNLOAD PDF REPORT ─── */
async function downloadReport() {
  const summary = document.getElementById("summary").innerText;
  if (!summary || summary.includes("Your summary will appear here") || summary === "No summary generated.") {
    toast("Generate a summary first before downloading.", "warn");
    return;
  }

  const analysisBox = document.getElementById("analysis");
  let analysis = {};
  try { analysis = JSON.parse(analysisBox.dataset.raw || "{}"); } catch { analysis = {}; }

  const btn = document.getElementById("btnDownload");
  const originalText = btn.innerHTML;
  btn.innerHTML = `<div class="spinner" style="width:14px;height:14px;border-width:2px;margin-right:8px;"></div> Generating PDF...`;
  btn.disabled = true;

  try {
    const response = await fetch(`http://127.0.0.1:8000/generate-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ summary, analysis })
    });
    if (!response.ok) throw new Error();
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "AI_Document_Intelligence_Report.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    toast("PDF Report downloaded successfully!", "ok");
  } catch {
    toast("Failed to download report. Check backend.", "error");
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

/* ─── TOOL 3: WRITING ENHANCER ─── */
async function runEnhancer() {
  const text = document.getElementById("enhanceInput").value.trim();
  const mode = document.getElementById("enhanceMode").value;
  if (!text) { toast("Please enter text to enhance.", "warn"); return; }

  const btn = document.getElementById("btnRunEnhancer");
  const originalText = btn.innerHTML;
  btn.innerHTML = 'Enhancing…';
  btn.disabled = true;

  try {
    const response = await fetch("http://127.0.0.1:8000/enhance-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, mode })
    });
    if (!response.ok) throw new Error();
    const data = await response.json();
    const output = document.getElementById("enhanceOutput");
    output.classList.remove("empty");
    output.innerText = data.enhanced_text || "No response generated.";
    toast("Text enhanced successfully!", "ok");
  } catch {
    toast("Enhancement failed. Check backend connectivity.", "error");
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function toggleCustomLength() {
  const mode = document.getElementById("mode").value;
  const wrapper = document.getElementById("customLengthWrapper");

  wrapper.style.display = mode === "custom" ? "block" : "none";
}

/* ─── TOOL 4: SIMILARITY ─── */
async function checkSimilarity() {
  const t1 = document.getElementById('text1').value.trim();
  const t2 = document.getElementById('text2').value.trim();
  if (!t1 || !t2) { toast('Both text fields are required.', 'warn'); return; }

  const btn = document.querySelector('.center-row .btn');
  btn.textContent = 'Analyzing…';
  btn.disabled = true;

  try {
    const res = await fetch('http://127.0.0.1:8000/similarity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text1: t1, text2: t2 })
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    const pct = Math.round(data.similarity_score * 100);
    document.getElementById('similarityResult').textContent = `${pct}% — ${data.interpretation}`;
    const bar = document.getElementById('similarityBar');
    bar.style.width = '0%';
    requestAnimationFrame(() => { bar.style.width = pct + '%'; });
  } catch {
    toast('Comparison failed.', 'error');
  } finally {
    btn.textContent = 'Run Comparison →';
    btn.disabled = false;
  }
}

/* ─── TOOL 5: RAG ─── */
async function buildRAG() {
  const text = document.getElementById('ragDocument').value.trim();
  const status = document.getElementById('ragStatus');
  if (!text) { toast('Paste document content to index.', 'warn'); return; }
  status.textContent = 'Indexing…';
  try {
    const res = await fetch('http://127.0.0.1:8000/rag/build', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    status.textContent = '✓ ' + data.message;
    status.style.color = 'var(--accent)';
  } catch {
    status.textContent = '✕ Indexing failed.';
    status.style.color = '#f87171';
  }
}

async function askQuestion() {
  const input = document.getElementById('userQuestion');
  const q = input.value.trim();
  const chatBox = document.getElementById('chatBox');
  if (!q) return;

  addMsg(chatBox, q, 'user');
  input.value = '';
  const thinking = addMsg(chatBox, '…', 'bot');

  try {
    const res = await fetch('http://127.0.0.1:8000/rag/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    thinking.remove();
    addMsg(chatBox, data.answer, 'bot');
  } catch {
    thinking.remove();
    addMsg(chatBox, 'Error retrieving answer.', 'bot');
  }
}

function addMsg(box, text, role) {
  const d = document.createElement('div');
  d.className = 'msg ' + role;
  d.textContent = text;
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
  return d;
}

/* ─── TOAST ─── */
function toast(msg, type = 'info') {
  document.getElementById('_toast')?.remove();
  const el = document.createElement('div');
  el.id = '_toast';
  el.className = 'toast ' + (type === 'warn' ? 'warn' : type === 'error' ? 'error' : 'ok');
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 200);
  }, 3200);
}

document.addEventListener("DOMContentLoaded", function () {
  renderHistory();
});