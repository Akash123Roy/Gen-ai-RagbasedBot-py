import fitz #pymupdf
from docx import Document
import os

class DataExtraction():
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = self.detect_file_type()
    
    def detect_file_type(self):
        _, file_extension = os.path.splitext(self.file_path)
        return file_extension.lower()
    
    def process_file(self):
        if self.file_type == ".txt":
            return self.extract_data_from_text()
        elif self.file_type == ".pdf":
            return self.extract_data_from_pdf()
        elif self.file_type == ".docx":
            return self.extract_data_from_docx()
        else:
            raise ValueError (f"Unsupported file type: {self.file_type}")
        
    def extract_data_from_text(self):
        try:
            with open(self.file_path, "r") as file:
                data = file.read()
                final_data = data.lower()
            return final_data
        except Exception as e:
            return (f"error extracting data from file: {e}")
        
    def extract_data_from_pdf(self):
        try:
            pdf_doc = fitz.open(self.file_path)
            extracted_text = []
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    extracted_text.append(text)
            full_text = " ".join(extracted_text)
            full_text_final = full_text.lower()
            return full_text_final
        
        except Exception as e:
            return(f"error extracting data from file: {e}")
        
    def extract_data_from_docx(self):
        try:
            doc = Document(self.file_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
            extracted_text = "\n".join(paragraphs)
            extracted_text_final = extracted_text.lower()
            return extracted_text_final
        except Exception as e:
            return(f"error extracting data from file: {e}")
        
if __name__ == "__main__":
    file_path = "selfish_giant_story.txt"
    process = DataExtraction(file_path)
    result = process.process_file()
    print(result)