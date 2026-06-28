import re

content = open('index.html', encoding='utf-8').read()

final_dashboard_html = """
            <!-- FINAL DASHBOARD VIEW -->
            <section id="final" class="view">
                <header class="top-bar">
                    <h1><i class="fa-solid fa-chart-pie" style="color:#58a6ff"></i> Final Investigation Dashboard</h1>
                    <div class="case-id" id="finalCaseIdDisplay">CASE #FS-2026-X99</div>
                </header>
                
                <div style="background:rgba(210,153,34,0.1); border:1px solid #d29922; color:#d29922; padding:16px; border-radius:8px; margin-bottom:20px; font-size:0.9rem; line-height:1.5;">
                    <i class="fa-solid fa-circle-info"></i> <strong>INVESTIGATIVE NOTICE:</strong> 
                    This system does not provide absolute legal conclusions. Evidence patterns are consistent with suspicious activity. The following intelligence supports the investigative hypothesis and must be reviewed by authorized personnel.
                </div>

                <div class="dashboard-grid" style="grid-template-columns: 1fr 1fr 1fr; margin-bottom: 20px;">
                    <div class="card stat-card" style="text-align:center;">
                        <div style="font-size:2.5rem; color:#3fb950; font-weight:700;">89%</div>
                        <h3 style="margin-top:10px; font-size:0.9rem; color:#8b949e;">Evidence Confidence Score</h3>
                    </div>
                    <div class="card stat-card" style="text-align:center;">
                        <div style="font-size:2.5rem; color:#d29922; font-weight:700;">74%</div>
                        <h3 style="margin-top:10px; font-size:0.9rem; color:#8b949e;">Witness Reliability Score</h3>
                    </div>
                    <div class="card stat-card" style="text-align:center;">
                        <div style="font-size:2.5rem; color:#f85149; font-weight:700;">61%</div>
                        <h3 style="margin-top:10px; font-size:0.9rem; color:#8b949e;">Timeline Consistency Score</h3>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div class="card">
                        <div class="card-header">
                            <h3><i class="fa-solid fa-magnifying-glass" style="color:#bc8cff"></i> Explainability Engine: Case Summary & Conclusions</h3>
                        </div>
                        <div style="font-size:0.9rem; color:#e6edf3; line-height:1.7; padding-top:10px;">
                            <p><strong>Crime Prediction based on Evidence Patterns:</strong> The evidence strongly suggests a deliberate, coordinated assault followed by movement of the victim. The sequence of metadata overlap and CCTV tracking indicates premeditation.</p>
                            <p style="margin-top:10px;"><strong>Possible Suspect Identification:</strong> Known Associate #1 (Marcus Vance). Connected via Communication Risk Node (Metadata) and CCTV Entity B tracking at the time of the gunshot audio trigger.</p>
                            
                            <h4 style="margin-top:20px; color:#58a6ff; font-size:0.85rem; text-transform:uppercase;">Reasoning Trace (Grounded Evidence):</h4>
                            <ul style="margin-top:10px; color:#8b949e; padding-left:20px;">
                                <li><strong>CCTV Evidence:</strong> Subject #2 is seen leaving the warehouse gate 42 seconds after the gunshot audio classification.</li>
                                <li><strong>Metadata Overlap:</strong> The suspect's device pinged the same cell tower as the victim's device from 10:15 PM to 10:35 PM.</li>
                                <li><strong>Witness Statements:</strong> Audio witness testimony corroborates hearing an argument followed by a loud sound at 10:30 PM.</li>
                                <li><strong>Timeline Correlation:</strong> The communication gap in the victim's phone matches the timeline of the assault recorded on the CCTV feed.</li>
                                <li><strong>Graph Relationships:</strong> The Knowledge Graph connects the victim's last known location directly to the suspect's registered vehicle license plate.</li>
                                <li><strong>Autopsy Observations:</strong> Time of death estimation (10:00 PM - 11:30 PM) perfectly brackets the chronological anomaly. Cause of death (homicide via blunt force) corroborates the defensive wounds and struggle observed.</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div style="display:flex; flex-direction:column; gap:20px;">
                        <div class="card">
                            <div class="card-header">
                                <h3><i class="fa-solid fa-bolt" style="color:#f85149"></i> Contradiction Alerts</h3>
                            </div>
                            <div style="font-size:0.85rem; color:#e6edf3; margin-top:10px; background:rgba(248,81,73,0.1); border-left:3px solid #f85149; padding:10px;">
                                <strong>High Priority:</strong> Witness claims they saw the suspect leaving at 9:00 PM, but Metadata GPS and CCTV confirm presence at 10:31 PM.
                            </div>
                        </div>
                        <div class="card" style="flex:1;">
                            <div class="card-header">
                                <h3><i class="fa-solid fa-layer-group" style="color:#58a6ff"></i> Major Evidence Findings</h3>
                            </div>
                            <ul style="font-size:0.85rem; color:#8b949e; padding-left:20px; margin-top:10px; line-height:1.6;">
                                <li>CCTV Video Tracked (Assault001)</li>
                                <li>Witness Audio Processed</li>
                                <li>Telecom Metadata Extracted</li>
                                <li>Autopsy RAG Indexed</li>
                                <li>Knowledge Graph Connected</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div style="text-align:center; margin-top:40px;">
                    <button class="btn-primary" style="background:#238636; border-color:#2ea043; padding:12px 30px; font-size:1rem; font-weight:600;"><i class="fa-solid fa-download"></i> Export Full Investigative Brief (PDF)</button>
                </div>
            </section>
"""

# Append the final dashboard view right before closing </main>
content = re.sub(r'(</main>)', final_dashboard_html + r'\n\1', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Final view added successfully!')
