const report = document.querySelector("#report");
const error = document.querySelector("#error");
const results = document.querySelector("#results");
const emptyState = document.querySelector("#empty-state");
const analyseButton = document.querySelector("#analyse");
const sampleButton = document.querySelector("#sample");
const count = document.querySelector("#report-count");

const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, character =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[character]));

function updateCount() {
  count.textContent = `${report.value.length.toLocaleString()} / 20,000 characters`;
}

function setStage(stage, state, message) {
  const element = document.querySelector(`#stage-${stage}`);
  element.className = state;
  element.querySelector("small").textContent = message;
}

function resetStages() {
  setStage("source", "current", report.value.trim() ? "Ready to analyse" : "Ready for input");
  setStage("evidence", "", "Awaiting analysis");
  setStage("rules", "", "Awaiting analysis");
  setStage("events", "", "Awaiting analysis");
}

function setLoading(isLoading) {
  analyseButton.disabled = isLoading;
  sampleButton.disabled = isLoading;
  analyseButton.innerHTML = isLoading ? "Analysing…" : 'Analyse report <span aria-hidden="true">↵</span>';
  if (isLoading) {
    setStage("source", "complete", "Submitted");
    setStage("evidence", "current", "Extracting passages");
    setStage("rules", "", "Awaiting analysis");
    setStage("events", "", "Awaiting analysis");
  }
}

function showError(message) {
  error.textContent = message;
  results.hidden = true;
  emptyState.hidden = false;
}

function yamlMarkup(yaml) {
  return escapeHtml(yaml)
    .replace(/^([\w-]+)(:)/gm, '<span class="key">$1</span>$2')
    .replace(/(&quot;.*?&quot;)/g, '<span class="string">$1</span>');
}

async function loadSample() {
  error.textContent = "";
  sampleButton.disabled = true;
  try {
    const response = await fetch("/api/sample-report");
    if (!response.ok) throw new Error("The sample report could not be loaded.");
    const data = await response.json();
    report.value = data.report;
    updateCount();
    resetStages();
    report.focus();
  } catch (requestError) {
    showError(requestError.message || "Could not load the sample report.");
  } finally {
    sampleButton.disabled = false;
  }
}

async function requestAnalysis() {
  error.textContent = "";
  if (!report.value.trim()) {
    showError("Enter a threat intelligence report before starting analysis.");
    report.focus();
    return;
  }
  setLoading(true);
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({report: report.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Analysis failed.");
    let events = [];
    try {
      const eventResponse = await fetch("/api/sample-events");
      if (!eventResponse.ok) throw new Error();
      events = await eventResponse.json();
    } catch {
      error.textContent = "Analysis completed, but synthetic event details could not be loaded.";
    }
    render(data, events);
  } catch (requestError) {
    showError(requestError.message || "The analysis request failed.");
    setStage("source", "current", "Ready to retry");
    setStage("evidence", "warning", "Analysis failed");
    setStage("rules", "", "Awaiting analysis");
    setStage("events", "", "Awaiting analysis");
  } finally {
    setLoading(false);
  }
}

function render(data, events) {
  const evidenceComplete = data.extracted_evidence.length > 0;
  setStage("evidence", evidenceComplete ? "complete" : "warning", evidenceComplete ? `${data.extracted_evidence.length} passage(s) found` : "No passages found");
  setStage("rules", "complete", `${data.summary.candidate_rules} candidates generated`);
  const matchedCount = data.rules.reduce((total, item) => total + item.suspicious_event_ids.length + item.benign_event_ids.length, 0);
  setStage("events", matchedCount ? "complete" : "warning", matchedCount ? `${matchedCount} sample match(es)` : "No sample matches");
  results.hidden = false;
  emptyState.hidden = true;
  renderSummary(data.summary);
  renderEvidence(data.extracted_evidence);
  renderRules(data.rules);
  renderEvents(data.rules, events);
  results.scrollIntoView({behavior: "smooth", block: "start"});
}

function renderSummary(summary) {
  const stats = [
    [summary.candidate_rules, "Candidates"],
    [summary.structurally_valid, "Schema valid"],
    [summary.evidence_supported, "Evidence supported"],
    [summary.rules_with_benign_matches, "Benign warnings"]
  ];
  document.querySelector("#summary-stats").innerHTML = stats.map(([value, label]) =>
    `<div class="summary-stat"><b>${escapeHtml(value)}</b><span>${escapeHtml(label)}</span></div>`).join("");
}

function renderEvidence(evidence) {
  const target = document.querySelector("#evidence-list");
  if (!evidence.length) {
    target.innerHTML = '<p class="no-result">No passages matched the two explicit baseline patterns. Candidate rules remain visible, but are marked unsupported.</p>';
    return;
  }
  target.innerHTML = evidence.map(item =>
    `<article class="evidence-item"><p class="evidence-ref">${escapeHtml(item.reference)}</p><blockquote>${escapeHtml(item.excerpt)}</blockquote></article>`).join("");
}

function renderRules(rules) {
  document.querySelector("#rule-list").innerHTML = rules.map((item, index) => {
    const matchCount = item.suspicious_event_ids.length + item.benign_event_ids.length;
    const evidenceText = item.rule.evidence_refs.length
      ? item.rule.evidence_refs.map(ref => `<p><span class="mono">${escapeHtml(ref.reference)}</span> — ${escapeHtml(ref.excerpt)}</p>`).join("")
      : `<p>${escapeHtml(item.unsupported_reason || "No supporting passage was found.")}</p>`;
    const errors = item.validation_errors.length
      ? `<p class="rule-error">${escapeHtml(item.validation_errors.join("; "))}</p>` : "";
    const warning = item.false_positive_warning
      ? `<p class="rule-warning">${escapeHtml(item.false_positive_warning)}. This is a synthetic benign-match warning, not a measured false-positive rate.</p>` : "";
    return `<article class="rule" id="rule-${index}">
      <header class="rule-header"><div><p class="rule-id">${escapeHtml(item.rule.id)}</p><h3>${escapeHtml(item.rule.title)}</h3></div>
      <div class="rule-status"><span class="status">Candidate</span><span class="status ${item.structural_valid ? "good" : "bad"}">Schema ${item.structural_valid ? "valid" : "invalid"}</span><span class="status ${item.evidence_supported ? "good" : "warn"}">Evidence ${item.evidence_supported ? "supported" : "missing"}</span></div></header>
      <div class="rule-body"><div class="rule-detail"><p class="rule-description">${escapeHtml(item.rule.description)}</p>
        <div class="match-grid"><div><span>Sample matches</span><b>${matchCount}</b></div><div><span>Suspicious / benign</span><b>${item.suspicious_event_ids.length} / ${item.benign_event_ids.length}</b></div></div>
        ${warning}${errors}<details><summary>Supporting evidence</summary>${evidenceText}</details></div>
        <div class="yaml-pane"><span class="yaml-label">CUSTOM RULE YAML</span><button class="button button-quiet copy-button" type="button" data-copy="${index}">Copy YAML</button><pre class="yaml"><code>${yamlMarkup(item.yaml)}</code></pre></div>
      </div></article>`;
  }).join("");
  document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click", () => copyYaml(rules[Number(button.dataset.copy)].yaml, button)));
}

async function copyYaml(yaml, button) {
  try {
    await navigator.clipboard.writeText(yaml);
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = original; }, 1300);
  } catch {
    button.textContent = "Copy unavailable";
  }
}

function renderEvents(rules, events) {
  const classifications = new Map();
  rules.forEach(rule => {
    rule.suspicious_event_ids.forEach(id => classifications.set(id, "suspicious"));
    rule.benign_event_ids.forEach(id => classifications.set(id, "benign"));
  });
  const matched = events.filter(event => classifications.has(event.event_id));
  document.querySelector("#event-empty").hidden = Boolean(matched.length);
  document.querySelector("#event-rows").innerHTML = matched.map(event => {
    const classification = classifications.get(event.event_id);
    const relevant = `host: ${event.host}\nuser: ${event.user}\nprocess: ${event.process_name}\ncommand: ${event.command_line}`;
    return `<tr><td class="event-mono">${escapeHtml(event.event_id)}</td><td class="event-mono">${escapeHtml(event.timestamp)}</td><td>${escapeHtml(event.event_type)}</td><td class="event-fields">${escapeHtml(relevant)}</td><td><span class="classification ${classification}">${escapeHtml(classification)} sample match</span></td></tr>`;
  }).join("");
}

report.addEventListener("input", () => { updateCount(); resetStages(); });
report.addEventListener("keydown", event => { if ((event.ctrlKey || event.metaKey) && event.key === "Enter") requestAnalysis(); });
sampleButton.addEventListener("click", loadSample);
analyseButton.addEventListener("click", requestAnalysis);
document.querySelectorAll(".nav-link").forEach(link => link.addEventListener("click", () => {
  document.querySelectorAll(".nav-link").forEach(item => item.classList.remove("active"));
  link.classList.add("active");
}));
updateCount();
resetStages();
