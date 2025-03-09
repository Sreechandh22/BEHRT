import os
import re
import spacy
import pandas as pd
from docx import Document

# Load SciSpacy NER model
try:
    nlp = spacy.load("en_core_sci_sm")
except:
    print("❌ SciSpacy model not found. Install it using:")
    print("   pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz")
    exit()

# Directory containing clinical case files
DATA_DIR = r"C:\Users\sreec\OneDrive\Desktop\Clinical\Chat GPT Cases"

# Improved regex patterns for data extraction
patterns = {
    "name": r"Name:\s*([\w\s]+)",
    "age": r"Age:\s*(\d+)\s*years?",
    "gender": r"Gender:\s*(Male|Female|Other)",
    "dob": r"Date of Birth:\s*([\w\s,]+)",
    "address": r"Address:\s*([\w\s,]+)",
    "phone": r"Contact Number:\s*([\(\)\d\s-]+)",
    "mrn": r"Medical Record Number:\s*(\d+)",
    "chief_complaint": r"Chief Complaint:\s*(.+)",
    "hpi": r"History of Present Illness \(HPI\):\s*(.+)",
    "pmh": r"Past Medical History \(PMH\):\s*(.+)",
    "family_history": r"Family History:\s*(.+)",
    "social_history": r"Social History:\s*(.+)",
    "ros": r"Review of Systems \(ROS\):\s*(.+)",
    "physical_exam": r"Physical Examination:\s*(.+)",
    "diagnostic_tests": r"Diagnostic Tests:\s*(.+)",
    "assessment": r"Assessment:\s*(.+)",
    "plan": r"Plan:\s*(.+)"
}

# Function to extract text from a Word document
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

# Function to extract structured data using regex and NER
def extract_data(text, filename):
    extracted = {"filename": filename}
    
    # Extract using regex patterns
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        extracted[field] = match.group(1).strip() if match else "Not Found"
    
    # NER-based extraction for medications and diseases
    doc = nlp(text)
    extracted["medications"] = ", ".join(set([ent.text for ent in doc.ents if ent.label_ == "CHEMICAL"]))
    extracted["diagnosis"] = ", ".join(set([ent.text for ent in doc.ents if ent.label_ in ["DISEASE", "DISORDER"]]))
    
    # Cleanup for missing data
    for key, value in extracted.items():
        if value == "Not Found" or value.strip() == "":
            extracted[key] = "N/A"
    
    return extracted

# Process all Word documents in the dataset folder
extracted_data = []
for file in os.listdir(DATA_DIR):
    if file.endswith(".docx"):
        file_path = os.path.join(DATA_DIR, file)
        text = extract_text_from_docx(file_path)
        extracted_data.append(extract_data(text, file))

# Convert to DataFrame and save results
df = pd.DataFrame(extracted_data)
output_file = os.path.join(DATA_DIR, "clinical_extracted_data.xlsx")
df.to_excel(output_file, index=False)

print(f"✅ Extraction completed! Data saved to: {output_file}")
