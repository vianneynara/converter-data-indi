import sys
import pypdf
from pathlib import Path


def parse_page_spec(spec):
    """
    Parse page specification string into a list of page numbers (0-indexed).

    Examples:
        "1,2,3" -> [0, 1, 2]
        "1-5" -> [0, 1, 2, 3, 4]
        "1,3-5,7" -> [0, 2, 3, 4, 6]
    """
    pages = set()
    parts = spec.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            # Handle range
            start, end = part.split("-")
            start = int(start.strip())
            end = int(end.strip())
            # Convert to 0-indexed and add all pages in range
            pages.update(range(start - 1, end))
        else:
            # Handle single page
            pages.add(int(part) - 1)

    return sorted(list(pages))


def remove_pages(input_pdf, output_pdf, page_numbers):
    """Remove specified pages from PDF."""
    pdf_reader = pypdf.PdfReader(input_pdf)
    pdf_writer = pypdf.PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        if page_num not in page_numbers:
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as file:
        pdf_writer.write(file)

    print(f"[✓] Removed pages and saved to {output_pdf}")


def keep_pages(input_pdf, output_pdf, page_numbers):
    """Keep only specified pages in PDF."""
    pdf_reader = pypdf.PdfReader(input_pdf)
    pdf_writer = pypdf.PdfWriter()

    for page_num in page_numbers:
        if page_num < len(pdf_reader.pages):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as file:
        pdf_writer.write(file)

    print(f"[✓] Kept pages and saved to {output_pdf}")


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
        sys.exit(1)

    print(f"[🔍] Found {len(pdf_files)} PDF file(s)\n")

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Remove pages: python script.py 1,2,3")
        print("  Remove range: python script.py 1-10")
        print("  Remove mixed: python script.py 1,3-5,7")
        print("  Keep pages:   python script.py --keep 1-10")
        sys.exit(1)

    # Check if we're keeping or removing pages
    if sys.argv[1] == "--keep":
        if len(sys.argv) < 3:
            print("[❌] Please specify pages to keep")
            sys.exit(1)
        mode = "keep"
        page_spec = sys.argv[2]
    else:
        mode = "remove"
        page_spec = sys.argv[1]

    print(f"[📄] Page specification: {page_spec}")

    # Parse page numbers
    try:
        page_numbers = parse_page_spec(page_spec)
        print(f"[📋] Parsed pages (1-indexed): {[p + 1 for p in page_numbers]}\n")
    except Exception as e:
        print(f"[❌] Error parsing page specification: {e}")
        sys.exit(1)

    # Process each PDF
    for pdf_file in pdf_files:
        output_pdf = output_path / pdf_file.name
        print(f"[📝] Processing: {pdf_file.name}")

        if mode == "keep":
            keep_pages(pdf_file, output_pdf, page_numbers)
        else:
            remove_pages(pdf_file, output_pdf, page_numbers)

    print(f"\n[✅] Done! Processed {len(pdf_files)} file(s)")