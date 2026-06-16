import sys
import os
import re
from pypdf import PdfReader

def extract_pdf_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Erro ao ler o PDF '{pdf_path}': {e}")
        return None

def summarize_financials(text):
    # Search for common sections or keywords
    performance_keywords = ["performance", "desempenho", "receita", "faturamento", "lucro", "crescimento", "financeira", "ebitda"]
    challenge_keywords = ["desafio", "dificuldade", "risco", "obstáculo", "queda", "redução", "problema", "competidor"]
    
    sentences = re.split(r'\.\s+', text)
    
    perf_highlights = []
    challenge_highlights = []
    
    for sentence in sentences:
        sentence_clean = sentence.strip().replace("\n", " ")
        if not sentence_clean:
            continue
            
        lower_sentence = sentence_clean.lower()
        
        # Check if sentence matches performance keywords
        if any(kw in lower_sentence for kw in performance_keywords):
            if len(perf_highlights) < 5 and len(sentence_clean) > 30:
                perf_highlights.append(sentence_clean)
                
        # Check if sentence matches challenge keywords
        if any(kw in lower_sentence for kw in challenge_keywords):
            if len(challenge_highlights) < 5 and len(sentence_clean) > 30:
                challenge_highlights.append(sentence_clean)
                
    return perf_highlights, challenge_highlights

def main():
    file_name = "financial_report_Q2_2025.pdf"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        
    if not os.path.exists(file_name):
        print(f"Erro: Arquivo '{file_name}' não encontrado no diretório atual.")
        print("Adicione o arquivo PDF nesta pasta e execute o script novamente:")
        print(f"python summarize_pdf.py {file_name}")
        return
        
    print(f"Analisando '{file_name}'...")
    text = extract_pdf_text(file_name)
    if not text:
        return
        
    perf, challenges = summarize_financials(text)
    
    print("\n--- Desempenho Financeiro ---")
    if perf:
        for idx, item in enumerate(perf, 1):
            print(f"{idx}. {item}.")
    else:
        print("Nenhum destaque claro sobre performance financeira foi encontrado.")
        
    print("\n--- Principais Desafios ---")
    if challenges:
        for idx, item in enumerate(challenges, 1):
            print(f"{idx}. {item}.")
    else:
        print("Nenhum destaque claro sobre desafios/riscos foi encontrado.")

if __name__ == "__main__":
    main()
