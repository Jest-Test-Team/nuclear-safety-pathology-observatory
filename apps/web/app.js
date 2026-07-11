const API = window.NSPO_API || 'http://localhost:8080';

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

async function loadFindings() {
  const container = document.querySelector('#findings');
  const select = document.querySelector('#finding-id');
  container.replaceChildren();
  select.replaceChildren();
  try {
    const response = await fetch(`${API}/api/findings`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const findings = await response.json();
    document.querySelector('#count').textContent = findings.length;
    const template = document.querySelector('#card-template');
    for (const finding of findings) {
      const node = template.content.cloneNode(true);
      node.querySelector('.rule').textContent = finding.rule_id;
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
loadFindings();
