from docx import Document
import os

file_path = r"C:\Users\baiss\OneDrive\Desktop\portfolio\ai agent 2.0\Security-Policy-2-Account-Management.docx"
print("File exists:", os.path.exists(file_path))

doc = Document(file_path)
text = "\n".join([para.text for para in doc.paragraphs])
print("Document content preview:")
print(text[:500])  # print first 500 characters
