import streamlit as st
import json
from docx import Document
import google.generativeai as genai
import re
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyChTAGoY9r2pEWvyKVpfrQXkmBkz3po2B4")

# Streamlit page setup
st.set_page_config(page_title="AI Compliance Agent", layout="centered")
st.title("🤖 AI Compliance Agent for NIST 800-171")
st.markdown("Upload your policy document and controls. I’ll find the gaps and suggest fixes — like your personal compliance assistant! 💼")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "results" not in st.session_state:
    st.session_state.results = {}

# Read .docx file
def read_policy(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

# Extract JSON from Gemini response
def extract_json(response_text):
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        raw_json = match.group(0)
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError as e:
            return {"status": "Error", "gap_summary": "Invalid JSON", "recommendation": response_text}
    else:
        return {"status": "Error", "gap_summary": "No JSON found", "recommendation": response_text}

# Auto-generate NIST control summaries if not uploaded
def generate_default_nist_controls(model):
    basic_controls = ["AC-2", "AC-5", "AC-6", "IA-2", "IA-5"]
    controls = {}
    for control_id in basic_controls:
        prompt = f"Summarize NIST 800-171 rev 3 control {control_id} in 3-5 lines suitable for comparing with a company policy."
        response = model.generate_content(prompt)
        controls[control_id] = response.text.strip()
    return controls

# Store to local JSON history
def save_to_local_history(policy_name, results):
    history_path = "upload_history.json"
    history = {}
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = json.load(f)
    history[policy_name] = results
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

# Sidebar
with st.sidebar:
    st.header("📁 Upload Files")
    policy_file = st.file_uploader("Company Policy (.docx)", type=["docx"])
    controls_file = st.file_uploader("NIST Controls (.json)", type=["json"])
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.results = {}

# Main logic
if policy_file:
    policy_text = read_policy(policy_file)
    model = genai.GenerativeModel('models/gemini-1.5-pro-001')

    if controls_file:
        controls = json.load(controls_file)
    else:
        st.warning("⚠️ NIST controls not uploaded. Auto-generating key control summaries with Gemini...")
        controls = generate_default_nist_controls(model)

    user_input = st.chat_input("Ask me to analyze your policy or suggest improvements...")

    # Show previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        reply = ""
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                if "analyze" in user_input.lower() or "gaps" in user_input.lower():
                    results = {}
                    for control_id, control_text in controls.items():
                        prompt = f"""
You are a compliance AI agent. Compare the following company policy against this NIST 800-171 rev 3 control. Respond ONLY in this JSON format (no extra text or markdown):

{{
  "status": "Fully Implemented | Partially Implemented | Missing",
  "gap_summary": "Short explanation of what's missing",
  "recommendation": "What to add/improve"
}}

NIST CONTROL ({control_id}):
{control_text}

COMPANY POLICY:
{policy_text}
"""
                        try:
                            response = model.generate_content(prompt)
                            parsed = extract_json(response.text)
                            results[control_id] = parsed
                        except Exception as e:
                            results[control_id] = {
                                "status": "Error",
                                "gap_summary": "Gemini API error",
                                "recommendation": str(e)
                            }

                    st.session_state.results = results
                    save_to_local_history(policy_file.name, results)

                    reply = "### 📟 Here are the analyzed gaps:\n"
                    for cid, result in results.items():
                        reply += f"\n**{cid} - {result['status']}**"
                        reply += f"\n- **Gap:** {result['gap_summary']}"
                        reply += f"\n- **Fix:** {result['recommendation']}\n"
                elif "suggest" in user_input.lower():
                    reply = "Here’s a sample improvement you could add to your policy:\n\n"
                    reply += "> All privileged accounts must use multi-factor authentication (MFA) and should be disabled automatically after 30 days of inactivity."
                else:
                    reply = "Try asking me to 'analyze gaps' or 'suggest improvements' based on your policy."

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("📅 Upload the company policy (.docx) to begin.")
