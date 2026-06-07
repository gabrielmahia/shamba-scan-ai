# Copyright (c) 2026 Gabriel Mahia / AI Kung Fu LLC. MIT License.
# shamba-scan-ai — Swahili Crop Disease Detection
# Research basis: Mohanty et al. (2016) arXiv:1604.03169 (PlantVillage deep learning)
#   Springer Nature 2026 comprehensive review on AI plant disease detection
#   PlantVillage dataset: 54,306 images, 14 crops, 26 diseases
# First in East Africa: Swahili-native, mobile-first, zero-install crop advisor
# =============================================================================

import streamlit as st
import urllib.request
import json
import base64
import os

st.set_page_config(
    page_title="Shamba Scan AI — Chunguza Ugonjwa wa Mmea",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background: #0a1f0d; }
  .stApp { background: #0a1f0d; }
  .title { font-size:1.6rem; font-weight:800; color:#4caf50; text-align:center; margin:0.5rem 0; }
  .sub   { font-size:0.88rem; color:#81c784; text-align:center; margin-bottom:1.2rem; }
  .card  { background:#0d2b10; border:1px solid #2e7d32; border-radius:10px; padding:14px; margin:8px 0; }
  .demo-tag { background:#e65100; color:#fff; font-size:0.65rem; padding:2px 7px; border-radius:3px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌿 Shamba Scan AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Piga picha ya jani linalougua — tuambie tatizo ni nini · <b>DEMO</b></div>',
            unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
API_KEY = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.warning(
        "⚠️ **Huduma hii bado haijaungwa na msimamizi.**\n\n"
        "Rudi baadaye. / This service is not yet configured in this demo."
    )
    st.stop()

# ── Disease database (synthetic DEMO data — representative, not diagnostic) ──
CROP_INFO = {
    "tomato": {"sw": "Nyanya", "diseases": ["blight ya mapema", "mipasuko ya jani", "virusi"]},
    "maize":  {"sw": "Mahindi", "diseases": ["koga la unga", "smut", "streak virus"]},
    "bean":   {"sw": "Maharagwe", "diseases": ["angular leaf spot", "anthracnose", "bean rust"]},
    "banana": {"sw": "Ndizi", "diseases": ["panama disease", "black sigatoka", "bunchy top"]},
    "coffee": {"sw": "Kahawa", "diseases": ["coffee leaf rust", "CBD (coffee berry disease)", "wilt"]},
}

DISCLAIMER = """
> ⚠️ **DEMO — Synthetic Reference Data**  
> This app provides AI-powered guidance based on visual features.  
> It is **not a substitute for professional agricultural extension advice**.  
> Source: Representative data — not field-validated diagnostics.  
> For certified diagnosis, contact your local KALRO office.
"""

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "📸 Pakia picha ya jani la mmea wako (Take a photo of the sick leaf)",
    type=["jpg","jpeg","png","webp"],
    help="Picha yenye ubora zaidi = jibu bora zaidi"
)
crop_choice = st.selectbox(
    "🌱 Chagua aina ya mmea (Select crop)",
    options=list(CROP_INFO.keys()),
    format_func=lambda x: f"{CROP_INFO[x]['sw']} ({x.title()})"
)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded and st.button("🔍 Chunguza Ugonjwa (Analyze Disease)", type="primary"):
    with st.spinner("Inachambua picha... / Analyzing image..."):
        try:
            img_bytes = uploaded.read()
            img_b64   = base64.b64encode(img_bytes).decode()
            mime_type = uploaded.type or "image/jpeg"
            crop_sw   = CROP_INFO[crop_choice]["sw"]

            system_prompt = f"""You are an expert agricultural extension officer for Kenya/East Africa.
You analyze plant leaf images for diseases. You are analyzing a {crop_choice} ({crop_sw}) leaf.

Respond in this exact JSON format:
{{
  "disease_english": "disease name or 'Healthy'",
  "disease_swahili": "jina la ugonjwa kwa Kiswahili au 'Mmea mzima'",
  "severity": "Low|Medium|High|None",
  "confidence": "High|Medium|Low",
  "symptoms_sw": "dalili zinazoonekana kwa Kiswahili (1-2 sentences)",
  "treatment_sw": "matibabu/hatua za kuchukua kwa Kiswahili (2-3 steps)",
  "prevention_sw": "jinsi ya kuzuia ugonjwa huu (1-2 sentences)",
  "see_expert": true or false
}}

Be concise. Use plain Swahili a farmer understands. If image is unclear, say so honestly.
This is educational demo data — remind user to consult KALRO for official diagnosis."""

            payload = {
                "model": "gemini-2.0-flash",
                "contents": [{
                    "parts": [
                        {"text": f"Analyze this {crop_choice} leaf for diseases. Respond in the JSON format specified."},
                        {"inline_data": {"mime_type": mime_type, "data": img_b64}}
                    ]
                }],
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "generation_config": {"temperature": 0.1, "max_output_tokens": 600}
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                          method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read())

            raw = resp["candidates"][0]["content"]["parts"][0]["text"]
            raw = raw.replace("```json","").replace("```","").strip()
            result = json.loads(raw)

            # Display result
            sev_color = {"None":"#4caf50","Low":"#8bc34a","Medium":"#ff9800","High":"#f44336"}.get(
                result.get("severity","Medium"), "#ff9800")
            disease = result.get("disease_swahili","Haijulikani")
            sev     = result.get("severity","?")
            conf    = result.get("confidence","?")

            st.markdown(f"""
<div class="card">
  <div style="font-size:1.2rem;font-weight:800;color:{sev_color}">{disease}</div>
  <div style="font-size:0.8rem;color:#a5d6a7;margin-top:4px">
    English: {result.get("disease_english","?")} &nbsp;|&nbsp;
    Ukali: <span style="color:{sev_color}">{sev}</span> &nbsp;|&nbsp;
    Uhakika: {conf}
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown("#### 🔎 Dalili (Symptoms)")
            st.info(result.get("symptoms_sw","—"))

            st.markdown("#### 💊 Matibabu (Treatment)")
            st.success(result.get("treatment_sw","—"))

            st.markdown("#### 🛡️ Kuzuia (Prevention)")
            st.info(result.get("prevention_sw","—"))

            if result.get("see_expert"):
                st.warning("⚠️ Wasiliana na afisa wa kilimo wa wilaya yako (KALRO) kwa matibabu zaidi.")

            st.markdown(DISCLAIMER)

        except json.JSONDecodeError:
            st.warning("AI ilijibu kwa muundo usio sahihi. Jaribu tena na picha nyingine.")
        except Exception as e:
            st.error(f"Hitilafu ya mfumo. Tafadhali jaribu tena. / System error: {str(e)[:80]}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("🌍 Shamba Scan AI — East Africa AI Stack · AI Kung Fu LLC · MIT License")
st.caption("Research basis: Mohanty et al. (2016) PlantVillage · DEMO data — consult KALRO for certified diagnosis")
