import os
import fitz  # PyMuPDF
import warnings
from tqdm import tqdm

# Suppress any warnings
warnings.filterwarnings("ignore")

def read_page(pdf_path):
    texts = []
    try:
        with fitz.open(pdf_path) as pdf:
            for page_number in range(pdf.page_count):
                page = pdf.load_page(page_number)
                text = page.get_text("text")
                if text:
                    texts.append({
                        "page_number": page_number + 1,  # Pages are 1-indexed
                        "text": text.strip().lower()
                    })
        return texts
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

def store_text_to_file(texts, pdf_filename, processing_folder):
    if texts:
        txt_filename = os.path.splitext(pdf_filename)[0] + '.txt'
        txt_path = os.path.join(processing_folder, txt_filename)
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                for entry in texts:
                    page_number = entry["page_number"]
                    text = entry["text"]
                    txt_file.write(f"[Page {page_number}]\n{text}\n\n")
            print(f"Successfully saved text to {txt_filename}")
        except Exception as e:
            print(f"Error saving text from {pdf_filename}: {e}")
    else:
        print(f"No text to save for {pdf_filename}")

def process_pdfs_in_folder(pdf_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    
    # Using tqdm to display a progress bar while processing PDFs
    for filename in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        pdf_path = os.path.join(pdf_folder, filename)
        texts = read_page(pdf_path)
        store_text_to_file(texts, filename, output_folder)

def main():
    data_folder = "/content/drive/My Drive/DSCI560_Final/law_code"
    processing_folder = "/content/drive/My Drive/DSCI560_Final/processing_data"
    process_pdfs_in_folder(data_folder, processing_folder)


if __name__ == "__main__":
    main()
    
