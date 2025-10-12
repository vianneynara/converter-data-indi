import sys

import pypdf
from pathlib import Path

def remove_page(input_pdf, output_pdf, page_numbers):
    pdf_reader = pypdf.PdfReader(input_pdf)
    pdf_writer = pypdf.PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        if page_num not in page_numbers:
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as file:
        pdf_writer.write(file)

    print(f"[✓] Removed pages {page_numbers} and saved to {output_pdf}")


if __name__ == "__main__":
    # Configuration
    INPUT_DIR = "./_input"
    OUTPUT_DIR = "./_output"

    # Create directories
    input_path = Path(INPUT_DIR)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    # Find all PDF files in input directory
    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"[❌] No PDF files found in {INPUT_DIR}")
        exit(1)

    print(f"[🔍] Found {len(pdf_files)} PDF file(s)\n")

    # read args "1,2,3" means putting page 0, 1, 2 list range

    arg1 = sys.argv[1]

    print(arg1)

    # parse
    page_numbers = [int(num) - 1 for num in arg1.split(",")]

    for pdf_file in pdf_files:
        output_pdf = output_path / pdf_file.name
        remove_page(pdf_file, output_pdf, page_numbers)