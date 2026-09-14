const API_BASE_URL = window.DEBATE_JUDGE_API_URL || window.location.origin;
const examples = [
  { label: 'Urban transport', topic: 'Should cities restrict private cars in downtown areas?', a: 'Cities should restrict private cars downtown. Less traffic creates safer streets, cleaner air, and stronger local commerce. Congestion pricing shows demand can be managed while transit investment improves access.', b: 'Cities should not restrict private cars downtown. Small businesses rely on easy access for customers, and many workers cannot depend on public transit. Restrictions could unfairly burden families and outer suburbs.' },
  { label: 'Four-day week', topic: 'Should companies adopt a four-day work week?', a: 'A four-day week improves focus and retention. Pilot programs show productivity can hold steady when needless meetings are reduced.', b: 'A four-day week creates operational pressure for customer-facing teams and may fail businesses needing continuous coverage.' },
  { label: 'AI in schools', topic: 'Should students be allowed to use AI tools in school?', a: 'AI tools should be permitted with guidance because they give students immediate feedback and teach a core modern literacy.', b: 'AI tools should be restricted because they can obscure original thinking before students master foundational skills.' }
];
const SAMPLE_JUDGMENT = {
  motion: examples[0].topic,
  pull_quote: 'A policy case is strongest when it answers the costs it creates.',
  winner: 'A',
  overall_score: { a: 7.4, b: 6.0 },
  argument_profile: {
    logic: { a: 7.3, b: 6.7 },
    evidence: { a: 7.3, b: 5.7 },
    rebuttal: { a: 7.7, b: 5.7 }
  },
  claims: {
    a: [
      { claim: 'Car-light centers create safer, more usable public streets.', logic_score: 8, evidence_score: 7, rebuttal_score: 8, analysis: 'The causal chain is clear and responds to the access concern through public-space benefits. The evidence remains general rather than local.' },
      { claim: 'Congestion pricing has reduced traffic in comparable city centers.', logic_score: 7, evidence_score: 8, rebuttal_score: 7, analysis: 'Comparable-city precedent supports the policy mechanism. The argument would be stronger with attention to differences between those cities and the proposed setting.' },
      { claim: 'Exemptions and transit investment can limit the burden on workers.', logic_score: 7, evidence_score: 7, rebuttal_score: 8, analysis: 'This directly addresses Side B’s strongest equity objection, although evidence that the mitigation is sufficient is not fully developed.' }
    ],
    b: [
      { claim: 'Small businesses need nearby driving and parking access.', logic_score: 7, evidence_score: 5, rebuttal_score: 6, analysis: 'The concern is relevant, but it is asserted without local business data and only partially engages the case for car-light commerce.' },
      { claim: 'Restrictions burden people outside reliable transit networks.', logic_score: 7, evidence_score: 6, rebuttal_score: 6, analysis: 'This is Side B’s strongest fairness point, but it does not show why exemptions and transit investment cannot address the burden.' },
      { claim: 'Delivery and emergency access make a full restriction impractical.', logic_score: 6, evidence_score: 6, rebuttal_score: 5, analysis: 'The claim identifies an operational limitation but assumes a full restriction despite the availability of targeted exemptions.' }
    ]
  },
  final_verdict: 'Side A wins because its congestion-pricing precedent and worker-exemption proposal establish both a policy benefit and a response to Side B’s principal access objection. Side B identifies a real transit-access concern but does not explain why targeted exemptions and investment are inadequate.'
};
const app = document.querySelector('#app');
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[c]);
let apiConfiguration = { ready: false, model: '', allow_custom_provider: false };

function apiNotice() {
  return `<aside class="api-callout" role="note"><strong>Set up an API for live judgments.</strong><span>The sample result works without a key. To analyze your own debate, copy <code>backend/.env.example</code> to <code>backend/.env</code>, add <code>OPENAI_API_KEY</code>, then start the backend.</span></aside>`;
}

function inputScreen(draft = {}, error = '') {
  app.innerHTML = `${apiNotice()}<section class="page"><header class="hero"><div class="mark">±</div><p class="eyebrow">Argument intelligence</p><h1>Let the best case win.</h1><p>Paste two sides of a debate. Get a clear, claim-by-claim judgment in seconds.</p></header><section class="card input-card"><div class="api-row"><span id="api-status" class="api-status">Checking AI connection…</span><button id="api-setup" class="chip" type="button">API setup</button></div><div id="api-panel" class="api-panel" hidden><strong>Connect the AI judge</strong><p>Your API key stays on the backend, never in this browser. Copy <code>backend/.env.example</code> to <code>backend/.env</code>, set <code>OPENAI_API_KEY</code>, then restart the server.</p><p id="api-model" class="api-model"></p></div><label class="field-label">Debate topic <span class="optional">(optional)</span><input id="topic" class="topic" value="${escapeHtml(draft.topic)}" placeholder="e.g. Should cities restrict cars downtown?"></label><div class="sides"><label class="field-label">Side A<span class="hint">The proposition or first position</span><textarea id="side-a" placeholder="Paste this side's argument here...">${escapeHtml(draft.side_a)}</textarea></label><label class="field-label">Side B<span class="hint">The opposition or counter-position</span><textarea id="side-b" placeholder="Paste this side's argument here...">${escapeHtml(draft.side_b)}</textarea></label></div><p id="error" class="error ${error ? 'show' : ''}">${escapeHtml(error || 'Please fill in both sides before submitting.')}</p><div class="action-row"><div><p class="try-label">TRY AN EXAMPLE</p><div class="chips">${examples.map((item, index) => `<button class="chip" data-example="${index}">${item.label}</button>`).join('')}</div></div><button id="judge" class="primary" disabled>Judge this debate →</button></div></section><p class="footer-note">✦ Built for thoughtful disagreements, not hot takes.</p></section>`;
  const apiPanel = document.querySelector('#api-panel');
  apiPanel.querySelector('p:not(#api-model)').textContent = 'Choose the shared AI judge or configure a personal system for this judgment.';
  apiPanel.insertAdjacentHTML('beforeend', '<p class="api-important"><strong>Important:</strong> Add your API details below to use your own AI system. Otherwise, the app will use the shared AI judge when it is available.</p>');
  apiPanel.insertAdjacentHTML('beforeend', `<section class="provider-controls"><label class="field-label">AI system<select id="ai-system" class="provider-select"><option value="shared">Use the shared AI judge</option><option value="openai">Use my OpenAI API</option><option value="compatible">Use my compatible Responses API</option></select><span class="hint">The shared judge is used when you do not provide your own system.</span></label><div id="personal-provider" class="personal-provider" hidden><label class="field-label">Personal API key<input id="personal-api-key" class="topic" type="password" autocomplete="off" placeholder="Used only for this judgment"></label><label class="field-label">Model<input id="personal-model" class="topic" maxlength="120" placeholder="e.g. gpt-4.1-mini"></label><label id="base-url-field" class="field-label" hidden>Compatible API base URL<input id="personal-base-url" class="topic" type="url" placeholder="https://your-provider.example/v1"></label><p class="provider-note">Your key is sent only to this backend request and is not saved by the app.</p></div></section>`);
  const sideA = document.querySelector('#side-a'), sideB = document.querySelector('#side-b'), button = document.querySelector('#judge');
  const validate = () => { button.disabled = sideA.value.trim().length < 20 || sideB.value.trim().length < 20; };
  sideA.oninput = sideB.oninput = validate;
  document.querySelectorAll('[data-example]').forEach(exampleButton => exampleButton.onclick = () => { const example = examples[exampleButton.dataset.example]; document.querySelector('#topic').value = example.topic; sideA.value = example.a; sideB.value = example.b; validate(); });
  document.querySelector('#api-setup').onclick = () => { const panel = document.querySelector('#api-panel'); panel.hidden = !panel.hidden; };
  document.querySelector('#ai-system').onchange = syncProviderControls;
  syncProviderControls();
  button.onclick = () => {
    try { loading({ topic: document.querySelector('#topic').value.trim(), side_a: sideA.value.trim(), side_b: sideB.value.trim(), provider: selectedProvider() }); }
    catch (providerError) { document.querySelector('#error').textContent = providerError.message; document.querySelector('#error').classList.add('show'); }
  };
  validate();
  refreshApiStatus();
}

function syncProviderControls() {
  const system = document.querySelector('#ai-system'), personal = document.querySelector('#personal-provider'), baseUrl = document.querySelector('#base-url-field');
  if (!system || !personal || !baseUrl) return;
  const personalSystem = system.value !== 'shared';
  personal.hidden = !personalSystem;
  baseUrl.hidden = system.value !== 'compatible';
  [...system.options].filter(option => option.value !== 'shared').forEach(option => option.disabled = !apiConfiguration.allow_custom_provider);
  if (!apiConfiguration.allow_custom_provider && personalSystem) { system.value = 'shared'; personal.hidden = true; }
}

function selectedProvider() {
  const system = document.querySelector('#ai-system').value;
  if (system === 'shared') return { mode: 'shared' };
  if (!apiConfiguration.allow_custom_provider) throw new Error('Personal AI systems are disabled by this server.');
  const apiKey = document.querySelector('#personal-api-key').value.trim(), model = document.querySelector('#personal-model').value.trim(), baseUrl = document.querySelector('#personal-base-url').value.trim();
  if (!apiKey || !model) throw new Error('Enter your personal API key and model before judging.');
  if (system === 'compatible' && !baseUrl) throw new Error('Enter a compatible API base URL before judging.');
  return { mode: 'custom', system, api_key: apiKey, model, base_url: system === 'compatible' ? baseUrl : null };
}

async function refreshApiStatus() {
  const status = document.querySelector('#api-status'), model = document.querySelector('#api-model');
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/configuration`);
    if (!response.ok) throw new Error();
    const configuration = await response.json(); apiConfiguration = configuration;
    status.textContent = configuration.ready ? `Shared AI connected · ${configuration.model}` : 'Shared AI key needed';
    status.classList.toggle('ready', configuration.ready);
    model.textContent = `Configured model: ${configuration.model}`;
    syncProviderControls();
  } catch { status.textContent = 'Backend unavailable'; }
}

async function loading(debate) {
  const labels = ['Extracting claims...', 'Scoring arguments...', 'Testing rebuttals...', 'Reaching a verdict...']; let step = 0;
  app.innerHTML = `<section class="page loading"><div><div class="spinner"></div><p id="status">${labels[0]}</p><small>Reading both sides with care</small></div></section>`;
  const clock = setInterval(() => { step = (step + 1) % labels.length; document.querySelector('#status').textContent = labels[step]; }, 750);
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/judgments`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(debate) });
    const body = await responseJson(response);
    if (!response.ok) throw new Error(body.detail || 'The judge could not analyze this debate.');
    dashboard(body);
  } catch (error) { inputScreen(debate, error.message || 'Unable to connect to the judging service.'); }
  finally { clearInterval(clock); }
}

async function responseJson(response) {
  const responseText = await response.text();
  if (!responseText.trim()) return {};
  try { return JSON.parse(responseText); }
  catch { throw new Error('The judging service returned an invalid response. Confirm the backend is running and your API is configured.'); }
}

function polygon(values) { const cx = 150, cy = 130, radius = 88; return values.map((value, index) => { const angle = (-90 + index * 120) * Math.PI / 180, scaled = radius * value / 10; return `${cx + Math.cos(angle) * scaled},${cy + Math.sin(angle) * scaled}`; }).join(' '); }
function claimColumn(name, side) { return `<div><div class="column-title"><h3>${name}</h3><span class="pill">${side.overall.toFixed(1)} overall</span></div>${side.items.map((claim, index) => `<article class="card claim"><button class="claim-toggle"><span class="number">${index + 1}</span><span class="claim-text">${escapeHtml(claim.claim)}</span><span class="arrow">⌄</span></button><div class="details"><div class="metrics">${[['Logic', claim.logic_score], ['Evidence', claim.evidence_score], ['Rebuttal', claim.rebuttal_score]].map(([label, score]) => `<div class="metric"><small>${label}</small><strong class="count" data-target="${score}">0.0</strong></div>`).join('')}</div><p class="note">✦ ${escapeHtml(claim.analysis)}</p></div></article>`).join('')}</div>`; }

function dashboard(result, isSample = false) {
  const profile = result.argument_profile, a = { overall: result.overall_score.a, items: result.claims.a }, b = { overall: result.overall_score.b, items: result.claims.b }, winner = result.winner === 'A' ? 'Side A' : 'Side B';
  const label = isSample ? 'SAMPLE VERDICT' : 'JUDGMENT DELIVERED';
  const summary = isSample ? 'A precomputed example—submit a new debate for a live AI judgment.' : 'A clearer case on balance of argument.';
  app.innerHTML = `${apiNotice()}<section class="page"><header class="topbar"><div class="brand"><i>±</i> AI Debate Judge</div><button class="ghost" id="reset">← New debate</button></header><section class="card banner"><div class="banner-left"><div class="icon-box">⚖</div><div><span class="badge">${label}</span><h1>${winner} wins</h1><p class="sub">${summary}</p></div></div><div class="score"><small>OVERALL SCORE</small><strong>${a.overall.toFixed(1)} <span>vs</span> ${b.overall.toFixed(1)}</strong></div></section><section class="overview"><article class="card pad"><p class="eyebrow">Argument profile</p><h2 class="section-title">How the cases compare</h2><svg class="chart" viewBox="0 0 300 270"><g transform="translate(0,5)" fill="none" stroke="#dbe3dc"><polygon points="150,42 226,174 74,174"/><polygon points="150,64 207,163 93,163"/><polygon points="150,86 188,152 112,152"/></g><g transform="translate(0,5)" font-family="DM Sans" font-size="11" font-weight="700" fill="#69736b"><text x="132" y="18">Logic</text><text x="237" y="190">Evidence</text><text x="21" y="190">Rebuttal</text></g><polygon transform="translate(0,5)" points="${polygon([profile.logic.a, profile.evidence.a, profile.rebuttal.a])}" fill="#3a5c4738" stroke="#3a5c47" stroke-width="2"/><polygon transform="translate(0,5)" points="${polygon([profile.logic.b, profile.evidence.b, profile.rebuttal.b])}" fill="#9aa69d25" stroke="#9aa69d" stroke-width="2"/></svg><div class="legend"><span><i class="dot"></i>Side A</span><span><i class="dot gray"></i>Side B</span></div></article><article class="card pad"><p class="eyebrow">The motion</p><h2 class="section-title">${escapeHtml(result.motion)}</h2><p class="ruling-quote">“${escapeHtml(result.pull_quote)}”</p><p class="sub">Explore each claim below to see how the ruling was reached.</p></article></section><section class="claims-header"><p class="eyebrow">Claim analysis</p><h2 class="section-title">Evidence, logic & response</h2><div class="claims">${claimColumn('Side A', a)}${claimColumn('Side B', b)}</div></section><section class="final"><p class="eyebrow">Final verdict</p><p>${escapeHtml(result.final_verdict)}</p></section><button class="primary again" id="again">Judge another debate →</button></section>`;
  document.querySelectorAll('.claim-toggle').forEach(button => button.onclick = () => { const card = button.closest('.claim'); card.classList.toggle('open'); if (card.classList.contains('open')) card.querySelectorAll('.count').forEach(countUp); });
  document.querySelector('#reset').onclick = document.querySelector('#again').onclick = () => inputScreen();
}
function countUp(element) { const target = Number(element.dataset.target), start = performance.now(), duration = 650; function frame(now) { const progress = Math.min((now - start) / duration, 1); element.textContent = (target * (1 - Math.pow(1 - progress, 3))).toFixed(1); if (progress < 1) requestAnimationFrame(frame); } requestAnimationFrame(frame); }
inputScreen();
