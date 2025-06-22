# 🤖 NIST Policy Analyzer - AI Compliance Agent

A smart Streamlit-based AI tool that analyzes your company’s policy documents against the **NIST 800-171 Rev. 3** cybersecurity standard and identifies **compliance gaps** along with **actionable suggestions**.

---

## 🚀 Features

- 🔍 **Automatic Gap Analysis**: Compare policy documents with NIST 800-171 controls.
- 📂 **Supports DOCX Uploads**: Upload company policy in `.docx` format.
- 🤖 **Powered by Gemini AI**: Uses Gemini Pro model to generate gap summaries and recommendations.
- ⚖️ **Uses Full NIST 800-171 Rev. 3 Controls**: No shortcuts — evaluates against all relevant standards.
- 💬 **Interactive Chat Interface**: Ask for suggestions, gaps, or recommendations.
- 📤 **Export Report**: Download results as `.json` or `.pdf`.

## 🧠 How It Works

1. Upload your company’s **policy document**.
2. (Optional) Upload a `.json` file of NIST controls — or let the app auto-generate summaries.
3. Click **Analyze** to identify gaps.
4. Get clear, structured feedback:
   - ✅ Status
   - 🕳️ Gap Summary
   - 🛠️ Recommendation
5. Download the analysis as PDF or JSON.

---

## 🛠️ Tech Stack

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)
- [reportlab](https://pypi.org/project/reportlab/) (for PDF generation)
- [docx](https://pypi.org/project/python-docx/) (for reading policy files)

---

## 📂 File Structure

nist-policy-analyzer/
│
├── app.py # Streamlit app
├── upload_history.json # Stores local run history
├── sample_controls.json # Sample NIST controls (optional)
├── requirements.txt # Python dependencies
├── README.md # You're reading it :)

yaml
Copy
Edit

---

## 📦 Installation

```bash
git clone https://github.com/sujal029/nist-policy-analyzer.git
cd nist-policy-analyzer
pip install -r requirements.txt
streamlit run app.py
📄 Sample Policy
You can test the tool with the sample policy file given in the assignment. Or upload any .docx company policy.

👨‍💼 Author
Sujal Singh Bais
LinkedIn: linkedin.com/in/sujalsingh07
Email: baissujal292@gmail.com

💼 Disclaimer
This is a student-built project designed for educational and job evaluation purposes. Please validate results with a security expert for production use.

⭐️ Show Your Support
If you like this project:

Star the repo 🌟

Share your feedback 💬

Suggest improvements 🛠️
