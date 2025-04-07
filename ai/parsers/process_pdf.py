import PyPDF2
from tqdm import tqdm
import os

folder_path = "D:/Projects/llm_benchmark/COMST/3gpp/IEEE/"
filename = "ethernet standards.pdf"


reader = PyPDF2.PdfReader(os.path.join(folder_path, filename))
filtered_doc = PyPDF2.PdfWriter()

for page in tqdm(reader.pages):
    _text = page.extract_text()
    
    if _text.count(".") > 30:
        continue
        
    all_words = _text.replace("\n", " ").split()
    valid_words = [w for w in all_words if w.isalpha()]
    
    if len(valid_words) > 400 and len(valid_words)/len(all_words) > .6:
        filtered_doc.add_page(page)

with open(os.path.join(folder_path, "processed_"+filename), 'wb') as f:
    filtered_doc.write(f)