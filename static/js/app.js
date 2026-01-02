function $(id) {
  return document.getElementById(id);
}

function setText(id, value) {
  const el = $(id);
  if (!el) return;
  el.textContent = value;
}

function setHidden(id, hidden) {
  const el = $(id);
  if (!el) return;
  el.hidden = hidden;
}

function setBadge(el, text, kind) {
  if (!el) return;
  el.textContent = text || '';
  el.classList.remove('badge-ok', 'badge-warn', 'badge-error');
  if (kind) el.classList.add(kind);
}

async function analyzeText(text) {
  const response = await fetch('/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.message || payload.error || 'Erreur lors de la requête.';
    const err = new Error(message);
    err.payload = payload;
    err.status = response.status;
    throw err;
  }
  return payload;
}

function renderResult(data) {
  setHidden('result', false);
  setHidden('error', true);

  setText('summary', data.summary || '');
  setText('sentiment', data.label || data.sentiment_fr || data.sentiment || '');
  setText('score', data.score_percent || String(data.score ?? ''));

  const confidence = data.confidence;
  if (typeof confidence === 'number') {
    setText('confidence', `${Math.round(confidence * 100)}%`);
  } else {
    setText('confidence', '');
  }

  const modeEl = $('mode');
  const mode = data.mode ? `Mode: ${data.mode}` : '';
  const isDemo = data.mode === 'demo' || data.demo === true;
  setBadge(modeEl, mode, isDemo ? 'badge-warn' : 'badge-ok');

  const resultEl = $('result');
  if (resultEl) {
    resultEl.classList.remove(
      'sentiment-positive',
      'sentiment-negative',
      'sentiment-neutral',
      'sentiment-error'
    );
    if (data.css_class) resultEl.classList.add(data.css_class);
  }
}

function renderError(err) {
  setHidden('result', false);
  const errorEl = $('error');
  if (errorEl) {
    errorEl.textContent = err && err.message ? err.message : 'Erreur inconnue.';
  }
  setHidden('error', false);
}

function setLoading(isLoading) {
  const btn = $('analyze-btn');
  if (!btn) return;
  btn.disabled = isLoading;
  btn.textContent = isLoading ? 'Analyse...' : 'Analyser';
}

document.addEventListener('DOMContentLoaded', () => {
  const form = $('analyze-form');
  const clearBtn = $('clear-btn');
  const textEl = $('text');

  if (clearBtn && textEl) {
    clearBtn.addEventListener('click', () => {
      textEl.value = '';
      setHidden('result', true);
    });
  }

  if (!form || !textEl) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = (textEl.value || '').trim();
    setLoading(true);
    try {
      const data = await analyzeText(text);
      renderResult(data);
    } catch (err) {
      renderError(err);
    } finally {
      setLoading(false);
    }
  });
});
