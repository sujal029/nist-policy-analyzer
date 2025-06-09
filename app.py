import streamlit as st
import json
from docx import Document
import google.generativeai as genai

genai.configure(api_key="AIzaSyChTAGoY9r2pEWvyKVpfrQXkmBkz3po2B4")

page_bg_img = '''
<style>
body {
background-image: url("https://dutton.psu.edu/sites/default/files/2023-03/AdobeStock_566275368.jpeg");
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}
.stApp {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 2rem;
    border-radius: 10px;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

def read_policy(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

st.title("NIST Controls vs Company Policy Analyzer")

policy_file = st.file_uploader("Upload Company Policy (DOCX)", type=["docx"])
controls_file = st.file_uploader("Upload NIST Controls JSON", type=["json"])

results = {}

if policy_file and controls_file:
    policy_text = read_policy(policy_file)
    controls = json.load(controls_file)

    model = genai.GenerativeModel('models/gemini-1.5-pro-001')

    if st.button("Run Analysis"):
        with st.spinner("Analyzing..."):
            for control_id, control_text in controls.items():
                prompt = f"""
Compare this NIST Control to the company's policy.

NIST CONTROL ({control_id}):
{control_text}

COMPANY POLICY:
{policy_text}

Is this control fully implemented, partially implemented, or missing? Justify your response.
"""
                try:
                    response = model.generate_content(prompt)
                    results[control_id] = response.text
                except Exception as e:
                    results[control_id] = f"Error: {str(e)}"

if results:
    st.success("✅ Analysis complete!")
    for control_id, analysis in results.items():
        with st.expander(f"Control {control_id}"):
            st.write(analysis)
