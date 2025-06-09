import json
from docx import Document
import google.generativeai as genai

# Configure your API key
genai.configure(api_key="AIzaSyChTAGoY9r2pEWvyKVpfrQXkmBkz3po2B4")

def read_policy(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

policy_path = r"C:\Users\baiss\OneDrive\Desktop\portfolio\ai agent 2.0\Security-Policy-2-Account-Management.docx"
controls_path = r"C:\Users\baiss\OneDrive\Desktop\portfolio\ai agent 2.0\nist_controls.json"

policy_text = read_policy(policy_path)

with open(controls_path, "r", encoding="utf-8") as f:
    controls = json.load(f)

model = genai.GenerativeModel('models/gemini-1.5-pro-001')

results = {}

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

with open("gaps_report_gemini.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("✅ Analysis complete! Check 'gaps_report_gemini.json' for results.")
