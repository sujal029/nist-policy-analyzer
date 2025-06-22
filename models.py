models = genai.list_models()
for m in models:
    print(m.name)
