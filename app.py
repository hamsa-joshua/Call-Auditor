import streamlit as st
import os
import shutil
import pandas as pd
from dotenv import load_dotenv

# Import our modules
from src.audio_processor import AudioProcessor
from src.chat_normalizer import ChatNormalizer
from src.rag_engine import RagEngine
from src.auditor import Auditor
from src.database_manager import DatabaseManager
from src.reporting import ReportGenerator

# Load env vars
load_dotenv()

# Setup Layout
st.set_page_config(page_title="Support Auditor AI", layout="wide")
st.title("Generative AI Support Auditor")

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("Configuration")
    st.info("Using Gemini API Provider")

    # Check env vars
    env_key = os.getenv("GEMINI_API_KEY")

    if env_key:
        st.success(f"Gemini API Key loaded from environment ✓")
        api_key = env_key
    else:
        api_key = st.text_input(f"Gemini API Key", type="password")

    st.markdown("---")
    manager_email = st.text_input("Manager Email (for alerts)")

    # Initialize classes based on user input or env vars
    gemini_key = api_key if api_key else None

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Run Audit", "Audit History", "Policy Manager"])

# --- Tab 1: Run Audit ---
with tab1:
    st.subheader("New Audit")
    uploaded_file = st.file_uploader("Upload Audio Call or Chat Log", type=['mp3', 'wav', 'txt', 'json'])

    if uploaded_file:
        if not gemini_key:
            st.error("Please provide a Gemini API Key in the sidebar or .env file.")
        else:
            with st.spinner("Initializing system components..."):
                # Save uploaded file safely
                upload_dir = "customer_auditor/data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Identify Type
                is_audio = uploaded_file.name.endswith(('.mp3', '.wav'))
                audit_type = "audio" if is_audio else "chat"

                # 1. Processing
                st.info("Step 1/4: Processing file...")
                transcript_text = ""
                try:
                    if is_audio:
                        processor = AudioProcessor(model_size="base")
                        segments = processor.process_audio(file_path)
                        transcript_text = "\n".join([f"[{s['start']:.1f}s] {s['speaker']}: {s['text']}" for s in segments])
                    else:
                        # Assume chat text
                        with open(file_path, 'r') as f:
                            raw_content = f.read()
                        normalizer = ChatNormalizer()
                        structured = normalizer.normalize_content(raw_content)
                        transcript_text = "\n".join([f"{m['speaker']}: {m['text']}" for m in structured])

                    st.text_area("Transcript Preview", transcript_text, height=150)
                except Exception as e:
                    st.error(f"Processing failed: {e}")
                    st.stop()

                # 2. RAG Retrieval
                st.info("Step 2/4: Retrieving Policy Context...")
                rag = RagEngine(policy_path="customer_auditor/policies/company_policy.txt")

                # Ensure DB exists
                if not os.path.exists(rag.index_path):
                    rag.build_vector_store()

                # Check if we successfully got text (if audio was empty, this might fail)
                if not transcript_text:
                    st.warning("No transcript generated. Check audio quality.")
                    st.stop()

                context_docs = rag.retrieve_context(transcript_text[:1000])
                policy_context = "\n---\n".join(context_docs)

                # 3. LLM Audit
                st.info("Step 3/4: Auditing with LLM...")
                auditor = Auditor(gemini_key=gemini_key)
                audit_result = auditor.audit_interaction(transcript_text, policy_context)

                if "error" in audit_result:
                    st.error(f"Audit Failed: {audit_result['error']}")
                    st.stop()

                # 4. Storage & Reporting
                st.info("Step 4/4: Saving & Reporting...")
                db = DatabaseManager()
                status = db.log_audit(uploaded_file.name, audit_type, audit_result)

                reporter = ReportGenerator()
                pdf_path = reporter.generate_pdf(audit_result, filename=f"report_{uploaded_file.name}.pdf")

                # Move Output based on status
                final_folder = "processed" if status == "Solved" else "violations"
                shutil.copy(pdf_path, f"customer_auditor/data/{final_folder}/{os.path.basename(pdf_path)}")

                # Email
                if status == "Flagged" and manager_email:
                    reporter.send_email_alert(manager_email, pdf_path, audit_result.get("summary"))
                    st.warning(f"Violation Detected! Alert sent to {manager_email}")
                else:
                    st.success("Audit Complete. Compliance standards met.")

                # Display Results
                st.markdown("### Audit Results")
                col1, col2 = st.columns(2)
                col1.metric("Score", f"{audit_result.get('score')}/100")
                col1.metric("Status", status)

                with col2:
                    st.download_button(
                        label="Download PDF Report",
                        data=open(pdf_path, "rb"),
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )

                st.json(audit_result)

# --- Tab 2: History ---
with tab2:
    st.subheader("Audit History")
    db = DatabaseManager()
    rows = db.get_all_audits()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df.drop(columns=["violations"]))
    else:
        st.info("No audits found.")

# --- Tab 3: Policy Manager ---
with tab3:
    st.subheader("Current Policy")
    with open("customer_auditor/policies/company_policy.txt", "r") as f:
        st.code(f.read())
    st.info("To update policies, edit the text file directly in 'customer_auditor/policies/company_policy.txt' and generic RAG will pick it up on next run.")
