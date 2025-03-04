import cmd
import os
import pdfplumber
from docx import Document

class DocumentViewer(cmd.Cmd):
    intro = 'Welcome to the Document Viewer. Type help or ? to list commands.\n'
    prompt = '>>> '

    def do_view(self, path):
        if not path or not os.path.isfile(path):
            print("Please provide a valid path to the document.")
            return

        ext = os.path.splitext(path)[1].lower()
        if ext == '.pdf':
            self.view_pdf(path)
        elif ext == '.txt':
            self.view_txt(path)
        elif ext == '.docx':
            self.view_docx(path)
        else:
            print("Unsupported file format. Supported formats: .pdf, .txt, .docx")

    def view_pdf(self, path):
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    print(page.extract_text())
                    print("\n" + "="*40 + "\n")
        except Exception as e:
            print(f"Error reading PDF: {e}")

    def view_txt(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                print(file.read())
        except Exception as e:
            print(f"Error reading TXT: {e}")

    def view_docx(self, path):
        try:
            doc = Document(path)
            for para in doc.paragraphs:
                print(para.text)
        except Exception as e:
            print(f"Error reading DOCX: {e}")

    def do_exit(self, arg):
        print("Exiting Document Viewer.")
        return True

if __name__ == "__main__":
    DocumentViewer().cmdloop()

