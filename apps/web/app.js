const API = (typeof window.NSPO_API === 'string') ? window.NSPO_API : 'http://localhost:8080';

let labels = null;
let findingsCache = [];

function currentLocale() {
  return document.querySelector('#locale').value || 'en';
}

function t(path, fallback = '') {
  if (!labels) return fallback;
  const parts = path.split('.');
  let cursor = labels.strings;
  for (const part of parts) {
    if (!cursor || typeof cursor !== 'object') return fallback;
    cursor = cursor[part];
  }
  if (cursor && typeof cursor === 'object') {
    return cursor[currentLocale()] || cursor.en || fallback;
  }
  return fallback;
}

function fillList(node, selector, values) {
  const list = node.querySelector(selector);
  list.replaceChildren();
  const items = Array.isArray(values) ? values : [];
  if (!items.length) {
    const li = document.createElement('li');
    li.textContent = 'None listed';
    list.append(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = item;
    list.append(li);
  }
}

function renderFindings(findings) {
  const container = document.querySelector('#findings');
  const select = document.querySelector('#finding-id');
  container.replaceChildren();
  select.replaceChildren();
  document.querySelector('#count').textContent = findings.length;
  document.querySelector('#disclaimer').textContent = t('disclaimer', document.querySelector('#disclaimer').textContent);
  const template = document.querySelector('#card-template');
  for (const finding of findings) {
    const node = template.content.cloneNode(true);
    node.querySelector('.rule').textContent = finding.rule_id;
    node.querySelector('.rule-label').textContent = t(`rules.${finding.rule_id}`, '');
    node.querySelector('.status').textContent = finding.status;
    node.querySelector('.scope').textContent = JSON.stringify(finding.scope, null, 2);
    fillList(node, '.evidence', finding.supporting_evidence);
    fillList(node, '.missing', finding.missing_evidence);
    fillList(node, '.alternatives', finding.alternative_explanations);
    fillList(node, '.limitations', finding.limitations);
    node.querySelector('.uncertainty').textContent = `Uncertainty: ${finding.uncertainty}`;
    container.append(node);

    const option = document.createElement('option');
    option.value = finding.finding_id;
    option.textContent = `${finding.rule_id} · ${finding.finding_id}`;
    select.append(option);
  }
  if (!findings.length) {
    container.textContent = 'No review candidates available.';
  }
}

async function loadLabels() {
  const response = await fetch('labels.json');
  if (!response.ok) throw new Error(`labels HTTP ${response.status}`);
  labels = await response.json();
  const saved = localStorage.getItem('nspo-locale');
  if (saved && labels.locales.includes(saved)) {
    document.querySelector('#locale').value = saved;
  }
}

async function loadFindings() {
  const container = document.querySelector('#findings');
  try {
    const response = await fetch(`${API}/api/findings`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    findingsCache = await response.json();
    renderFindings(findingsCache);
  } catch (error) {
    container.textContent = `Unable to load findings: ${error.message}`;
  }
}

async function submitReview(event) {
  event.preventDefault();
  const status = document.querySelector('#review-status');
  status.textContent = 'Submitting…';
  const payload = {
    finding_id: document.querySelector('#finding-id').value,
    decision: document.querySelector('#decision').value,
    reviewer: document.querySelector('#reviewer').value.trim(),
    comment: document.querySelector('#comment').value.trim(),
  };
  try {
    const response = await fetch(`${API}/api/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const body = await response.text();
    if (!response.ok) throw new Error(body || `HTTP ${response.status}`);
    status.textContent = `Review recorded for ${payload.finding_id} (${payload.decision}).`;
    document.querySelector('#comment').value = '';
  } catch (error) {
    status.textContent = `Review failed: ${error.message}`;
  }
}

document.querySelector('#review-form').addEventListener('submit', submitReview);
document.querySelector('#locale').addEventListener('change', () => {
  localStorage.setItem('nspo-locale', currentLocale());
  renderFindings(findingsCache);
});

(async function boot() {
  try {
    await loadLabels();
  } catch (error) {
    console.warn('labels unavailable', error);
  }
  await loadFindings();
})();
