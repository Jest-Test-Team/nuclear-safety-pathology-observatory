const API = window.NSPO_API || 'http://localhost:8080';

async function load() {
  const container = document.querySelector('#findings');
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
      for (const item of finding.alternative_explanations) {
        const li = document.createElement('li'); li.textContent = item; node.querySelector('.alternatives').append(li);
      }
      for (const item of finding.limitations) {
        const li = document.createElement('li'); li.textContent = item; node.querySelector('.limitations').append(li);
      }
      node.querySelector('.uncertainty').textContent = `Uncertainty: ${finding.uncertainty}`;
      container.append(node);
    }
  } catch (error) {
    container.textContent = `Unable to load findings: ${error.message}`;
  }
}
load();
