import sys
import os

# --- CRITICAL FIX FOR CLOUD RUN ---
# This must be the very first thing, BEFORE importing from 'services'
# It tells Python to look one directory up to find the 'services' folder.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, ".") 
# ----------------------------------

import streamlit as st
from datetime import datetime, timezone
import json
import uuid
from dotenv import load_dotenv

# Now we can safely import from services because the path is fixed
from services.gemini_client import analyze_image, analyze_text
from services.web_scraper import scrape_url_text
from workers.schema_validator import validate_review_doc
from workers.firestore_real import save_review_to_firestore
from workers.bigquery_real import insert_review_to_bigquery
from workers.bq_mapper import map_doc_to_bq_row

# Load .env file
load_dotenv()

# -------- Configuration --------------------------------
USE_REAL_GEMINI = os.environ.get("USE_REAL_GEMINI", "false").lower() == "true"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", None)

if USE_REAL_GEMINI and not GEMINI_API_KEY:
    st.error("CRITICAL: GEMINI_API_KEY is missing.")
    st.stop()

# ----------------- Helper functions --------------------------------
def build_firestore_doc(gemini_result: dict, source_type: str):
    now = datetime.now(timezone.utc).isoformat()
    review_id = f"local-{uuid.uuid4().hex[:8]}"
    analysis = gemini_result.get("analysis", {}) or {}
    extracted_text = gemini_result.get("extracted_text") or ""
    model = gemini_result.get("model", "mock")
    doc = {
        "review_id": review_id,
        "source": source_type,
        "user_id_hash": None,
        "raw_text": extracted_text,
        "extracted_text": extracted_text,
        "analysis": analysis,
        "image_gcs_path": None,
        "language": "en",
        "model": model,
        "processing_latency_ms": gemini_result.get("processing_latency_ms", None),
        "created_at": now,
        "processed_at": now,
        "metadata": {"upload_method": "local_ui"}
    }
    return doc

def save_local_doc(doc: dict, dirpath: str) -> str:
    fname = f"{doc['review_id']}.json"
    path = os.path.join(dirpath, fname)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
    return path

# ----------------- UI --------------------------------
st.set_page_config(page_title="Consumer Sense AI", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        background: -webkit-linear-gradient(45deg, #4285F4, #34A853, #FBBC05, #EA4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stExpander { border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    .metric-box { background-color: #f9f9f9; padding: 10px; border-radius: 5px; text-align: center; }
    
    .sentiment-positive { color: #0F9D58; font-weight: bold; }
    .sentiment-negative { color: #D93025; font-weight: bold; }
    .sentiment-neutral { color: #5F6368; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Consumer Sense AI — Product Insights 🚀</div>', unsafe_allow_html=True)

if USE_REAL_GEMINI:
    st.caption(f"🟢 Real Gemini Pipeline Active")
else:
    st.warning("🟡 Mock Mode Active")

col1, col2 = st.columns([1, 2])
storage_dir = os.path.join(os.getcwd(), "examples", "saved")
os.makedirs(storage_dir, exist_ok=True)

with col1:
    st.subheader("Input Source")
    mode = st.radio("Select Input:", ["Screenshot (image)", "Raw text", "Web URL"], label_visibility="collapsed")
    
    uploaded_files = [] 
    raw_text = ""
    url_input = ""

    if mode == "Screenshot (image)":
        uploaded_files = st.file_uploader("Upload Review Screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        if uploaded_files:
            st.caption(f"{len(uploaded_files)} file(s) selected.")
    elif mode == "Raw text":
        raw_text = st.text_area("Paste Reviews", height=250, placeholder="Paste one or more reviews here...")
    else:
        url_input = st.text_input("Enter Product/Blog URL", placeholder="https://...")
        st.info("ℹ️ Scrapes visible text.")

    analyze_clicked = st.button("Generate Product Insights", type="primary", use_container_width=True)

with col2:
    if "last_result" in st.session_state and st.session_state["last_result"] is not None:
        r = st.session_state["last_result"]
        analysis = r.get("analysis", {})
        
        st.subheader("Strategic Analysis")
        if "overall_summary" in analysis and analysis["overall_summary"]:
            st.info(f"**Executive Summary:** {analysis['overall_summary']}")

        rich_reviews = analysis.get("rich_reviews", [])

        if rich_reviews:
            st.write(f"**Detected {len(rich_reviews)} distinct review(s)**")
            for idx, item in enumerate(rich_reviews):
                meta = item.get("metadata", {})
                anl = item.get("analysis", {})
                
                sent = anl.get('sentiment', 'Neutral')
                sent_lower = sent.lower()
                color_class = "sentiment-neutral"
                if "positive" in sent_lower: color_class = "sentiment-positive"
                elif "negative" in sent_lower: color_class = "sentiment-negative"

                label = f"Review #{idx+1}"
                if meta.get("username"): label += f" | 👤 {meta['username']}"
                if meta.get("rating"): label += f" | ⭐ {meta['rating']}"
                
                with st.expander(label, expanded=(idx==0)):
                    if anl.get("actionable_advice"):
                        st.markdown(f"💡 **Actionable Advice:** :green-background[{anl['actionable_advice']}]")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**🔴 Pain Points:**")
                        for p in anl.get("pain_points", []): st.write(f"- {p}")
                    with c2:
                        st.markdown("**🟢 Feature Requests:**")
                        for f in anl.get("feature_requests", []): st.write(f"- {f}")
                    
                    st.divider()
                    st.markdown(f"**Sentiment:** <span class='{color_class}'>{sent}</span> | **Date:** {meta.get('date', 'N/A')}", unsafe_allow_html=True)
        else:
            st.markdown("#### 🔍 Strategic Product Overview")
            st.caption("No individual user reviews detected. Showing analysis of product description/marketing text.")
            
            advice = analysis.get("top_level_advice") 
            pains = analysis.get("top_level_pains", [])
            features = analysis.get("top_level_features", [])
            
            if not advice and not pains:
                st.warning("Analysis structure mismatch. Showing raw output for debugging:")
                st.json(analysis)
            else:
                if advice: st.markdown(f"💡 **Strategic Recommendation:** :green-background[{advice}]")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**⚠️ Potential Limitations:**")
                    for p in pains: st.write(f"- {p}")
                with c2:
                    st.markdown("**✨ Key Selling Points:**")
                    for f in features: st.write(f"- {f}")

        st.divider()
        st.subheader("Pipeline Integration")
        source_map = {"Screenshot (image)": "mobile_app_screenshot", "Raw text": "manual_text", "Web URL": "web_scrape"}
        firestore_doc = build_firestore_doc(r, source_map.get(mode, "manual"))
        ok, errs = validate_review_doc(firestore_doc)
        if ok:
            c_a, c_b, c_c = st.columns(3)
            if c_a.button("💾 Save JSON"):
                save_local_doc(firestore_doc, storage_dir); st.toast("Saved!")
            if c_b.button("🔥 Save Firestore"):
                st.write(save_review_to_firestore(firestore_doc, test_mode=True))
            if c_c.button("📊 Save BigQuery"):
                from workers.bigquery_store import insert_review_to_bigquery as insert_bq_mock
                st.write(insert_bq_mock(map_doc_to_bq_row(firestore_doc), test_mode=True))
        else:
            st.error(f"Schema Validation Failed: {errs}")
    else:
        st.info("👈 Select an input source to begin.")

if analyze_clicked:
    st.session_state["last_result"] = None
    with st.spinner("🤖 Gemini 2.5 is analyzing product feedback..."):
        try:
            if mode == "Screenshot (image)":
                if uploaded_files:
                    image_data_list = [f.read() for f in uploaded_files]
                    st.session_state["last_result"] = analyze_image(image_data_list, test_mode=False)
                else:
                    st.warning("Please upload at least one image.")
            elif mode == "Raw text":
                if raw_text.strip():
                    st.session_state["last_result"] = analyze_text(raw_text, test_mode=False)
                else:
                    st.warning("Please enter text.")
            elif mode == "Web URL":
                if url_input.strip():
                    scraped = scrape_url_text(url_input)
                    if not scraped: st.error("Could not extract text.")
                    else: st.session_state["last_result"] = analyze_text(scraped, test_mode=False)
                else:
                    st.warning("Please enter a URL.")
            
            if st.session_state["last_result"]:
                st.rerun()
        except Exception as e:
            st.error(f"Pipeline Error: {e}")