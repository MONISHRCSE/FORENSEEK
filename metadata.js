// metadata.js  — Metadata Intelligence Module

let metaMap = null;

// ─── LOAD ALL METADATA PANELS ──────────────────────────────────────────────
async function loadMetadataModule() {
    await Promise.all([
        loadRiskScores(),
        loadMetaTimeline(),
        loadCallLogs(),
        loadSMS(),
        loadInsights(),
        loadMetaContradictions(),
    ]);
    initMetaMap();
}

// ─── RISK SCORES ───────────────────────────────────────────────────────────
async function loadRiskScores() {
    const resp = await fetch('/api/metadata/risk_scores');
    const { scores } = await resp.json();

    setScore('scoreMovement',    'barMovement',    scores.movement_anomaly,     '#f85149');
    setScore('scoreComm',        'barComm',        scores.communication_risk,   '#d29922');
    setScore('scoreSMS',         'barSMS',         scores.sms_content_risk,     '#bc8cff');
    setScore('scoreConsistency', 'barConsistency', scores.metadata_consistency, '#3fb950');
}
function setScore(scoreId, barId, val, color) {
    document.getElementById(scoreId).textContent = val + '%';
    setTimeout(() => document.getElementById(barId).style.width = val + '%', 100);
}

// ─── CORRELATED TIMELINE ───────────────────────────────────────────────────
async function loadMetaTimeline() {
    const resp = await fetch('/api/metadata/timeline');
    const { timeline } = await resp.json();
    const el = document.getElementById('metaTimeline');
    if (!timeline.length) { el.innerHTML = '<p>No timeline data.</p>'; return; }

    const colorMap = { call: '#58a6ff', sms: '#bc8cff', gps: '#3fb950', app: '#d29922' };
    el.innerHTML = timeline.map(ev => `
        <div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid #21262d;">
            <div style="min-width:48px;color:${colorMap[ev.type]||'#ccc'};font-weight:600;font-size:0.78rem;">${ev.time}</div>
            <div style="font-size:0.78rem;">
                <span style="margin-right:4px;">${ev.icon}</span>
                <span style="color:#e6edf3;">${ev.label}</span>
            </div>
        </div>
    `).join('');
}

// ─── CALL LOGS ─────────────────────────────────────────────────────────────
async function loadCallLogs() {
    const resp = await fetch('/api/metadata/calls');
    const { calls } = await resp.json();
    const table = document.getElementById('callTable');
    // Remove old rows
    while (table.rows.length > 1) table.deleteRow(1);

    const typeColor = { outgoing: '#58a6ff', incoming: '#3fb950', missed: '#f85149' };
    calls.forEach(c => {
        const row = table.insertRow();
        row.innerHTML = `
            <td style="padding:5px 6px;color:#e6edf3;">${c.time}</td>
            <td style="padding:5px 6px;color:${typeColor[c.type]||'#ccc'};">${(c.type||'').toUpperCase()}</td>
            <td style="padding:5px 6px;color:#8b949e;font-size:0.72rem;">${c.number||''}</td>
            <td style="padding:5px 6px;color:#8b949e;">${c.duration||0}s</td>
        `;
        // Flag repeated/unknown contacts
        if ((c.contact||'').toLowerCase() === 'unknown') row.style.background = 'rgba(248,81,73,0.05)';
    });
}

// ─── SMS INTELLIGENCE ──────────────────────────────────────────────────────
const RISKY_KEYWORDS = ['warehouse', 'meet', 'done', "don't call", 'heading out', 'hide'];
async function loadSMS() {
    const resp = await fetch('/api/metadata/sms');
    const { sms } = await resp.json();
    const el = document.getElementById('smsList');
    if (!sms.length) { el.innerHTML = '<p style="color:#8b949e;">No SMS data.</p>'; return; }

    el.innerHTML = sms.map(s => {
        const dir   = (s.direction || s.dir || '');
        const text  = s.text || s.message || '';
        const risky = RISKY_KEYWORDS.some(kw => text.toLowerCase().includes(kw));
        const highlighted = risky
            ? text.replace(new RegExp(`(${RISKY_KEYWORDS.join('|')})`, 'gi'),
                           '<mark style="background:rgba(248,81,73,0.25);color:#f85149;border-radius:2px;">$1</mark>')
            : text;
        return `
            <div style="padding:7px 0;border-bottom:1px solid #21262d;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="color:${dir==='sent'?'#58a6ff':'#3fb950'};font-size:0.72rem;font-weight:600;">${dir.toUpperCase()}</span>
                    <span style="color:#8b949e;font-size:0.72rem;">${s.time}</span>
                </div>
                <div style="color:#e6edf3;font-size:0.79rem;line-height:1.5;">${highlighted}</div>
                ${risky ? '<div style="color:#f85149;font-size:0.7rem;margin-top:3px;">⚠ Flagged content</div>' : ''}
            </div>
        `;
    }).join('');
}

// ─── AI INSIGHTS ───────────────────────────────────────────────────────────
async function loadInsights() {
    const resp = await fetch('/api/metadata/insights');
    const { insights } = await resp.json();
    const el = document.getElementById('metaInsights');
    if (!insights.length) { el.innerHTML = '<p style="color:#8b949e;">No insights generated.</p>'; return; }

    const severityColor = { HIGH: '#f85149', MEDIUM: '#d29922', LOW: '#3fb950' };
    el.innerHTML = insights.map(ins => `
        <div style="padding:8px;margin-bottom:7px;background:rgba(255,255,255,0.03);border-radius:6px;border-left:3px solid ${severityColor[ins.severity]||'#58a6ff'};">
            <div style="color:${severityColor[ins.severity]};font-size:0.7rem;font-weight:700;margin-bottom:3px;">${ins.severity}</div>
            <div style="color:#ccc;font-size:0.78rem;line-height:1.5;">${ins.text}</div>
        </div>
    `).join('');
}

// ─── CONTRADICTIONS ────────────────────────────────────────────────────────
async function loadMetaContradictions() {
    const resp = await fetch('/api/metadata/contradictions');
    const { contradictions } = await resp.json();
    const el = document.getElementById('metaContradictions');
    if (!contradictions.length) { el.innerHTML = '<p style="color:#3fb950;">✓ No contradictions detected.</p>'; return; }

    el.innerHTML = contradictions.map(c => `
        <div style="margin-bottom:12px;padding:12px;background:rgba(248,81,73,0.06);border-radius:8px;">
            <span style="color:#f85149;font-weight:700;font-size:0.78rem;">⚠ ${c.severity} SEVERITY</span>
            <div style="display:flex;gap:14px;margin-top:8px;">
                <div style="flex:1;padding:10px;background:#161b22;border-radius:6px;">
                    <div style="color:#8b949e;font-size:0.7rem;margin-bottom:4px;">SOURCE A</div>
                    <div style="color:#e6edf3;font-size:0.8rem;">${c.source_a}</div>
                </div>
                <div style="flex:1;padding:10px;background:#161b22;border-radius:6px;">
                    <div style="color:#8b949e;font-size:0.7rem;margin-bottom:4px;">SOURCE B</div>
                    <div style="color:#e6edf3;font-size:0.8rem;">${c.source_b}</div>
                </div>
            </div>
            <div style="margin-top:8px;color:#ccc;font-size:0.79rem;">${c.description}</div>
        </div>
    `).join('');
}

// ─── LEAFLET GPS MAP ────────────────────────────────────────────────────────
async function initMetaMap() {
    const resp = await fetch('/api/metadata/gps');
    const { gps } = await resp.json();
    if (!gps.length) return;

    if (metaMap) { metaMap.remove(); metaMap = null; }

    const center = [gps[0].lat, gps[0].lon];
    metaMap = L.map('metaMap', { zoomControl: true }).setView(center, 14);

    // Dark tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap, CartoDB',
        maxZoom: 19,
    }).addTo(metaMap);

    // Draw GPS trail polyline
    const coords = gps.map(g => [g.lat, g.lon]);
    L.polyline(coords, { color: '#58a6ff', weight: 3, opacity: 0.85, dashArray: '6,4' }).addTo(metaMap);

    // Markers for each GPS point
    gps.forEach((g, i) => {
        const color = i === 0 ? '#3fb950' : (i === gps.length - 1 ? '#f85149' : '#58a6ff');
        const icon = L.divIcon({
            className: '',
            html: `<div style="width:12px;height:12px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 0 8px ${color};"></div>`,
            iconSize: [12, 12],
        });
        L.marker([g.lat, g.lon], { icon })
            .addTo(metaMap)
            .bindPopup(`<b style="color:#111">${g.time}</b><br>${g.label||'Location'}`);
    });

    // Fit map to trail
    metaMap.fitBounds(coords, { padding: [20, 20] });
}

// ─── FILE UPLOAD ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('metaUploadInput');
    if (input) {
        input.addEventListener('change', async function() {
            if (!this.files.length) return;
            const formData = new FormData();
            formData.append('file', this.files[0]);
            document.getElementById('metaLoading').style.display = 'block';
            try {
                const resp = await fetch('/api/metadata/upload', { method: 'POST', body: formData });
                if (resp.ok) {
                    await loadMetadataModule();
                    // ✔ Mark Metadata intelligence complete
                    const unlocked = pipelineComplete('metadata');
                    showUnlockBanner(unlocked);
                    showModuleCompleteBar('metadata', 'Metadata Intelligence Analysis Complete');
                } else alert('Error parsing file.');
            } catch(e) { alert('Server error.'); }
            finally {
                document.getElementById('metaLoading').style.display = 'none';
                this.value = '';
            }
        });
    }
});

// ─── RESET ──────────────────────────────────────────────────────────────────
async function resetMetadata() {
    await fetch('/api/metadata/reset', { method: 'POST' });
    await loadMetadataModule();
}

// ─── AUTO-INIT when switching to metadata view ────────────────────────────
const _origSwitchView2 = window.switchView;
window.switchView = function(viewId) {
    _origSwitchView2 && _origSwitchView2(viewId);
    if (viewId === 'metadata') {
        setTimeout(loadMetadataModule, 200);
    }
};

// ─── MARK METADATA COMPLETE & NAVIGATE ───────────────────────────────────
function markMetadataAndProceed() {
    pipelineComplete('metadata');
    showModuleCompleteBar('metadata', 'Metadata Intelligence Analysis Complete');

    // Check if CCTV and Voice are also done
    const stillNeeded = ['cctv', 'voice'].filter(id => !PIPELINE.completed.has(id));

    if (stillNeeded.length === 0) {
        // All 3 primary modules done — navigate to Contradiction Detection
        forceView('contradiction');
    } else {
        // Not all done — guide user to the next incomplete primary module
        const stageNames = stillNeeded.map(id => {
            const s = PIPELINE.stages.find(x => x.id === id);
            return s ? s.label : id;
        });

        // Show amber notice inside the metadata view
        const existing = document.getElementById('meta-proceed-notice');
        if (existing) existing.remove();
        const notice = document.createElement('div');
        notice.id = 'meta-proceed-notice';
        notice.style.cssText = `
            background:rgba(210,153,34,0.12); border:1px solid #d29922; border-radius:8px;
            padding:12px 16px; margin-top:14px; display:flex; align-items:flex-start;
            gap:10px; color:#d29922; font-size:0.88rem;
        `;
        notice.innerHTML = `
            <i class="fa-solid fa-triangle-exclamation" style="margin-top:2px;"></i>
            <div>
                <strong>Metadata complete ✓</strong><br>
                <span style="color:#8b949e;">Still need to complete: <b style="color:#d29922;">${stageNames.join(', ')}</b><br>
                Click "Next Phase" inside those modules to mark them complete, then Contradiction Detection will unlock.</span>
            </div>`;
        const section = document.getElementById('metadata');
        if (section) section.appendChild(notice);

        // Navigate to the first incomplete primary module
        forceView(stillNeeded[0]);
    }
}
