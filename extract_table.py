import sys
import os
from pypdf import PdfReader

def extract_page_3_table(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo '{pdf_path}' não encontrado.")
        return
        
    print(f"Lendo '{pdf_path}'...")
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) < 3:
            print(f"Erro: O PDF tem apenas {len(reader.pages)} páginas. A página 3 não existe.")
            return
            
        page = reader.pages[2] # Page 3 (0-indexed index 2)
        text = page.extract_text()
        
        print("\n--- Texto bruto extraído da Página 3 ---")
        print(text)
        print("----------------------------------------\n")
        
        # Simple parser logic helper
        print("Nota: Para converter o texto bruto acima em Markdown de forma precisa,")
        print("analise os delimitadores de tabulação/espaço ou instale a biblioteca 'pdfplumber':")
        print("pip install pdfplumber")
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")

if __name__ == "__main__":
    file_name = "quarterly_sales.pdf"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    extract_page_3_table(file_name)
