# KNOWLEDGE GRAPH MODULE DEVELOPMENT INSTRUCTION
# FORENSEEK – Evidence Relationship & Investigative Intelligence Engine

---

# OBJECTIVE

Develop the Knowledge Graph Module for the FORENSEEK platform.

This module acts as the central investigative intelligence engine that connects:
- suspects
- victims
- witnesses
- locations
- timestamps
- CCTV events
- forensic evidence
- objects
- vehicles
- digital metadata

into a unified relationship network.

The module must visually represent evidence relationships and help investigators:
- understand hidden connections
- detect contradictions
- analyze timelines
- correlate multimodal evidence
- navigate investigations interactively

The Knowledge Graph Module should feel like:
# an intelligent forensic investigation reasoning system.

---

# PRIMARY GOAL

Convert fragmented evidence into:
# connected investigative intelligence.

The system must:
- automatically extract entities from uploaded evidence
- create relationship connections
- visualize evidence relationships interactively
- support timeline reasoning
- enable contradiction detection

---

# MODULE NAME

# FORENSEEK Knowledge Graph Engine

Alternative Internal Names:
- Evidence Intelligence Graph
- Investigative Relationship Engine
- Forensic Correlation Network

---

# CORE FUNCTIONALITIES

---

# 1. ENTITY EXTRACTION ENGINE

The system must extract entities from:
- witness transcripts
- CCTV analysis
- GPS metadata
- autopsy reports
- crime scene observations
- evidence files

---

## REQUIRED ENTITY TYPES

### Person Entities
Examples:
- suspect
- victim
- witness
- unidentified person

---

### Object Entities
Examples:
- knife
- mobile phone
- bottle
- bag
- vehicle

---

### Location Entities
Examples:
- parking lot
- warehouse
- entrance gate
- room number
- highway

---

### Event Entities
Examples:
- victim entered area
- gunshot detected
- suspect exited building
- vehicle parked

---

### Time Entities
Examples:
- 10:12 PM
- 11:45 PM
- timestamp metadata

---

# 2. RELATIONSHIP CREATION ENGINE

The system must automatically create relationships between entities.

---

## REQUIRED RELATIONSHIP TYPES

### Person Relationships
Examples:
- Seen Near
- Spoke To
- Followed
- Mentioned By

---

### Object Relationships
Examples:
- Holding
- Near
- Used
- Detected With

---

### Location Relationships
Examples:
- Located At
- Appeared Near
- Entered
- Exited

---

### Timeline Relationships
Examples:
- Before
- After
- During
- Simultaneous

---

# 3. GRAPH VISUALIZATION ENGINE

The frontend must display:
# interactive evidence relationship graphs.

The graph must:
- support zoom
- support dragging
- support clicking nodes
- highlight relationships
- animate connections
- support dark mode UI

---

## NODE TYPES

Different node colors/icons for:
- suspects
- victims
- vehicles
- locations
- evidence
- timestamps

---

## EXAMPLE GRAPH

```text
Victim
   ↓
Found Near
   ↓
Warehouse
   ↓
Seen By
   ↓
CCTV Camera 3
   ↓
Detected Person
   ↓
Suspect
```

---

# 4. CONTRADICTION DETECTION ENGINE

This is one of the most important features.

The graph must compare:
- witness statements
- CCTV timestamps
- GPS metadata
- evidence timelines

and identify contradictions automatically.

---

## EXAMPLE

Witness Statement:
"I left the area at 9 PM."

CCTV:
Subject detected at 10:14 PM.

System Output:
⚠ Contradiction Detected:
Witness statement conflicts with CCTV evidence.

---

## REQUIRED LOGIC

Detect:
- impossible timelines
- conflicting locations
- overlapping events
- inconsistent timestamps

---

# 5. TIMELINE CORRELATION

The graph must connect events chronologically.

The system should automatically generate:
# smart investigative timelines.

---

## EXAMPLE

10:12 PM → Victim enters area

10:18 PM → Suspect detected

10:24 PM → Vehicle appears

10:31 PM → Gunshot detected

10:38 PM → Subject exits area

---

# 6. EVIDENCE LINKING SYSTEM

When investigators click a graph node,
the system should display:
- related CCTV clips
- witness transcript
- timestamps
- images
- metadata
- evidence confidence

---

## EXAMPLE

Click:
"Red Motorcycle"

Display:
- CCTV Camera 2
- Witness mentions red bike
- GPS overlap
- Timeline appearances

---

# 7. AI INSIGHT GENERATION

The graph should generate:
- evidence summaries
- suspicious relationship indicators
- anomaly alerts
- connected evidence observations

---

## EXAMPLE OUTPUTS

- Multiple evidence sources linked to suspect
- Timeline inconsistency observed
- Same vehicle appears at multiple locations
- Witness testimony partially conflicts with CCTV evidence

---

# 8. KNOWLEDGE GRAPH SEARCH

The graph should support:
# natural language investigative search.

---

## EXAMPLES

Search:
"Show all evidence connected to suspect"

Search:
"Find all events after 10 PM"

Search:
"Show vehicles near crime scene"

---

# 9. DASHBOARD INTEGRATION

The Knowledge Graph must integrate with:
- Crime Scene Module
- CCTV Tracking Module
- Witness Intelligence Module
- Timeline Engine
- Risk Scoring Engine
- AI Investigation Assistant

---

# 10. FRONTEND REQUIREMENTS

---

## UI DESIGN

The graph interface must:
- feel futuristic
- dark themed
- cyber intelligence style
- visually premium

---

## RECOMMENDED COLORS

Background:
#0B1120

Cards:
#111827

Accent:
Cyan / Blue

Alert:
Red

---

## REQUIRED PANELS

### Graph Visualization Panel
Interactive graph area

---

### Relationship Details Panel
Shows selected node details

---

### Contradiction Alerts Panel
Displays timeline conflicts

---

### Timeline Panel
Chronological event flow

---

# 11. RECOMMENDED TECHNOLOGIES

---

## FRONTEND

### React.js

### Cytoscape.js
Use for:
- graph visualization
- node interactions
- relationship rendering

Alternative:
React Flow

---

## BACKEND

### FastAPI

---

## DATABASE

Initially:
- JSON
- Python dictionaries

Future:
- Neo4j

---

# 12. BACKEND DATA STRUCTURE

Use simple graph structure initially.

---

## NODE STRUCTURE

```python
{
  "id": "suspect_1",
  "label": "Suspect",
  "type": "person"
}
```

---

## EDGE STRUCTURE

```python
{
  "source": "suspect_1",
  "target": "warehouse_1",
  "relationship": "Seen Near"
}
```

---

# 13. API REQUIREMENTS

---

## REQUIRED APIs

### Upload Evidence API

### Get Graph Data API

### Timeline API

### Contradiction Detection API

### Evidence Linking API

### Search Graph API

---

# 14. DEVELOPMENT STRATEGY

IMPORTANT:
Build the module in phases.

---

# PHASE 1

Build:
- static graph visualization
- dummy nodes
- dummy edges

Goal:
frontend graph UI working.

---

# PHASE 2

Connect:
- backend APIs
- dynamic graph generation

---

# PHASE 3

Add:
- contradiction detection
- timeline correlation
- evidence linking

---

# PHASE 4

Add:
- AI insight generation
- natural language search
- advanced graph animations

---

# 15. IMPORTANT DEVELOPMENT RULES

DO NOT:
- build complex graph neural networks
- build advanced AI reasoning systems
- overcomplicate backend logic
- attempt enterprise-level scalability initially

Instead:
- focus on visually impressive evidence linking
- create believable investigative intelligence
- prioritize demo experience
- optimize for hackathon presentation

---

# 16. HACKATHON DEMO FLOW

Example Demo:

1. Upload witness transcript

2. Upload CCTV metadata

3. Upload GPS data

4. Graph automatically updates

5. Relationships appear visually

6. Contradiction alert triggered

7. Timeline generated

8. Investigator clicks suspect node

9. Related evidence instantly appears

This should feel like:
# AI-powered investigative reasoning.

---

# 17. EXPECTED OUTPUT

The final module should:
- visually connect evidence
- assist investigative reasoning
- detect contradictions
- improve evidence understanding
- generate connected intelligence
- support timeline reconstruction

The system should transform fragmented forensic evidence into:
# explainable investigative relationship intelligence.

---

# 18. FINAL GOAL

The Knowledge Graph Module should become:
# the central intelligence brain of FORENSEEK.

It should provide:
- evidence relationships
- timeline reasoning
- contradiction detection
- connected investigation analysis
- explainable forensic intelligence

while remaining:
- visually impressive
- interactive
- understandable
- realistic for hackathon implementation

```