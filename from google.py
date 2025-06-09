import google.generativeai as genai

genai.configure(api_key="AIzaSyChTAGoY9r2pEWvyKVpfrQXkmBkz3po2B4")

models = genai.list_models()

print("Available models:")
for model in models:
    print(f"- {model.name}: {model.description}")
