let sessionWitnessLogs = [];

// ─── Navigation stubs (implemented in pipeline.js) ────────────────────────────
// forceView, goToStep, switchView, pipelineComplete etc. live in pipeline.js
// which is loaded before script.js.

// ─── CCTV TIMELINE LOADER ─────────────────────────────────────────────────────
async function loadCCTVTimeline(jsonUrl = 'CCTV sample/cctv_timeline_events.json') {
    try {
        const response = await fetch(jsonUrl);
        if (response.ok) {
            const data = await response.json();
            const list = document.querySelector('.timeline-list');
            list.innerHTML = '';
            const sampleData = data.slice(0, 100);
            sampleData.forEach(event => {
                const li = document.createElement('li');
                const timeSpan = document.createElement('span');
                timeSpan.className = 'time';
                const totalSec = Math.floor(event.time_offset_sec);
                const min = String(Math.floor(totalSec / 60)).padStart(2, '0');
                const sec = String(totalSec % 60).padStart(2, '0');
                timeSpan.innerText = `${min}:${sec}`;
                const eventSpan = document.createElement('span');
                eventSpan.className = 'event';
                eventSpan.innerHTML = `<b>${event.subject_id} (${event.entity_type})</b> detected tracking.`;
                li.appendChild(timeSpan);
                li.appendChild(eventSpan);
                list.appendChild(li);
            });
        }
    } catch (e) {
        console.log("Timeline not loaded yet.");
    }
}

// ─── VOICE INTELLIGENCE: LIVE RECORDING ──────────────────────────────────────
let recognition = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let timerInterval = null;
let timerSeconds = 0;
let fullTranscript = '';
let audioContext = null;
let analyser = null;
let animFrameId = null;

function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    isRecording = true;
    fullTranscript = '';
    audioChunks = [];
    timerSeconds = 0;

    // Update UI
    document.getElementById('recordBtn').innerHTML = '<i class="fa-solid fa-stop"></i> Stop Recording';
    document.getElementById('recordBtn').style.background = 'rgba(248,81,73,0.3)';
    document.getElementById('recordBtn').style.border = '1px solid #f85149';
    document.getElementById('recordingBadge').style.display = 'inline-block';
    document.getElementById('liveTranscriptBox').innerHTML = '<span style="color:#58a6ff">Listening...</span>';
    document.getElementById('wordCount').textContent = '0';

    // Start timer
    timerInterval = setInterval(() => {
        timerSeconds++;
        const m = String(Math.floor(timerSeconds / 60)).padStart(2, '0');
        const s = String(timerSeconds % 60).padStart(2, '0');
        document.getElementById('recTimer').textContent = `${m}:${s}`;
    }, 1000);

    // ── 1. Web Speech API for LIVE interim text ──────────────────────────────
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        const langMap = {
            "English": "en-US",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "Hindi": "hi-IN",
            "German": "de-DE",
            "Mandarin": "zh-CN",
            "Tamil": "ta-IN"
        };
        const selectedLang = document.getElementById('voiceTargetLanguage')?.value || 'English';
        recognition.lang = langMap[selectedLang] || 'en-US';

        recognition.onresult = (event) => {
            let interim = '';
            let final = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                const confidence = event.results[i][0].confidence;
                if (event.results[i].isFinal) {
                    final += transcript;
                    fullTranscript += transcript + ' ';
                    if (confidence > 0) {
                        document.getElementById('confScore').textContent = Math.round(confidence * 100) + '%';
                    }
                } else {
                    interim += transcript;
                }
            }
            const words = fullTranscript.trim().split(/\s+/).filter(w => w.length > 0);
            document.getElementById('wordCount').textContent = words.length;
            document.getElementById('liveTranscriptBox').innerHTML =
                `<span style="color:#e6edf3">${fullTranscript}</span>` +
                `<span style="color:#8b949e"> ${interim}</span>`;
        };

        recognition.onerror = (e) => console.error('Speech recognition error:', e.error);
        recognition.start();
    } else {
        document.getElementById('liveTranscriptBox').innerHTML =
            '<span style="color:#f85149">Live transcription not supported in this browser. Use Chrome.</span>';
    }

    // ── 2. MediaRecorder to capture audio for ElevenLabs ────────────────────
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
        mediaRecorder.start(250);

        // ── 3. Waveform visualizer ───────────────────────────────────────────
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        drawWaveform();
    } catch(err) {
        console.error('Microphone access denied:', err);
        document.getElementById('liveTranscriptBox').innerHTML =
            '<span style="color:#f85149">Microphone access denied. Please allow microphone permissions.</span>';
    }
}

function drawWaveform() {
    const canvas = document.getElementById('waveformCanvas');
    if (!canvas || !analyser) return;
    const ctx = canvas.getContext('2d');
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    canvas.width = canvas.offsetWidth;

    function draw() {
        animFrameId = requestAnimationFrame(draw);
        analyser.getByteTimeDomainData(dataArray);
        ctx.fillStyle = '#0d1117';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#58a6ff';
        ctx.beginPath();
        const sliceWidth = canvas.width / bufferLength;
        let x = 0;
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = (v * canvas.height) / 2;
            i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            x += sliceWidth;
        }
        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
    }
    draw();
}

async function stopRecording() {
    isRecording = false;
    clearInterval(timerInterval);
    if (animFrameId) cancelAnimationFrame(animFrameId);

    // Reset UI
    document.getElementById('recordBtn').innerHTML = '<i class="fa-solid fa-microphone"></i> Start Recording';
    document.getElementById('recordBtn').style.background = '';
    document.getElementById('recordBtn').style.border = '';
    document.getElementById('recordingBadge').style.display = 'none';

    // Stop speech recognition
    if (recognition) { try { recognition.stop(); } catch(e){} }

    // Stop media recorder and send to ElevenLabs
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendToElevenLabs(blob, 'recording.webm');
            // Stop all tracks
            mediaRecorder.stream.getTracks().forEach(t => t.stop());
            if (audioContext) audioContext.close();
        };
    }
}

async function sendToElevenLabs(blob, filename) {
    document.getElementById('voiceLoading').style.display = 'block';
    document.getElementById('voiceTranscript').style.opacity = '0.4';

    const formData = new FormData();
    formData.append('file', blob, filename);
    const targetLang = document.getElementById('voiceTargetLanguage')?.value || 'English';
    formData.append('target_language', targetLang);

    try {
        const response = await fetch('/api/upload_voice', { method: 'POST', body: formData });
        if (response.ok) {
            const data = await response.json();
            document.getElementById('voiceTranscript').textContent = '"' + data.transcript + '"';
            document.getElementById('voiceTranscript').style.opacity = '1';

            // Store for contradiction engine
            sessionWitnessLogs.push({ text: data.transcript, language: targetLang });

            // Add to Witness Logs
            const logsContainer = document.getElementById('witnessLogsContainer');
            const noLogsMsg = document.getElementById('noWitnessLogsMsg');
            if(noLogsMsg) noLogsMsg.style.display = 'none';

            const logEntry = document.createElement('div');
            logEntry.style.background = '#0d1117';
            logEntry.style.border = '1px solid #30363d';
            logEntry.style.borderRadius = '6px';
            logEntry.style.padding = '12px';
            logEntry.style.borderLeft = '3px solid #58a6ff';
            
            const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            
            logEntry.innerHTML = `
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <strong style="color:#e6edf3;">Interview Log</strong>
                    <span style="font-size:0.8rem; color:#8b949e;">${timestamp} | Lang: ${targetLang}</span>
                </div>
                <div style="color:#ccc; font-style:italic; font-size:0.9rem;">"${data.transcript}"</div>
            `;
            if (logsContainer) logsContainer.prepend(logEntry);

            const badge = document.getElementById('voiceStatusBadge');
            badge.textContent = 'STT COMPLETE';
            badge.style.background = 'rgba(63,185,80,0.2)';
            badge.style.color = '#3fb950';
            badge.style.border = '1px solid #3fb950';

            // ✔ Mark Voice Intelligence complete
            const unlocked = pipelineComplete('voice');
            showUnlockBanner(unlocked);
            showModuleCompleteBar('voice', 'Voice Intelligence Analysis Complete');

            const table = document.getElementById('voiceEntityTable');
            while(table.rows.length > 1) table.deleteRow(1);
            if (data.entities && data.entities.length > 0) {
                data.entities.forEach(ent => {
                    const row = table.insertRow();
                    row.innerHTML = `<td style="padding:8px;color:#58a6ff">${ent.text || ent}</td><td style="padding:8px">${ent.type || 'ENTITY'}</td>`;
                });
            } else {
                const row = table.insertRow();
                row.innerHTML = '<td colspan="2" style="padding:8px;color:#8b949e">No structured entities extracted.</td>';
            }
        } else {
            document.getElementById('voiceTranscript').textContent = 'ElevenLabs API error. Check server.';
        }
    } catch(err) {
        console.error(err);
        document.getElementById('voiceTranscript').textContent = 'Server connection error.';
    } finally {
        document.getElementById('voiceLoading').style.display = 'none';
        document.getElementById('voiceTranscript').style.opacity = '1';
    }
}

// ─── DOM READY ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadCCTVTimeline();

    // 3D SCENE UPLOAD
    const uploadInput = document.getElementById('sceneUploadInput');
    if(uploadInput) {
        uploadInput.addEventListener('change', async function(e) {
            if(this.files.length === 0) return;
            const formData = new FormData();
            for (let i = 0; i < this.files.length; i++) formData.append('files', this.files[i]);
            document.getElementById('sceneIframeContainer').style.display = 'none';
            document.getElementById('sceneLoading').style.display = 'block';
            try {
                const response = await fetch('/api/upload_scene_multi', { method: 'POST', body: formData });
                if(response.ok) {
                    const iframe = document.querySelector('#sceneIframeContainer iframe');
                    iframe.src = '3d_viewer.html?' + new Date().getTime();
                } else { alert('Error processing image.'); }
            } catch(err) { alert('Server error.'); }
            finally {
                document.getElementById('sceneLoading').style.display = 'none';
                document.getElementById('sceneIframeContainer').style.display = 'block';
                this.value = '';
            }
        });
    }

    // VICTIM REFERENCE PHOTO UPLOAD
    const victimPhotoInput = document.getElementById('victimPhotoInput');
    if (victimPhotoInput) {
        victimPhotoInput.addEventListener('change', async function() {
            if (this.files.length === 0) return;
            const statusEl = document.getElementById('victimPhotoStatus');
            statusEl.style.display = 'block';
            statusEl.style.background = 'rgba(88, 166, 255, 0.1)';
            statusEl.style.borderColor = '#58a6ff';
            statusEl.style.color = '#58a6ff';
            statusEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Registering victim reference photo into tracking engine...';

            const formData = new FormData();
            formData.append('photo', this.files[0]);
            formData.append('role', 'VICTIM');
            try {
                const res = await fetch('/api/cctv/reference_photo', { method: 'POST', body: formData });
                const data = await res.json();
                statusEl.style.background = 'rgba(63, 185, 80, 0.1)';
                statusEl.style.borderColor = '#3fb950';
                statusEl.style.color = '#3fb950';
                statusEl.innerHTML = `<i class="fa-solid fa-check-circle"></i> Victim Reference Photo registered. Label: <b>${data.victim_label}</b>. Engine will now flag this subject as "VICTIM" in the footage.`;
            } catch(err) {
                statusEl.style.background = 'rgba(248,81,73,0.1)';
                statusEl.style.borderColor = '#f85149';
                statusEl.style.color = '#f85149';
                statusEl.innerHTML = '<i class="fa-solid fa-xmark"></i> Failed to register reference photo. Ensure the server is running.';
            }
        });
    }

    // WITNESS REFERENCE PHOTO UPLOAD
    const witnessPhotoInput = document.getElementById('witnessPhotoInput');
    if (witnessPhotoInput) {
        witnessPhotoInput.addEventListener('change', async function() {
            if (this.files.length === 0) return;
            const statusEl = document.getElementById('victimPhotoStatus');
            statusEl.style.display = 'block';
            statusEl.style.background = 'rgba(88, 166, 255, 0.1)';
            statusEl.style.borderColor = '#58a6ff';
            statusEl.style.color = '#58a6ff';
            statusEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Registering witness reference photo into tracking engine...';

            const formData = new FormData();
            formData.append('photo', this.files[0]);
            formData.append('role', 'WITNESS');
            try {
                const res = await fetch('/api/cctv/reference_photo', { method: 'POST', body: formData });
                const data = await res.json();
                statusEl.style.background = 'rgba(63, 185, 80, 0.1)';
                statusEl.style.borderColor = '#3fb950';
                statusEl.style.color = '#3fb950';
                statusEl.innerHTML = `<i class="fa-solid fa-check-circle"></i> Witness Reference Photo registered. Label: <b>${data.victim_label}</b>. Engine will now flag this subject as "WITNESS" in the footage.`;
            } catch(err) {
                statusEl.style.background = 'rgba(248,81,73,0.1)';
                statusEl.style.borderColor = '#f85149';
                statusEl.style.color = '#f85149';
                statusEl.innerHTML = '<i class="fa-solid fa-xmark"></i> Failed to register reference photo. Ensure the server is running.';
            }
        });
    }

    // CCTV VIDEO UPLOAD
    const cctvUploadInput = document.getElementById('cctvUploadInput');
    if(cctvUploadInput) {
        cctvUploadInput.addEventListener('change', async function(e) {
            if(this.files.length === 0) return;
            const formData = new FormData();
            formData.append('file', this.files[0]);
            document.querySelector('.content-split').style.display = 'none';
            const placeholder = document.getElementById('cctvPlaceholder');
            if(placeholder) placeholder.style.display = 'none';
            document.getElementById('cctvLoading').style.display = 'block';
            try {
                const response = await fetch('/api/upload_cctv', { method: 'POST', body: formData });
                if(response.ok) {
                    const data = await response.json();
                    const vp = document.querySelector('.cctv-player');
                    vp.src = data.video_url; vp.load(); vp.play();
                    loadCCTVTimeline(data.json_url);
                    // ✔ Mark CCTV intelligence complete
                    const unlocked = pipelineComplete('cctv');
                    showUnlockBanner(unlocked);
                    showModuleCompleteBar('cctv', 'CCTV Intelligence Analysis Complete');
                } else { alert('Error processing video.'); }
            } catch(err) { alert('Server error.'); }
            finally {
                document.getElementById('cctvLoading').style.display = 'none';
                document.querySelector('.content-split').style.display = 'grid';
                this.value = '';
            }
        });
    }

    // VOICE FILE UPLOAD (alternative to live recording)
    const voiceUploadInput = document.getElementById('voiceUploadInput');
    if(voiceUploadInput) {
        voiceUploadInput.addEventListener('change', async function(e) {
            if(this.files.length === 0) return;
            const blob = this.files[0];
            await sendToElevenLabs(blob, blob.name);
            // ✔ Mark Voice intelligence complete after file upload
            const unlocked = pipelineComplete('voice');
            showUnlockBanner(unlocked);
            showModuleCompleteBar('voice', 'Voice Intelligence Analysis Complete');
            this.value = '';
        });
    }
});

async function runContradictionAnalysis() {
    const container = document.getElementById('dynamicContradictionsContainer');
    if (!container) return;
    
    container.innerHTML = '<div style="text-align:center; padding:20px; color:#58a6ff;"><i class="fa-solid fa-spinner fa-spin"></i> AI Cross-Analyzing Evidence...</div>';
    
    try {
        const response = await fetch('/api/contradictions/cross_analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ witness_logs: sessionWitnessLogs })
        });
        
        if (response.ok) {
            const data = await response.json();
            container.innerHTML = '';
            
            if (!data.contradictions || data.contradictions.length === 0) {
                container.innerHTML = '<p style="color:#8b949e;font-style:italic;">No contradictions detected.</p>';
                // Still mark complete - absence of contradiction is a valid result
                const unlocked = pipelineComplete('contradiction');
                showUnlockBanner(unlocked);
                return;
            }

            
            data.contradictions.forEach(c => {
                const isHigh = c.severity === 'HIGH';
                const color = isHigh ? '#f85149' : (c.severity === 'MEDIUM' ? '#d29922' : '#3fb950');
                const card = document.createElement('div');
                card.className = 'card';
                card.style.borderLeft = `4px solid ${color}`;
                card.style.marginBottom = '15px';
                card.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <h4 style="color:${color};"><i class="fa-solid fa-triangle-exclamation"></i> ${c.type.replace('_', ' ')}</h4>
                        <span class="badge" style="background:transparent;border:1px solid ${color};color:${color}">${c.severity} RISK</span>
                    </div>
                    <p style="color:#e6edf3;margin-bottom:15px;">${c.description}</p>
                    <div style="background:#0d1117;padding:12px;border-radius:6px;font-size:0.9rem;border:1px solid #30363d;">
                        <div style="margin-bottom:8px;color:#8b949e;"><strong style="color:#ccc;">Source A:</strong> ${c.source_1}</div>
                        <div style="color:#8b949e;"><strong style="color:#ccc;">Source B:</strong> ${c.source_2}</div>
                    </div>
                `;
                container.appendChild(card);
            });
            // ✔ Mark Contradiction Detection complete
            const unlocked = pipelineComplete('contradiction');
            showUnlockBanner(unlocked);
            
        } else {
            container.innerHTML = '<p style="color:#f85149;">Error analyzing contradictions.</p>';
        }
    } catch(err) {
        console.error(err);
        container.innerHTML = '<p style="color:#f85149;">Server connection error.</p>';
    }
}

async function reconstructTemporalGaps() {
    const container = document.getElementById('dynamicGlobalTimeline');
    if (!container) return;
    
    container.innerHTML = '<div style="text-align:center; padding:20px; color:#58a6ff;"><i class="fa-solid fa-spinner fa-spin"></i> Engine detecting missing timeline intervals...</div>';
    
    try {
        const response = await fetch('/api/timeline/reconstruct', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ witness_logs: sessionWitnessLogs })
        });
        
        if (response.ok) {
            const data = await response.json();
            container.innerHTML = '';
            
            if (!data.timeline || data.timeline.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:40px; color:#8b949e;"><i class="fa-solid fa-circle-info fa-2x" style="margin-bottom:12px; color:#30363d;"></i><p>No timeline events could be generated.</p></div>';
                return;
            }

            data.timeline.forEach(ev => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                
                // Handle the "no CCTV" informational card
                if (!ev.is_gap && ev.time === '--:--') {
                    container.innerHTML = `
                        <div style="text-align:center; padding:40px; background:rgba(88,166,255,0.05); border:1px dashed #30363d; border-radius:8px;">
                            <i class="fa-solid fa-video-slash fa-2x" style="color:#30363d; margin-bottom:14px;"></i>
                            <h3 style="color:#e6edf3; margin-bottom:8px;">${ev.content}</h3>
                            <p style="color:#8b949e; font-size:0.9rem;">${ev.source}</p>
                        </div>`;
                    return;
                }
                
                if (ev.is_gap) {
                    item.style.borderLeftColor = '#d29922';
                    let actsHtml = (ev.activities || []).map(a => `<li style="margin-bottom:4px;">• ${a}</li>`).join('');
                    item.innerHTML = `
                        <div class="tl-time" style="color:#d29922; font-weight:bold; width:130px; font-size:0.8rem;">${ev.time}</div>
                        <div class="tl-content" style="background:rgba(210,153,34,0.08); border:1px solid #d29922; border-radius:6px; padding:15px; margin-bottom:15px;">
                            <h4 style="color:#d29922; margin-bottom:10px;"><i class="fa-solid fa-triangle-exclamation"></i> ${ev.content}</h4>
                            <div style="margin-bottom:12px;">
                                <strong style="color:#e6edf3; font-size:0.9rem;">Possible Intermediate Activities:</strong>
                                <ul style="margin-top:6px; list-style-type:none; padding-left:5px; color:#c9d1d9; font-size:0.85rem;">${actsHtml}</ul>
                            </div>
                            <div style="background:#0d1117; padding:10px; border-radius:4px; font-size:0.8rem; color:#8b949e; border:1px solid #30363d;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:6px; border-bottom:1px solid #21262d; padding-bottom:6px;">
                                    <span><strong style="color:#ccc;">Confidence:</strong> <span style="color:#3fb950; font-weight:bold;">${ev.confidence}</span></span>
                                    <span><strong style="color:#ccc;">Supporting Evidence:</strong> ${ev.supporting_evidence}</span>
                                </div>
                                <div><strong style="color:#ccc;">Reasoning:</strong> ${ev.reasoning}</div>
                            </div>
                        </div>`;
                } else {
                    item.innerHTML = `
                        <div class="tl-time" style="width:130px;">${ev.time}</div>
                        <div class="tl-content" style="margin-bottom:15px;">
                            <h4 style="color:#58a6ff; margin-bottom:4px;">${ev.content}</h4>
                            <p style="color:#8b949e; font-size:0.85rem;"><i class="fa-solid fa-link" style="font-size:0.7rem;"></i> Source: ${ev.source || 'System'}</p>
                        </div>`;
                }
                container.appendChild(item);
            });
            // ✔ Mark Event Timeline complete
            const unlocked = pipelineComplete('timeline');
            showUnlockBanner(unlocked);
            
        } else {
            container.innerHTML = '<p style="color:#f85149;"><i class="fa-solid fa-xmark"></i> Server returned an error. Check the server terminal for details.</p>';
        }
    } catch(err) {
        console.error(err);
        container.innerHTML = '<p style="color:#f85149;"><i class="fa-solid fa-plug"></i> Cannot reach server. Ensure the FastAPI server is running.</p>';
    }
}

// ==========================================
// METAMODEL FINAL DASHBOARD ENGINE
// ==========================================

function updateFinalUI(data) {
    if (data.status === "insufficient_data") {
        document.getElementById('finalContent').style.display = 'none';
        document.getElementById('finalLoading').innerHTML = `<i class="fa-solid fa-triangle-exclamation fa-2x" style="color:#f85149;"></i><p style="color:#f85149; margin-top:10px;">${data.summary}</p>`;
        return;
    }

    document.getElementById('finalContent').style.display = 'block';

    // Animate Scores
    document.getElementById('scoreEvidence').innerText = data.scores.evidence + '%';
    document.getElementById('scoreWitness').innerText = data.scores.witness + '%';
    document.getElementById('scoreTimeline').innerText = data.scores.timeline + '%';

    // Color code scores dynamically
    const applyColor = (id, score) => {
        const el = document.getElementById(id);
        if(score >= 80) el.style.color = '#3fb950';
        else if(score >= 50) el.style.color = '#d29922';
        else el.style.color = '#f85149';
    };
    applyColor('scoreEvidence', data.scores.evidence);
    applyColor('scoreWitness', data.scores.witness);
    applyColor('scoreTimeline', data.scores.timeline);

    // Update Text Data
    document.getElementById('finalSummary').innerText = data.summary;
    document.getElementById('finalSuspect').innerText = data.suspect;

    // Reasoning Trace
    const reasonHtml = data.reasoning_trace.map(r => {
        let color = '#8b949e';
        if(r.includes("WHAT-IF OVERRIDE")) color = '#f85149';
        if(r.includes("WHAT-IF APPLIED")) color = '#d29922';
        return `<li style="margin-bottom:8px; color:${color};"><i class="fa-solid fa-angle-right" style="font-size:0.7rem; margin-right:5px;"></i> ${r}</li>`;
    }).join('');
    document.getElementById('finalReasoning').innerHTML = reasonHtml || '<li>No explicit trace available.</li>';

    // Contradictions
    let contraHtml = '';
    if (data.contradiction_alerts && data.contradiction_alerts.length > 0) {
        contraHtml = data.contradiction_alerts.map(a => {
            let color = a.includes('HIGH') ? '#f85149' : '#d29922';
            return `<div style="background:rgba(248,81,73,0.1); border-left:3px solid ${color}; padding:10px; margin-bottom:10px;">${a}</div>`;
        }).join('');
    } else {
        contraHtml = '<div style="color:#3fb950;"><i class="fa-solid fa-check"></i> No contradictions detected across evidence.</div>';
    }
    document.getElementById('finalContradictions').innerHTML = contraHtml;
}

async function generateFinalDashboard() {
    document.getElementById('finalLoading').style.display = 'block';
    document.getElementById('finalContent').style.display = 'none';
    
    try {
        const res = await fetch('/api/final/dashboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ witness_logs: sessionWitnessLogs })
        });
        const data = await res.json();
        document.getElementById('finalLoading').style.display = 'none';
        updateFinalUI(data);
    } catch (err) {
        console.error(err);
        document.getElementById('finalLoading').innerHTML = '<p style="color:#f85149;">Connection error resolving metamodel.</p>';
    }
}

async function runWhatIf() {
    const scenario = document.getElementById('whatIfInput').value;
    if(!scenario) return;
    
    document.getElementById('whatIfStatus').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Simulating probabilistic shift...';
    
    try {
        const res = await fetch('/api/final/whatif', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ witness_logs: sessionWitnessLogs, scenario: scenario })
        });
        const data = await res.json();
        updateFinalUI(data);
        document.getElementById('whatIfStatus').innerHTML = '<span style="color:#3fb950;">Simulation complete. Scores adjusted based on theoretical scenario.</span>';
    } catch (err) {
        console.error(err);
        document.getElementById('whatIfStatus').innerHTML = '<span style="color:#f85149;">Simulation failed.</span>';
    }
}

// ==========================================
// PDF REPORT EXPORT ENGINE
// ==========================================

async function exportPDFReport() {
    const btn = document.querySelector('[onclick="exportPDFReport()"]');
    if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Report...';
        btn.disabled = true;
    }

    try {
        // Fetch the final dashboard data for report content
        const res = await fetch('/api/final/dashboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ witness_logs: sessionWitnessLogs })
        });
        const dashData = await res.json();

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

        const W = 210, MARGIN = 15;
        const usableW = W - MARGIN * 2;
        let y = 20;

        // ── Header
        doc.setFillColor(13, 17, 23);
        doc.rect(0, 0, W, 35, 'F');
        doc.setTextColor(88, 166, 255);
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.text('FORENSEEK', MARGIN, 14);
        doc.setFontSize(9);
        doc.setTextColor(139, 148, 158);
        doc.text('AI-Powered Forensic Investigation Platform', MARGIN, 20);
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(13);
        doc.text('OFFICIAL INVESTIGATION BRIEF', MARGIN, 29);
        doc.setTextColor(139, 148, 158);
        doc.setFontSize(8);
        doc.text(`Generated: ${new Date().toLocaleString()}`, W - MARGIN, 29, { align: 'right' });
        y = 45;

        // ── Helper functions
        const sectionTitle = (title, color = [88, 166, 255]) => {
            if (y > 260) { doc.addPage(); y = 20; }
            doc.setFillColor(...color);
            doc.rect(MARGIN, y, usableW, 0.5, 'F');
            y += 3;
            doc.setTextColor(...color);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(title, MARGIN, y);
            y += 6;
            doc.setTextColor(201, 209, 217);
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
        };

        const addText = (text, indent = 0, bold = false) => {
            if (y > 265) { doc.addPage(); y = 20; }
            doc.setFont('helvetica', bold ? 'bold' : 'normal');
            const lines = doc.splitTextToSize(text, usableW - indent);
            doc.text(lines, MARGIN + indent, y);
            y += lines.length * 5;
        };

        const addKeyValue = (key, value, valueColor = [201, 209, 217]) => {
            if (y > 265) { doc.addPage(); y = 20; }
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(139, 148, 158);
            doc.text(key + ':', MARGIN, y);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...valueColor);
            const lines = doc.splitTextToSize(String(value), usableW - 35);
            doc.text(lines, MARGIN + 35, y);
            y += lines.length * 5;
        };

        // ── Section 1: Case Information
        sectionTitle('1. CASE INFORMATION');
        addKeyValue('Case ID', document.getElementById('caseIdIn')?.value || 'N/A');
        addKeyValue('Title', document.getElementById('caseTitleIn')?.value || 'N/A');
        addKeyValue('Report Date', new Date().toLocaleDateString());
        addKeyValue('Pipeline Status', [...PIPELINE.completed].join(' → '));
        y += 4;

        // ── Section 2: Evidence Summary
        sectionTitle('2. EVIDENCE SUMMARY', [63, 185, 80]);
        const sources = ['CCTV Intelligence', 'Voice Intelligence', 'Metadata Intelligence', 'Autopsy Intelligence'];
        sources.forEach(src => {
            const done = PIPELINE.completed.has(src.toLowerCase().split(' ')[0]);
            addKeyValue(src, done ? 'Processed ✓' : 'Not Uploaded', done ? [63, 185, 80] : [139, 148, 158]);
        });
        addKeyValue('Witness Statements', `${sessionWitnessLogs.length} log(s) recorded`);
        y += 4;

        // ── Section 3: AI Scores
        sectionTitle('3. AI CONFIDENCE SCORES', [210, 153, 34]);
        if (dashData && dashData.scores) {
            addKeyValue('Evidence Confidence', `${dashData.scores.evidence_confidence}%`, [88, 166, 255]);
            addKeyValue('Witness Reliability', `${dashData.scores.witness_reliability}%`, [63, 185, 80]);
            addKeyValue('Timeline Consistency', `${dashData.scores.timeline_consistency}%`, [210, 153, 34]);
            addKeyValue('Overall Suspicion Score', `${dashData.scores.overall_suspicion || 'N/A'}%`, [248, 81, 73]);
        } else {
            addText('Dashboard not yet generated. Run the Final Dashboard first.');
        }
        y += 4;

        // ── Section 4: AI Reasoning Trace
        sectionTitle('4. AI REASONING & EXPLAINABILITY', [188, 140, 255]);
        if (dashData && dashData.reasoning_trace) {
            dashData.reasoning_trace.forEach((line, i) => {
                addText(`${i + 1}. ${line}`, 3);
            });
        } else {
            addText('No reasoning trace available. Generate the dashboard first.');
        }
        y += 4;

        // ── Section 5: Contradiction Alerts
        sectionTitle('5. CONTRADICTION ANALYSIS', [248, 81, 73]);
        const contraCards = document.querySelectorAll('#dynamicContradictionsContainer .card');
        if (contraCards.length > 0) {
            contraCards.forEach((card, i) => {
                const heading = card.querySelector('h4')?.innerText || 'Contradiction';
                const desc = card.querySelector('p')?.innerText || '';
                addText(`[${i + 1}] ${heading}`, 0, true);
                if (desc) addText(desc, 5);
                y += 2;
            });
        } else {
            addText('No contradiction data captured. Run the Contradiction Engine first.');
        }
        y += 4;

        // ── Section 6: Event Timeline
        sectionTitle('6. EVENT TIMELINE SUMMARY', [88, 166, 255]);
        const tlItems = document.querySelectorAll('#dynamicGlobalTimeline .timeline-item');
        if (tlItems.length > 0) {
            tlItems.forEach(item => {
                const time = item.querySelector('.tl-time')?.innerText || '';
                const content = item.querySelector('h4')?.innerText || '';
                const source = item.querySelector('p')?.innerText || '';
                if (time || content) {
                    addText(`${time}  —  ${content}`, 0, false);
                    if (source) addText(source, 8);
                    y += 1;
                }
            });
        } else {
            addText('No timeline data. Run the Event Timeline engine first.');
        }
        y += 4;

        // ── Section 7: Witness Statements
        sectionTitle('7. WITNESS STATEMENTS', [63, 185, 80]);
        if (sessionWitnessLogs.length > 0) {
            sessionWitnessLogs.forEach((log, i) => {
                const text = typeof log === 'string' ? log : (log.text || JSON.stringify(log));
                addText(`Statement ${i + 1}:`, 0, true);
                addText(`"${text}"`, 5);
                y += 2;
            });
        } else {
            addText('No witness statements recorded.');
        }
        y += 4;

        // ── Section 8: Forensic Observations
        sectionTitle('8. FORENSIC OBSERVATIONS & NEXT STEPS', [88, 166, 255]);
        const observations = [
            'This report was generated by the FORENSEEK AI Forensic Pipeline.',
            'All evidence was processed through independent AI modules before aggregation.',
            'Contradiction analysis was performed using multi-modal cross-referencing.',
            'AI-generated scores should be validated by a qualified forensic investigator.',
            'This document is for investigative support only and is not a legal document.',
        ];
        observations.forEach(obs => addText('• ' + obs, 3));

        // ── Footer on all pages
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(7);
            doc.setTextColor(100, 100, 100);
            doc.text('FORENSEEK CONFIDENTIAL — AI Investigative Brief', MARGIN, 292);
            doc.text(`Page ${i} of ${totalPages}`, W - MARGIN, 292, { align: 'right' });
        }

        // ── Save
        const caseId = document.getElementById('caseIdIn')?.value || 'FORENSEEK';
        doc.save(`${caseId}_Investigation_Brief_${Date.now()}.pdf`);

    } catch (err) {
        console.error('PDF Export error:', err);
        alert('Error generating PDF. Ensure the Final Dashboard has been generated first.');
    } finally {
        if (btn) {
            btn.innerHTML = '<i class="fa-solid fa-download"></i> Export Full Investigative Brief (PDF)';
            btn.disabled = false;
        }
    }
}
