// autopsy.js — RAG-Powered Autopsy Intelligence Module

// ─── INIT MODULE ───────────────────────────────────────────────────────────
async function loadAutopsyModule() {
    try {
        const resp = await fetch('/api/autopsy/summary');
        const data = await resp.json();
        renderAutopsySummary(data);
        loadReportText();
    } catch(e) {
        console.error('Autopsy module load error:', e);
    }
}

// ─── SUMMARY CARDS ─────────────────────────────────────────────────────────
function renderAutopsySummary(data) {
    document.getElementById('autopsyReportTitle').textContent = data.title || 'Report';
    document.getElementById('autopsyChunkCount').textContent  = `${data.chunk_count || 0} chunks indexed`;

    const s = data.summary || {};

    document.getElementById('sumCause').textContent   = truncate(s.cause_of_death  || 'Not detected', 160);
    document.getElementById('sumTOD').textContent     = truncate(s.time_of_death   || 'Not detected', 160);
    document.getElementById('sumTox').textContent     = truncate(s.toxicology      || 'Not detected', 160);

    const findings = s.key_findings || [];
    document.getElementById('sumFindings').innerHTML = findings.length
        ? findings.map(f => `<div style="display:flex;gap:6px;margin-bottom:4px;"><span style="color:#3fb950;">✓</span><span>${f}</span></div>`).join('')
        : '<span style="color:#8b949e;">None flagged</span>';

    // Key findings panel (right column)
    document.getElementById('autopsyKeyFindings').innerHTML = findings.length
        ? findings.map(f => `
            <div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #21262d;">
                <span style="color:#3fb950;font-size:1.1rem;">✓</span>
                <span style="color:#e6edf3;font-size:0.85rem;">${f}</span>
            </div>`).join('')
        : '<p style="color:#8b949e;">No key findings extracted.</p>';
}

// ─── REPORT TEXT ───────────────────────────────────────────────────────────
async function loadReportText() {
    const resp = await fetch('/api/autopsy/report_text');
    const { text } = await resp.json();
    document.getElementById('autopsyReportText').textContent = text || 'No report text available.';
}

// ─── AI CHAT Q&A ───────────────────────────────────────────────────────────
async function askAutopsy() {
    const input = document.getElementById('autopsyQuestion');
    const question = input.value.trim();
    if (!question) return;

    appendChatMessage('investigator', question);
    input.value = '';

    // Typing indicator
    const thinkingId = `think_${Date.now()}`;
    appendChatMessage('ai', '<i class="fa-solid fa-spinner fa-spin"></i> Retrieving from report...', thinkingId);
    document.getElementById('autopsyAIBadge').textContent = 'RETRIEVING...';

    try {
        const resp = await fetch('/api/autopsy/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });
        const data = await resp.json();

        // Remove thinking bubble
        const el = document.getElementById(thinkingId);
        if (el) el.remove();

        appendChatMessage('ai', data.answer || 'No answer retrieved.');
        renderSources(data.sources || []);
        document.getElementById('autopsyAIBadge').textContent = 'RAG READY';
    } catch(e) {
        document.getElementById(thinkingId)?.remove();
        appendChatMessage('ai', '⚠ Server error. Is the server running?');
    }
}

function quickAsk(question) {
    document.getElementById('autopsyQuestion').value = question;
    askAutopsy();
}

function appendChatMessage(role, text, id) {
    const box    = document.getElementById('autopsyChatBox');
    const isUser = role === 'investigator';
    const div    = document.createElement('div');
    if (id) div.id = id;
    div.style.cssText = `
        padding: 12px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        line-height: 1.6;
        max-width: 85%;
        ${isUser
            ? 'align-self:flex-end;background:rgba(88,166,255,0.15);border:1px solid rgba(88,166,255,0.3);color:#e6edf3;'
            : 'align-self:flex-start;background:#161b22;border:1px solid #30363d;color:#ccc;border-left:3px solid #bc8cff;'}
    `;
    div.innerHTML = isUser
        ? `<span style="color:#8b949e;font-size:0.75rem;margin-bottom:6px;display:inline-block;font-weight:600;">INVESTIGATOR</span><br>${text}`
        : `<span style="color:#bc8cff;font-size:0.75rem;margin-bottom:6px;display:inline-block;font-weight:600;"><i class="fa-solid fa-brain"></i> RAG ENGINE</span><br>${text}`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

// ─── SOURCE REFERENCES ─────────────────────────────────────────────────────
function renderSources(sources) {
    const el = document.getElementById('autopsySources');
    if (!sources.length) {
        el.innerHTML = '<p style="color:#8b949e;">No sources retrieved.</p>';
        return;
    }
    el.innerHTML = sources.map((s, i) => `
        <div style="margin-bottom:12px;padding:10px;background:#0d1117;border-radius:6px;border-left:2px solid ${i===0?'#bc8cff':'#30363d'};">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:${i===0?'#bc8cff':'#58a6ff'};font-size:0.7rem;font-weight:600;">${s.section}</span>
                <span style="color:#3fb950;font-size:0.7rem;">${s.confidence}% match</span>
            </div>
            <div style="color:#8b949e;font-size:0.75rem;line-height:1.5;">${s.text}</div>
        </div>
    `).join('');
}

// ─── FILE UPLOAD ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('autopsyUploadInput');
    if (!input) return;
    input.addEventListener('change', async function() {
        if (!this.files.length) return;
        const formData = new FormData();
        formData.append('file', this.files[0]);

        const loadingEl = document.getElementById('autopsyLoading');
        const loadingText = document.getElementById('autopsyLoadingText');
        loadingEl.style.display = 'block';
        loadingText.textContent = `Extracting & indexing "${this.files[0].name}"...`;

        try {
            const resp = await fetch('/api/autopsy/upload', { method: 'POST', body: formData });
            if (resp.ok) {
                const data = await resp.json();
                renderAutopsySummary({ title: data.title, chunk_count: data.chunks, summary: data.summary });
                loadReportText();
                // Reset chat
                document.getElementById('autopsyChatBox').innerHTML = `
                    <div style="background:rgba(63,185,80,0.1);border-left:3px solid #3fb950;padding:10px 12px;border-radius:6px;font-size:0.82rem;color:#3fb950;">
                        ✓ Report indexed (${data.chunks} chunks). You can now ask questions.
                    </div>`;
                document.getElementById('autopsySources').innerHTML = '<p style="color:#8b949e;">Ask a question to see retrieved sections.</p>';
            } else {
                alert('Error processing report. Check the file format.');
            }
        } catch(e) {
            alert('Server error. Is the server running?');
        } finally {
            loadingEl.style.display = 'none';
            this.value = '';
        }
    });
});

// ─── RESET ──────────────────────────────────────────────────────────────────
async function resetAutopsy() {
    await fetch('/api/autopsy/reset', { method: 'POST' });
    await loadAutopsyModule();
    document.getElementById('autopsyChatBox').innerHTML = `
        <div style="background:rgba(88,166,255,0.08);border-left:3px solid #58a6ff;padding:10px 12px;border-radius:6px;font-size:0.82rem;color:#8b949e;">
            Demo report reloaded. Ask any question about the autopsy.
        </div>`;
    document.getElementById('autopsySources').innerHTML = '<p style="color:#8b949e;">Ask a question to see retrieved sections.</p>';
}

// ─── AUTO-INIT ON VIEW SWITCH ──────────────────────────────────────────────
const _origSwitchView3 = window.switchView;
window.switchView = function(viewId) {
    _origSwitchView3 && _origSwitchView3(viewId);
    if (viewId === 'autopsy') setTimeout(loadAutopsyModule, 150);
};

// ─── UTILITIES ────────────────────────────────────────────────────────────
function truncate(text, maxLen) {
    return text && text.length > maxLen ? text.slice(0, maxLen) + '...' : (text || '—');
}
