// graph.js - Knowledge Graph Module Logic (Cytoscape.js)

let cy = null;  // Cytoscape instance

// ─── NODE TYPE → SHAPE MAPPING ─────────────────────────────────────────────
const SHAPE_MAP = {
    suspect:   'octagon',
    victim:    'ellipse',
    witness:   'diamond',
    vehicle:   'rectangle',
    location:  'round-rectangle',
    object:    'triangle',
    event:     'star',
    timestamp: 'hexagon',
    person:    'ellipse',
};

// ─── INIT GRAPH ────────────────────────────────────────────────────────────
async function initGraph() {
    try {
        const resp = await fetch('/api/graph/data');
        const data = await resp.json();

        cy = cytoscape({
            container: document.getElementById('cy'),
            elements: data.elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(bg)',
                        'border-color':     'data(border)',
                        'border-width':     2,
                        'label':            'data(label)',
                        'color':            '#e6edf3',
                        'font-size':        '11px',
                        'font-family':      'Inter, sans-serif',
                        'text-valign':      'bottom',
                        'text-margin-y':    6,
                        'text-wrap':        'wrap',
                        'text-max-width':   '100px',
                        'width':            42,
                        'height':           42,
                        'shape':            function(ele) {
                            return SHAPE_MAP[ele.data('type')] || 'ellipse';
                        },
                        'overlay-opacity':  0,
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-width':   4,
                        'border-color':   '#ffffff',
                        'shadow-blur':    20,
                        'shadow-color':   'data(border)',
                        'shadow-opacity': 1,
                        'shadow-offset-x': 0,
                        'shadow-offset-y': 0,
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width':              1.5,
                        'line-color':         '#30363d',
                        'target-arrow-color': '#30363d',
                        'target-arrow-shape': 'triangle',
                        'curve-style':        'bezier',
                        'label':              'data(label)',
                        'font-size':          '9px',
                        'color':              '#8b949e',
                        'font-family':        'Inter, sans-serif',
                        'text-background-color': '#0b1120',
                        'text-background-opacity': 0.8,
                        'text-background-padding': '2px',
                        'overlay-opacity':    0,
                    }
                },
                {
                    selector: 'edge:selected',
                    style: { 'line-color': '#58a6ff', 'target-arrow-color': '#58a6ff' }
                },
                {
                    selector: '.highlighted',
                    style: { 'border-color': '#f0c000', 'border-width': 3 }
                }
            ],
            layout: {
                name: 'cose',
                animate: true,
                animationDuration: 800,
                randomize: true,
                nodeRepulsion: () => 8000,
                idealEdgeLength: () => 100,
                edgeElasticity: () => 100,
            }
        });

        // ── Node click → show details ──
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const data = node.data();
            const icon = data.icon || '🔵';
            document.getElementById('nodeDetailContent').innerHTML = `
                <div style="margin-bottom:8px;">
                    <span style="font-size:1.5rem;">${icon}</span>
                    <strong style="color:${data.border};margin-left:8px;">${data.label}</strong>
                </div>
                <div style="color:#8b949e;font-size:0.8rem;margin-bottom:6px;">
                    <b style="color:#e6edf3;">Type:</b> ${data.type.toUpperCase()}
                </div>
                <div style="background:#0b1120;padding:10px;border-radius:6px;color:#ccc;font-size:0.8rem;line-height:1.6;">
                    ${data.details || 'No additional details.'}
                </div>
                <div style="margin-top:10px;font-size:0.75rem;color:#8b949e;">
                    Connected to <b style="color:#58a6ff;">${node.connectedEdges().length}</b> other nodes
                </div>
            `;
            // Highlight connected edges
            cy.elements().removeClass('highlighted');
            node.connectedEdges().addClass('highlighted');
        });

        // ── Background click → deselect ──
        cy.on('tap', function(evt) {
            if(evt.target === cy) {
                document.getElementById('nodeDetailContent').innerHTML = 'Click any node in the graph to inspect it.';
                document.getElementById('nodeDetailContent').style.color = '#8b949e';
            }
        });

        document.getElementById('graphLoading').style.display = 'none';

        // Load side panels
        loadTimeline();
        loadContradictions();

        // ✔ Mark Knowledge Graph complete
        const unlocked = pipelineComplete('graph');
        showUnlockBanner(unlocked);
        showModuleCompleteBar('graph', 'Knowledge Graph Generation Complete');

    } catch(err) {
        console.error('Graph init error:', err);
        document.getElementById('graphLoading').innerHTML =
            '<p style="color:#f85149;">Failed to load graph. Is the server running?</p>';
    }
}

// ─── LOAD TIMELINE ─────────────────────────────────────────────────────────
async function loadTimeline() {
    try {
        const resp = await fetch('/api/graph/timeline');
        const data = await resp.json();
        const el = document.getElementById('graphTimeline');
        if (!data.timeline || data.timeline.length === 0) {
            el.innerHTML = '<p style="color:#8b949e;">No timeline events.</p>';
            return;
        }
        el.innerHTML = data.timeline.map((ev, i) => `
            <div style="display:flex;gap:10px;margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid #21262d;">
                <div style="min-width:60px;color:#3fb950;font-weight:600;font-size:0.78rem;">${ev.time}</div>
                <div>
                    <div style="color:#e6edf3;font-size:0.82rem;">${ev.event}</div>
                    <div style="color:#8b949e;font-size:0.72rem;margin-top:2px;">${ev.source}</div>
                </div>
            </div>
        `).join('');
    } catch(e) { console.error(e); }
}

// ─── LOAD CONTRADICTIONS ───────────────────────────────────────────────────
async function loadContradictions() {
    try {
        const resp = await fetch('/api/graph/contradictions');
        const data = await resp.json();
        const el = document.getElementById('contradictionList');
        const badge = document.getElementById('contraBadge');
        badge.textContent = data.contradictions.length;
        if (!data.contradictions.length) {
            el.innerHTML = '<p style="color:#3fb950;">✓ No contradictions detected.</p>';
            return;
        }
        el.innerHTML = data.contradictions.map(c => `
            <div style="margin-bottom:10px;padding:8px;background:rgba(248,81,73,0.08);border-radius:6px;border-left:2px solid #f85149;">
                <div style="color:#f85149;font-weight:600;font-size:0.78rem;">${c.severity} SEVERITY</div>
                <div style="color:#ccc;font-size:0.78rem;margin-top:4px;">${c.description}</div>
            </div>
        `).join('');
    } catch(e) { console.error(e); }
}

// ─── SEARCH GRAPH ──────────────────────────────────────────────────────────
async function searchGraph() {
    const q = document.getElementById('graphSearchInput').value.trim();
    if (!q) return;

    const resp = await fetch(`/api/graph/search?q=${encodeURIComponent(q)}`);
    const data = await resp.json();

    document.getElementById('searchResultsPanel').style.display = 'block';
    const list = document.getElementById('searchResultsList');

    if (!data.results.length) {
        list.innerHTML = '<p style="color:#8b949e;">No matching nodes found.</p>';
        cy.elements().removeClass('highlighted');
        return;
    }

    cy.elements().removeClass('highlighted');
    list.innerHTML = data.results.map(r => `
        <div onclick="focusNode('${r.id}')" style="cursor:pointer;padding:8px;border-radius:6px;background:rgba(88,166,255,0.1);margin-bottom:6px;border:1px solid #30363d;">
            <strong style="color:#58a6ff;">${r.label}</strong>
            <span style="color:#8b949e;font-size:0.75rem;margin-left:8px;">${r.type}</span>
        </div>
    `).join('');

    // Highlight matching nodes in graph
    data.results.forEach(r => {
        const node = cy.getElementById(r.id);
        if (node) node.addClass('highlighted');
    });
}

function focusNode(nodeId) {
    const node = cy.getElementById(nodeId);
    if (node) {
        cy.animate({ center: { eles: node }, zoom: 1.8 }, { duration: 400 });
        node.select();
        node.emit('tap');
    }
}

// ─── INGEST CCTV ──────────────────────────────────────────────────────────
async function ingestCCTV() {
    const btn = document.querySelector('[onclick="ingestCCTV()"]');
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Ingesting...';
    try {
        await fetch('/api/graph/ingest_cctv', { method: 'POST' });
        // Re-render graph
        if (cy) cy.destroy();
        document.getElementById('graphLoading').style.display = 'flex';
        await initGraph();
    } catch(e) { console.error(e); }
    btn.innerHTML = '<i class="fa-solid fa-video"></i> Ingest CCTV';
}

// ─── RESET GRAPH ──────────────────────────────────────────────────────────
async function resetGraph() {
    await fetch('/api/graph/reset', { method: 'POST' });
    if (cy) cy.destroy();
    document.getElementById('graphLoading').style.display = 'flex';
    await initGraph();
}

// ─── AUTO-INIT when switching to graph view ────────────────────────────────
// Hook into the switchView function to lazy-init the graph
const _origSwitchView = window.switchView;
window.switchView = function(viewId) {
    _origSwitchView && _origSwitchView(viewId);
    if (viewId === 'graph' && !cy) {
        setTimeout(initGraph, 200);
    }
};

// Also init if graph view is already active on page load
document.addEventListener('DOMContentLoaded', () => {
    const active = document.querySelector('.view.active');
    if (active && active.id === 'graph') initGraph();
});
