import os
import re
from pypdf import PdfReader

# Directory containing invoices
INVOICES_DIR = os.path.join("Financial", "Invoices")

months_pt = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8,
    'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

def extract_date(text):
    """Parses text to extract the first valid date and returns it as YYYY-MM-DD."""
    # Pattern 1: YYYY-MM-DD or YYYY/MM/DD
    match1 = re.search(r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b', text)
    if match1:
        y, m, d = match1.groups()
        if int(m) <= 12 and int(d) <= 31:
            return f"{y}-{int(m):02d}-{int(d):02d}"
        
    # Pattern 2: DD-MM-YYYY or DD/MM/YYYY (common in Brazil)
    match2 = re.search(r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b', text)
    if match2:
        d, m, y = match2.groups()
        if int(d) <= 31 and int(m) <= 12:
            return f"{y}-{int(m):02d}-{int(d):02d}"
            
    # Pattern 3: DD de [Mês] de YYYY
    pattern_text = r'\b(\d{1,2})\s+de\s+([a-zA-Zçõáéíóú]+)\s+de\s+(\d{4})\b'
    match3 = re.search(pattern_text, text, re.IGNORECASE)
    if match3:
        d, month_name, y = match3.groups()
        month_lower = month_name.lower()
        if month_lower in months_pt:
            m = months_pt[month_lower]
            return f"{y}-{m:02d}-{int(d):02d}"
            
    return None

def get_pdf_text(file_path):
    """Extracts raw text content from all pages of a PDF."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Erro ao ler PDF '{file_path}': {e}")
        return ""

def process_invoices():
    if not os.path.exists(INVOICES_DIR):
        print(f"Diretório '{INVOICES_DIR}' não encontrado. Execute o script 'categorize_docs.py' primeiro.")
        return
        
    files = [f for f in os.listdir(INVOICES_DIR) if os.path.isfile(os.path.join(INVOICES_DIR, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado na pasta '{INVOICES_DIR}'.")
        return
        
    for filename in pdf_files:
        file_path = os.path.join(INVOICES_DIR, filename)
        
        # Check if the file is already formatted as "invoice_YYYY-MM-DD_" to avoid double-renaming
        if re.match(r'^invoice_\d{4}-\d{2}-\d{2}_', filename):
            print(f"Ignorado (já renomeado anteriormente): '{filename}'")
            continue
            
        text_content = get_pdf_text(file_path)
        date_str = extract_date(text_content)
        
        if date_str:
            new_filename = f"invoice_{date_str}_{filename}"
            new_file_path = os.path.join(INVOICES_DIR, new_filename)
            try:
                os.rename(file_path, new_file_path)
                print(f"Renomeado com sucesso: '{filename}' ➔ '{new_filename}'")
            except Exception as e:
                print(f"Erro ao renomear '{filename}' para '{new_filename}': {e}")
        else:
            print(f"Aviso: Nenhuma data válida encontrada no conteúdo de '{filename}'")

if __name__ == "__main__":
    process_invoices()
