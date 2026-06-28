// ====================================================
// FORENSEEK PIPELINE STATE MANAGER
// Controls the sequential investigation workflow.
// ====================================================

const PIPELINE = {
    stages: [
        { id: 'case-init',     label: '1. Case Initialization',    icon: 'fa-folder-open',          requires: [] },
        { id: 'cctv',          label: '2. CCTV Intelligence',       icon: 'fa-video',                requires: ['case-init'] },
        { id: 'voice',         label: '3. Voice Intelligence',      icon: 'fa-microphone',           requires: ['case-init'] },
        { id: 'metadata',      label: '4. Metadata Intelligence',   icon: 'fa-mobile-screen-button', requires: ['case-init'] },
        // Advanced modules LOCKED until all 3 primary evidence modules are explicitly completed
        { id: 'contradiction', label: '5. Contradiction Detection', icon: 'fa-triangle-exclamation', requires: ['cctv', 'voice', 'metadata'] },
        { id: 'graph',         label: '6. Knowledge Graph',         icon: 'fa-project-diagram',      requires: ['contradiction'] },
        { id: 'timeline',      label: '7. Event Timeline',          icon: 'fa-timeline',             requires: ['cctv'] },
        { id: 'autopsy',       label: '8. Autopsy Intelligence',    icon: 'fa-file-medical',         requires: ['case-init'] }, // Optional
        { id: 'final',         label: '9. Final Dashboard',         icon: 'fa-chart-pie',            requires: ['graph'] },
    ],
    completed: new Set(['case-init']),
    current: 'case-init'
};

// Mark a stage as complete and cascade unlock
function pipelineComplete(stageId) {
    PIPELINE.completed.add(stageId);
    renderPipeline();
    // Return list of newly-unlocked stages for notification
    return PIPELINE.stages
        .filter(s => !PIPELINE.completed.has(s.id) && s.requires.every(r => PIPELINE.completed.has(r)))
        .map(s => s.label);
}

// Check if a stage is unlocked (all its requirements are complete)
function pipelineIsUnlocked(stageId) {
    const stage = PIPELINE.stages.find(s => s.id === stageId);
    if (!stage) return false;
    return stage.requires.every(r => PIPELINE.completed.has(r));
}

// Navigate to a view (respects lock)
function forceView(viewId) {
    if (!pipelineIsUnlocked(viewId) && !PIPELINE.completed.has(viewId)) {
        showPipelineLockToast(viewId);
        return false;
    }
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    const view = document.getElementById(viewId);
    if (view) view.classList.add('active');
    const nav = document.getElementById('nav-' + viewId);
    if (nav) nav.classList.add('active');
    PIPELINE.current = viewId;
    return true;
}

function goToStep(currentId, hintNextId) {
    // 1. Mark current stage complete
    pipelineComplete(currentId);
    renderPipeline();

    // 2. If contradiction just unlocked (all 3 primaries done) → go there
    if (pipelineIsUnlocked('contradiction')) {
        showUnlockBanner(['5. Contradiction Detection — All evidence modules complete!']);
        forceView('contradiction');
        return;
    }

    // 3. Try the hinted next step if it's accessible
    if (hintNextId && (pipelineIsUnlocked(hintNextId) || PIPELINE.completed.has(hintNextId))) {
        forceView(hintNextId);
        return;
    }

    // 4. Find next incomplete primary module to guide the investigator
    const primaryOrder = ['cctv', 'voice', 'metadata'];
    const nextPrimary = primaryOrder.find(id => !PIPELINE.completed.has(id));
    if (nextPrimary) {
        showModuleCompleteBar(currentId, `${currentId.toUpperCase()} module complete ✓ — complete remaining evidence modules to unlock analysis.`);
        forceView(nextPrimary);
        return;
    }

    // 5. Fallback — stay on current view, show what was unlocked
    const newlyUnlocked = PIPELINE.stages
        .filter(s => pipelineIsUnlocked(s.id) && !PIPELINE.completed.has(s.id))
        .map(s => s.label);
    if (newlyUnlocked.length > 0) showUnlockBanner(newlyUnlocked);
}


// Compatibility shim
function switchView(viewId) { forceView(viewId); }

// Render sidebar based on current pipeline state
function renderPipeline() {
    const menu = document.getElementById('workflow-menu');
    if (!menu) return;
    menu.innerHTML = `<p class="menu-label">INVESTIGATION PIPELINE</p>`;

    PIPELINE.stages.forEach(stage => {
        const isCompleted = PIPELINE.completed.has(stage.id);
        const isUnlocked = pipelineIsUnlocked(stage.id) || isCompleted;
        const isCurrent = PIPELINE.current === stage.id;

        let statusIcon = '';
        let extraClass = '';

        if (isCompleted) {
            statusIcon = `<i class="fa-solid fa-check-circle" style="color:#3fb950; font-size:0.75rem; margin-left:auto;"></i>`;
        } else if (!isUnlocked) {
            statusIcon = `<i class="fa-solid fa-lock" style="color:#484f58; font-size:0.75rem; margin-left:auto;"></i>`;
            extraClass = 'locked';
        } else {
            statusIcon = `<i class="fa-solid fa-circle-dot" style="color:#d29922; font-size:0.75rem; margin-left:auto;"></i>`;
        }

        const div = document.createElement('div');
        div.className = `menu-item ${isCurrent ? 'active' : ''} ${extraClass}`;
        div.id = 'nav-' + stage.id;
        div.onclick = () => forceView(stage.id);
        div.innerHTML = `<i class="fa-solid ${stage.icon}"></i> ${stage.label} ${statusIcon}`;
        menu.appendChild(div);
    });
}

function showPipelineLockToast(stageId) {
    const stage = PIPELINE.stages.find(s => s.id === stageId);
    const missing = stage ? stage.requires.filter(r => !PIPELINE.completed.has(r)) : [];
    const missingLabels = missing.map(m => {
        const s = PIPELINE.stages.find(x => x.id === m);
        return s ? s.label : m;
    });

    const existing = document.getElementById('pipeline-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'pipeline-toast';
    toast.style.cssText = `
        position:fixed; bottom:30px; left:50%; transform:translateX(-50%);
        background:#161b22; border:1px solid #d29922; color:#d29922;
        padding:14px 24px; border-radius:10px; font-size:0.88rem;
        z-index:9999; box-shadow:0 8px 30px rgba(0,0,0,0.5);
        display:flex; align-items:center; gap:10px; max-width:500px;
        animation: slideUp 0.3s ease;
    `;
    toast.innerHTML = `
        <i class="fa-solid fa-lock"></i>
        <div>
            <strong>Module Locked</strong><br>
            <span style="color:#8b949e; font-size:0.8rem;">Complete required stages first: <b style="color:#d29922;">${missingLabels.join(', ')}</b></span>
        </div>`;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 4000);
}

// Show an unlock notification banner
function showUnlockBanner(labels) {
    if (!labels || labels.length === 0) return;
    const existing = document.getElementById('unlock-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'unlock-banner';
    banner.style.cssText = `
        position:fixed; top:20px; right:20px;
        background:#161b22; border:1px solid #3fb950; color:#3fb950;
        padding:14px 20px; border-radius:10px; font-size:0.88rem;
        z-index:9999; box-shadow:0 8px 30px rgba(0,0,0,0.5);
        display:flex; align-items:flex-start; gap:10px; max-width:380px;
    `;
    banner.innerHTML = `
        <i class="fa-solid fa-lock-open" style="margin-top:3px;"></i>
        <div>
            <strong>Modules Unlocked!</strong><br>
            <span style="color:#8b949e; font-size:0.8rem;">${labels.join('<br>')} — ready for analysis.</span>
        </div>`;
    document.body.appendChild(banner);
    setTimeout(() => { if (banner.parentNode) banner.remove(); }, 5000);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    renderPipeline();
    // Unlock the three primary modules immediately after case init
    PIPELINE.completed.add('case-init');
    renderPipeline();
});

// Show a green "Module Complete" bar at the top of the completed view
function showModuleCompleteBar(stageId, message) {
    const view = document.getElementById(stageId);
    if (!view) return;
    const existing = view.querySelector('.module-complete-bar');
    if (existing) existing.remove();

    const bar = document.createElement('div');
    bar.className = 'module-complete-bar';
    bar.style.cssText = `
        background: rgba(63,185,80,0.12); border: 1px solid #3fb950;
        border-radius: 8px; padding: 10px 16px; margin-bottom: 16px;
        display: flex; align-items: center; gap: 10px; color: #3fb950;
        font-size: 0.88rem; font-weight: 500;
    `;
    bar.innerHTML = `
        <i class="fa-solid fa-check-circle"></i>
        <span>${message} — <span style="color:#8b949e;">Next stage has been unlocked.</span></span>`;
    view.insertBefore(bar, view.children[1]);
}
