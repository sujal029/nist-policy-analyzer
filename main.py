import os
import json
import re
from docx import Document
from agno.agent import Agent
from agno.models.groq import Groq

# ✅ Set your Agno + Groq API key
os.environ["GROQ_API_KEY"] = "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"

# ✅ Load policy from DOCX
def read_policy(file_path):
    doc = Document(file_path)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

# ✅ Extract JSON from model response
def extract_json(text, control_id):
    if not isinstance(text, str):
        return {
            "control_id": control_id,
            "covered": "no",
            "suggestion": "Error: model response was not a string"
        }

    try:
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            data["control_id"] = control_id  # Force correct control ID
            return data
        else:
            return {
                "control_id": control_id,
                "covered": "no",
                "suggestion": "No JSON found in model response"
            }
    except Exception as e:
        return {
            "control_id": control_id,
            "covered": "no",
            "suggestion": f"Invalid JSON: {str(e)}"
        }

# ✅ Load NIST controls
def load_controls(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ Create Agno agent
audit_agent = Agent(
    model=Groq(id="llama3-70b-8192"),
    instructions="""
You are a cybersecurity compliance auditor.
Given a NIST control and a company's policy text,
respond strictly in JSON format:
{
  "control_id": "<control_id>",
  "covered": "yes" or "no",
  "suggestion": "<...>"
}
"""
)

# ✅ Analyze controls
def analyze_controls(policy_text, controls):
    results = {}

    for control_id, control_text in controls.items():
        prompt = f"NIST Control [{control_id}]:\n{control_text}\n\nPolicy Text:\n{policy_text}"
        try:
            # First attempt
            response = audit_agent.run(prompt)
            output = getattr(response, "content", None)

            # Retry if needed
            if output is None or not isinstance(output, str):
                print(f"🔁 Retrying {control_id} due to invalid output...")
                response = audit_agent.run(prompt)
                output = getattr(response, "content", None)

            # Fallback if still invalid
            if output is None or not isinstance(output, str):
                output = json.dumps({
                    "control_id": control_id,
                    "covered": "no",
                    "suggestion": "Fallback: model did not return valid string"
                })

            # Log raw model output
            with open("raw_llm_outputs.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n--- Control ID: {control_id} ---\n{repr(output)}")

            # Extract valid JSON response
            results[control_id] = extract_json(output, control_id)

        except Exception as e:
            results[control_id] = {
                "control_id": control_id,
                "covered": "no",
                "suggestion": f"Error: {str(e)}"
            }

    return results

# ✅ Run everything
if __name__ == "__main__":
    policy_text = read_policy(r"D:\nist policy\Security-Policy-2-Account-Management.docx")
    controls = load_controls(r"D:\nist policy\nist_controls.json")
    results = analyze_controls(policy_text, controls)

    with open("gap_analysis_agno.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("✅ Done! Results saved to 'gap_analysis_agno.json'")
