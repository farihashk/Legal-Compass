import os
import pdfplumber


def read_page(pdf_path):
    all_text = ""  
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:  
                    all_text += text.lower()  
        if not all_text:  
            raise ValueError("No text extracted from the PDF.")
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return all_text


def store_text_to_file(text, pdf_filename, processing_folder):
    if text:
        # Change the PDF filename extension to .txt
        txt_filename = os.path.splitext(pdf_filename)[0] + '.txt'
        txt_path = os.path.join(processing_folder, txt_filename)
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            print(f"Successfully saved text to {txt_filename}")
        except Exception as e:
            print(f"Error saving text from {pdf_filename}: {e}")
    else:
        print(f"No text to save for {pdf_filename}")

def process_pdfs_in_folder(data_folder, processing_folder):
    os.makedirs(processing_folder, exist_ok=True)
    
    # Get all PDF files in the data folder
    pdf_files = [f for f in os.listdir(data_folder) if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(data_folder, pdf_file)
        text = read_page(pdf_path)
        
        # Store the extracted text in the processing folder
        store_text_to_file(text, pdf_file, processing_folder)

def main():
    data_folder = os.path.join("../data", "raw_data")
    processing_folder = os.path.join(data_folder, "processing_data")
    process_pdfs_in_folder(data_folder, processing_folder)


if __name__ == "__main__":
    main()
