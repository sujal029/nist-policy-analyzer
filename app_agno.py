import os
import json
import streamlit as st
from docx import Document
import re
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from agno.agent import Agent
from agno.models.groq import Groq

# ✅ Set your Agno + Groq API key
os.environ["GROQ_API_KEY"] = "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"  # Replace if needed

# ✅ Configure Agno Agent
agent = Agent(
    model=Groq(id="llama3-70b-8192"),
    instructions="""
You are a cybersecurity compliance auditor.
Given a NIST control and a company's policy text,
respond strictly in JSON format:
{
  "status": "Fully Implemented | Partially Implemented | Missing",
  "gap_summary": "Short explanation of what's missing",
  "recommendation": "What to add or improve"
}
"""
)

# ✅ Streamlit setup
st.set_page_config(page_title="Agno AI Compliance Agent", layout="centered")
st.title("🤖 Agno-Powered Compliance Agent (NIST 800-171)")
st.markdown("Upload your policy and control files. I’ll help you analyze NIST compliance gaps. 🚀")

# ✅ Read .docx file
def read_policy(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

# ✅ Extract JSON from LLM response
def extract_json(response_text):
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {
                "status": "Error",
                "gap_summary": "Invalid JSON format.",
                "recommendation": response_text
            }
    return {
        "status": "Error",
        "gap_summary": "No JSON found.",
        "recommendation": response_text
    }

# ✅ Generate PDF download
def generate_pdf(data_dict):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Gap Analysis Report")
    p.setFont("Helvetica", 12)
    y -= 30

    for cid, item in data_dict.items():
        text_block = f"{cid} - {item['status']}\nGap: {item['gap_summary']}\nFix: {item['recommendation']}\n"
        for line in text_block.split("\n"):
            if y < 50:
                p.showPage()
                y = height - 40
                p.setFont("Helvetica", 12)
            p.drawString(40, y, line)
            y -= 20

    p.save()
    buffer.seek(0)
    return buffer

# ✅ Sidebar for uploads
with st.sidebar:
    st.header("📁 Upload Files")
    policy_file = st.file_uploader("Upload Company Policy (.docx)", type=["docx"])
    controls_file = st.file_uploader("Upload NIST Controls (.json)", type=["json"])

# ✅ Main app logic
if policy_file:
    policy_text = read_policy(policy_file)

    if controls_file:
        try:
            controls = json.load(controls_file)
        except Exception as e:
            st.error(f"Failed to load controls file: {e}")
            st.stop()
    else:
        st.error("Please upload NIST control file in JSON format.")
        st.stop()

    if st.button("🔍 Run Gap Analysis"):
        st.info("Analyzing policy against NIST controls...")
        results = {}

        for cid, control_text in controls.items():
            prompt = f"""
NIST CONTROL ({cid}):
{control_text}

COMPANY POLICY:
{policy_text}
"""
            try:
                response = agent.run(prompt)
                output = getattr(response, "content", None)
                parsed = extract_json(output) if output else {
                    "status": "Error",
                    "gap_summary": "Empty response from LLM",
                    "recommendation": ""
                }
            except Exception as e:
                parsed = {
                    "status": "Error",
                    "gap_summary": "Agent exception",
                    "recommendation": str(e)
                }

            results[cid] = parsed

        # Show results
        st.success("✅ Gap Analysis Complete")
        for cid, res in results.items():
            st.subheader(f"🔒 {cid} – {res['status']}")
            st.markdown(f"- **Gap**: {res['gap_summary']}")
            st.markdown(f"- **Recommendation**: {res['recommendation']}")

        # Downloads
        st.markdown("---")
        st.download_button("⬇️ Download JSON", data=json.dumps(results, indent=2), file_name="gap_analysis_agno.json", mime="application/json")
        st.download_button("⬇️ Download PDF", data=generate_pdf(results), file_name="gap_analysis_agno.pdf", mime="application/pdf")
else:
    st.info("📑 Upload your policy document to begin.")
