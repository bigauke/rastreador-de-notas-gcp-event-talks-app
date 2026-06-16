import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

# Target directories
INVOICES_DIR = os.path.join("Financial", "Invoices")
RECEIPTS_DIR = os.path.join("Financial", "Receipts")
REPORTS_DIR = "Relatórios"

def setup_directories():
    for directory in [INVOICES_DIR, RECEIPTS_DIR, REPORTS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Diretório criado: {directory}")

def get_docx_text(file_path):
    """Extracts raw text from a .docx file using standard library zipfile."""
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        texts = [elem.text for elem in root.iter() if elem.tag.endswith('t') and elem.text]
        return " ".join(texts)
    except Exception as e:
        print(f"Erro ao ler conteúdo de {file_path}: {e}")
        return ""

def categorize_files(search_dir="."):
    setup_directories()
    
    files = [f for f in os.listdir(search_dir) if os.path.isfile(f)]
    pdf_docx_files = [f for f in files if f.lower().endswith(('.pdf', '.docx'))]
    
    if not pdf_docx_files:
        print("Nenhum arquivo PDF ou DOCX encontrado no diretório raiz para categorização.")
        return
        
    for filename in pdf_docx_files:
        file_path = filename
        lower_name = filename.lower()
        content = ""
        
        # If it's a docx, search its internal text contents
        if lower_name.endswith('.docx'):
            content = get_docx_text(file_path).lower()
            
        # Decision logic based on name or content
        is_invoice = "invoice" in lower_name or "invoice" in content
        is_receipt = "receipt" in lower_name or "receipt" in content
        
        dest_dir = None
        if is_invoice:
            dest_dir = INVOICES_DIR
        elif is_receipt:
            dest_dir = RECEIPTS_DIR
        elif lower_name.endswith('.docx'):
            dest_dir = REPORTS_DIR
            
        if dest_dir:
            dest_path = os.path.join(dest_dir, filename)
            try:
                shutil.move(file_path, dest_path)
                print(f"Movido: '{filename}' ➔ '{dest_path}'")
            except Exception as e:
                print(f"Erro ao mover '{filename}': {e}")
        else:
            print(f"Ignorado (não corresponde a nenhuma categoria): '{filename}'")

if __name__ == "__main__":
    categorize_files()
