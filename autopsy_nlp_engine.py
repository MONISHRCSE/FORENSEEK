"""
autopsy_nlp_engine.py
RAG-Powered Autopsy Intelligence Module for FORENSEEK
Uses: pdfplumber (PDF), python-docx (DOCX), sentence-transformers (embeddings), numpy (similarity)
No external LLM API required — pure retrieval-augmented summarization.
"""

import os
import re
import json
import numpy as np

# ─── LAZY IMPORTS (heavy models only loaded when needed) ────────────────────
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading sentence-transformer model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


class AutopsyNLPEngine:
    def __init__(self):
        print("Initializing Autopsy NLP Engine (RAG)...")
        self.report_text  = ""
        self.chunks       = []
        self.embeddings   = None   # numpy array [N, dim]
        self.report_title = "No report loaded"
        self.summary      = {}
        self.chat_history = []
        self._load_demo_report()

    # ─── DEMO REPORT ──────────────────────────────────────────────────────────
    def _load_demo_report(self):
        demo = """
FORENSIC AUTOPSY REPORT
Case ID: FS-2026-X99 | Prepared by: Dr. R. Sharma, MD | Date: 09-May-2026

SECTION 1 – IDENTIFICATION
The decedent is a male individual, approximately 35–45 years of age. Identity confirmed via dental records.
Body was discovered at the Warehouse District, Gate 4, at approximately 11:10 PM on 08-May-2026.

SECTION 2 – EXTERNAL EXAMINATION
1. Multiple lacerations observed on the posterior cranial region (back of head).
2. Bruising consistent with blunt force trauma noted on the left temporal region.
3. Defensive wound patterns observed on both forearms — indicative of a struggle prior to death.
4. No evidence of firearm injury.
5. Ligature marks observed on the wrists, consistent with restraint prior to death.

SECTION 3 – INTERNAL EXAMINATION
1. Severe subdural hematoma detected — bleeding between the skull and brain surface.
2. Cerebral edema (brain swelling) present, consistent with repeated blunt force impacts.
3. Multiple rib fractures — ribs 4, 5, and 6 on the left side fractured.
4. Internal hemorrhage detected in the abdominal cavity.
5. Liver contusion observed — consistent with high-impact trauma.

SECTION 4 – TOXICOLOGY
Blood alcohol content: 0.02% — within normal limits.
No controlled substances detected.
No evidence of poisoning.

SECTION 5 – TIME OF DEATH ESTIMATION
Based on body temperature, rigor mortis, and liver mortis:
Estimated time of death: between 10:00 PM and 11:30 PM on 08-May-2026.
This estimate is consistent with the CCTV timestamp at 10:31 PM (gunshot audio trigger detected).

SECTION 6 – CAUSE AND MANNER OF DEATH
Primary cause of death: Severe cranial trauma leading to acute subdural hematoma.
Secondary contributing factor: Internal hemorrhage.
Manner of death: Homicide.

SECTION 7 – FORENSIC OBSERVATIONS
1. The injury pattern is consistent with repeated blunt force applied by a heavy object.
2. Defensive wounds indicate the victim was conscious during initial assault.
3. Restraint marks suggest the victim was immobilized at some point.
4. The abdominal trauma may be indicative of a secondary weapon or stomping force.
5. No evidence of sexual assault.

SECTION 8 – FORENSIC CONCLUSIONS
This report concludes that death occurred as a result of deliberate and repeated blunt force trauma.
The estimated TOD of 10:00 PM – 11:30 PM is consistent with available physical and electronic evidence.
This report is submitted for investigative purposes only and does not constitute a legal determination.
"""
        self.report_title = "Demo Autopsy Report – Case FS-2026-X99"
        self._process_text(demo.strip())

    # ─── FILE PARSING ──────────────────────────────────────────────────────────
    def load_file(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        print(f"Parsing autopsy file: {file_path}")
        text = ""
        if ext == ".pdf":
            text = self._parse_pdf(file_path)
        elif ext in (".docx", ".doc"):
            text = self._parse_docx(file_path)
        elif ext == ".txt":
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported format: {ext}")

        self.report_title = os.path.basename(file_path)
        self._process_text(text)

    def _parse_pdf(self, path):
        import pdfplumber
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text

    def _parse_docx(self, path):
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # ─── TEXT CHUNKING ─────────────────────────────────────────────────────────
    def _process_text(self, text: str):
        self.report_text = text
        # Split on blank lines or numbered sections
        raw_chunks = re.split(r'\n{2,}|(?=SECTION \d+)', text)
        self.chunks = [c.strip() for c in raw_chunks if len(c.strip()) > 40]
        print(f"  → {len(self.chunks)} chunks created")
        # Build embeddings
        model = get_embedding_model()
        self.embeddings = model.encode(self.chunks, show_progress_bar=False, batch_size=16)
        # Auto-generate summary
        self._build_summary()
        self.chat_history = []

    # ─── COSINE SIMILARITY RETRIEVAL ──────────────────────────────────────────
    def _retrieve(self, query: str, top_k: int = 3):
        model = get_embedding_model()
        q_emb = model.encode([query])[0]
        # Cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb)
        norms = np.where(norms == 0, 1e-8, norms)
        sims  = (self.embeddings @ q_emb) / norms
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [(self.chunks[i], float(sims[i])) for i in top_idx]

    # ─── Q&A ENGINE ────────────────────────────────────────────────────────────
    def ask(self, question: str) -> dict:
        if not self.chunks:
            return {"answer": "No report loaded. Please upload an autopsy report first.", "sources": []}

        results = self._retrieve(question, top_k=3)

        # Build a formatted answer from the top retrieved chunk
        top_chunk, top_score = results[0]

        if top_score < 0.2:
            return {
                "answer": "I am a forensic AI assistant. I can only answer questions related to the loaded autopsy report. Please ask about injuries, cause of death, or toxicology.",
                "sources": []
            }

        # Simplify medical terms if needed
        simplified = self._simplify(top_chunk)

        # Compose answer
        answer = f"{simplified}"

        sources = []
        for chunk, score in results:
            if score < 0.15: continue
            # Determine section heading
            header = self._detect_section(chunk)
            sources.append({
                "text":       chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "section":    header,
                "confidence": round(score * 100),
            })

        # Add to chat history
        self.chat_history.append({"role": "investigator", "text": question})
        self.chat_history.append({"role": "ai",           "text": answer})

        return {"answer": answer, "sources": sources}

    def _detect_section(self, text):
        m = re.search(r'SECTION \d+.*', text)
        return m.group(0)[:50] if m else "Report Content"

    # ─── MEDICAL TERM SIMPLIFIER ───────────────────────────────────────────────
    SIMPLIFICATIONS = {
        r"subdural hematoma":       "bleeding between the skull and brain surface",
        r"cerebral edema":          "brain swelling",
        r"laceration":              "deep cut",
        r"hemorrhage":              "heavy internal bleeding",
        r"contusion":               "bruising",
        r"blunt force trauma":      "injury caused by a heavy object",
        r"rigor mortis":            "post-death muscle stiffening",
        r"livor mortis":            "skin discolouration after death",
        r"cranial":                 "skull/head",
        r"temporal region":         "side of the head near the temple",
        r"posterior cranial region": "back of the head",
        r"ligature marks":          "marks from binding/restraint",
        r"defensive wounds":        "injuries showing the victim tried to protect themselves",
        r"homicide":                "death caused by another person",
        r"toxicology":              "drug/poison test results",
    }
    def _simplify(self, text):
        for medical, plain in self.SIMPLIFICATIONS.items():
            text = re.sub(medical, f"{medical} ({plain})", text, flags=re.IGNORECASE, count=1)
        return text

    # ─── AUTO SUMMARY BUILDER ─────────────────────────────────────────────────
    def _build_summary(self):
        # Extract key forensic findings using keyword-based retrieval
        def q(query): return self._retrieve(query, top_k=1)[0][0][:250] if self.chunks else "N/A"

        self.summary = {
            "cause_of_death":  q("cause of death manner"),
            "injuries":        q("injuries trauma wounds lacerations"),
            "time_of_death":   q("time of death estimate TOD"),
            "toxicology":      q("toxicology alcohol substance poison"),
            "key_findings": [
                kf for kf in [
                    self._extract_bullet("defensive wound", "Defensive wounds observed — victim was conscious during attack"),
                    self._extract_bullet("restraint|ligature", "Ligature/restraint marks detected"),
                    self._extract_bullet("blunt force", "Blunt force trauma confirmed"),
                    self._extract_bullet("internal hemorrhage|hematoma", "Internal bleeding identified"),
                    self._extract_bullet("homicide", "Manner of death: Homicide"),
                ] if kf
            ]
        }

    def _extract_bullet(self, pattern, label):
        if re.search(pattern, self.report_text, re.IGNORECASE):
            return label
        return None

    # ─── GETTERS ─────────────────────────────────────────────────────────────
    def get_summary(self):     return self.summary
    def get_chat_history(self):return self.chat_history
    def get_report_text(self): return self.report_text
    def get_chunks(self):      return self.chunks

    def reset(self):
        self.report_text = ""
        self.chunks = []
        self.embeddings = None
        self.summary = {}
        self.chat_history = []
        self.report_title = "No report loaded"
        self._load_demo_report()


if __name__ == "__main__":
    engine = AutopsyNLPEngine()
    print("Summary:", json.dumps(engine.get_summary(), indent=2))
    print("\nAsk:", engine.ask("What injuries were found?"))
