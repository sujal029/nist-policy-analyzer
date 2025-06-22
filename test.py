import google.generativeai as genai

genai.configure(api_key="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")

model = genai.GenerativeModel("gemini-pro")  # ✅ Works only with v1+ API
response = model.generate_content("Say hello")

print(response.text)
