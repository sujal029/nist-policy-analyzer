import streamlit as st
import json
from docx import Document
import google.generativeai as genai
import re
import os

# ✅ Configure Gemini API
genai.configure(api_key="AIzaSyC_4R9j_uqmPZC4LAlEHTl9fqPn1wFDCm4")  # Replace with your actual key

# ✅ Streamlit page setup
st.set_page_config(page_title="AI Compliance Agent", layout="centered")
st.title("🤖 AI Compliance Agent for NIST 800-171")
st.markdown("Upload your policy document and controls. I’ll find the gaps and suggest fixes — like your personal compliance assistant! 💼")

# ✅ Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "results" not in st.session_state:
    st.session_state.results = {}

# ✅ Read .docx file
def read_policy(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

# ✅ Extract JSON from Gemini response
def extract_json(response_text):
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        raw_json = match.group(0)
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            return {
                "status": "Error",
                "gap_summary": "Invalid JSON format received.",
                "recommendation": response_text
            }
    return {
        "status": "Error",
        "gap_summary": "No JSON structure found in response.",
        "recommendation": response_text
    }

# ✅ Generate fallback controls
def generate_default_nist_controls(model):
    basic_controls = ["AC-2", "AC-5", "AC-6", "IA-2", "IA-5"]
    ctrls = {}
    for cid in basic_controls:
        prompt = f"Summarize NIST 800-171 rev 3 control {cid} in 3-5 lines suitable for comparing with a company policy."
        resp = model.generate_content(prompt)
        ctrls[cid] = resp.text.strip()
    return ctrls

# ✅ Save to local history
def save_to_local_history(policy_name, results):
    history_path = "upload_history.json"
    hist = {}
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            hist = json.load(f)
    hist[policy_name] = results
    with open(history_path, "w") as f:
        json.dump(hist, f, indent=2)

# ✅ Sidebar
with st.sidebar:
    st.header("📁 Upload Files")
    policy_file = st.file_uploader("Company Policy (.docx)", type=["docx"])
    controls_file = st.file_uploader("NIST Controls (.json)", type=["json"])
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.results = {}

# ✅ Main logic
if policy_file:
    policy_text = read_policy(policy_file)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    st.session_state.messages.append({"role": "system", "content": "You are a compliance AI agent."})
    st.session_state.messages.append({"role": "user", "content": f"Analyzing    policy: {policy_file.name}"})   # Log the uploaded policy file name
  # Correct model name

    # ---- Safe JSON load with type-check ----
    if controls_file:
        try:
            controls = json.load(controls_file)
            if not isinstance(controls, dict):
                st.error("Uploaded JSON must be an object mapping control_id→control_text.")
                controls = {}
        except Exception as e:
            st.error(f"Failed to load JSON: {e}")
            controls = {}
    else:
        st.warning("⚠️ No controls uploaded; generating sample controls...")
        controls = generate_default_nist_controls(model)

    user_input = st.chat_input("Ask me to analyze your policy or suggest improvements...")

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # On new input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        reply = ""
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                if "analyze" in user_input.lower() or "gaps" in user_input.lower():
                    results = {}
                    for cid, ctext in controls.items():
                        prompt = f"""
You are a compliance AI agent. Compare the following company policy against this NIST 800-171 rev 3 control. Respond ONLY in this JSON format:

{{
  "status": "Fully Implemented | Partially Implemented | Missing",
  "gap_summary": "Short explanation of what's missing",
  "recommendation": "What to add/improve"
}}

NIST CONTROL ({cid}):
{ctext}

COMPANY POLICY:
{policy_text}
"""
                        try:
                            resp = model.generate_content(prompt)
                            results[cid] = extract_json(resp.text)
                        except Exception as e:
                            results[cid] = {
                                "status": "Error",
                                "gap_summary": "Gemini API error",
                                "recommendation": str(e)
                            }
                    st.session_state.results = results
                    save_to_local_history(policy_file.name, results)

                    # build reply markdown
                    reply = "### 📟 Compliance Gap Report:\n"
                    for cid, res in results.items():
                        reply += f"\n**{cid} – {res['status']}**\n"
                        reply += f"- Gap: {res['gap_summary']}\n"
                        reply += f"- Fix: {res['recommendation']}\n"
                else:
                    reply = "Try asking me to 'analyze gaps' or 'suggest improvements'."

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("📅 Upload the company policy (.docx) to begin.")
