import os
import json
from docx import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyC_4R9j_uqmPZC4LAlEHTl9fqPn1wFDCm4"  # 🔐 Replace with your actual key

# Load policy from .docx
def read_policy(file_path):
    doc = Document(file_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

# Extract JSON from model response
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            return {"control_id": "unknown", "covered": "no", "suggestion": "Invalid JSON"}
    return {"control_id": "unknown", "covered": "no", "suggestion": "No JSON found"}

# Load JSON controls
def load_controls(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Setup LangChain LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.3
)

# Define LangChain prompt template
template = """
You are a cybersecurity compliance auditor.

You are given:
1. A NIST control: "{control_text}"
2. The following company policy paragraphs:
{policy_text}

Task:
- Determine whether the policy addresses this control.
- If NOT, mark it as a gap and provide a policy suggestion.

Respond strictly in JSON format:
{{
  "control_id": "{control_id}",
  "covered": "yes" | "no",
  "suggestion": "..."
}}
"""

prompt = PromptTemplate(
    input_variables=["control_id", "control_text", "policy_text"],
    template=template
)

# Build LangChain chain
chain = LLMChain(llm=llm, prompt=prompt)

# 🔁 Main logic
def analyze_controls(policy_text, controls):
    results = {}
    for control_id, control_text in controls.items():
        try:
            response = chain.run({
                "control_id": control_id,
                "control_text": control_text,
                "policy_text": policy_text
            })
            results[control_id] = extract_json(response)
        except Exception as e:
            results[control_id] = {
                "control_id": control_id,
                "covered": "no",
                "suggestion": f"LangChain Error: {str(e)}"
            }
    return results

# ✅ Main entry
if __name__ == "__main__":
    # Edit paths as needed
    policy_path = r"C:\Users\baiss\OneDrive\Desktop\portfolio\ai agent 2.0\Security-Policy-2-Account-Management.docx"
    controls_path = r"C:\Users\baiss\OneDrive\Desktop\portfolio\ai agent 2.0\nist_controls.json"

    print("📄 Loading policy and controls...")
    policy_text = read_policy(policy_path)
    controls = load_controls(controls_path)

    print("⚙️ Running LangChain + Gemini...")
    results = analyze_controls(policy_text, controls)

    with open("gap_analysis_langchain.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("✅ Done! Results saved in 'gap_analysis_langchain.json'")
