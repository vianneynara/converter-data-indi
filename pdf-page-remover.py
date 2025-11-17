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


def parse_page_ranges(spec):
    """
    Parse page specification into separate ranges for splitting.
    
    Examples:
        "1,2,3" -> [([0], "1"), ([1], "2"), ([2], "3")]
        "1-5" -> [([0,1,2,3,4], "1-5")]
        "1,3-5,7" -> [([0], "1"), ([2,3,4], "3-5"), ([6], "7")]
    """
    ranges = []
    parts = spec.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            # Handle range
            start, end = part.split("-")
            start = int(start.strip())
            end = int(end.strip())
            pages = list(range(start - 1, end))
            range_label = f"{start}-{end}"
            ranges.append((pages, range_label))
        else:
            # Handle single page
            page_num = int(part) - 1
            ranges.append(([page_num], part))

    return ranges


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


def split_pages(input_pdf, output_path, page_ranges):
    """Split PDF into multiple files based on page ranges."""
    pdf_reader = pypdf.PdfReader(input_pdf)
    input_stem = input_pdf.stem
    
    for pages, range_label in page_ranges:
        pdf_writer = pypdf.PdfWriter()
        
        for page_num in pages:
            if page_num < len(pdf_reader.pages):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
        
        output_filename = f"{input_stem}[{range_label}].pdf"
        output_file = output_path / output_filename
        
        with open(output_file, 'wb') as file:
            pdf_writer.write(file)
        
        print(f"[✓] Split pages {range_label} to {output_filename}")


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
        print("  Split pages:  python script.py --split 1-5,6-10,11")
        sys.exit(1)

    # Check mode
    if sys.argv[1] == "--keep":
        if len(sys.argv) < 3:
            print("[❌] Please specify pages to keep")
            sys.exit(1)
        mode = "keep"
        page_spec = sys.argv[2]
    elif sys.argv[1] == "--split":
        if len(sys.argv) < 3:
            print("[❌] Please specify pages to split")
            sys.exit(1)
        mode = "split"
        page_spec = sys.argv[2]
    else:
        mode = "remove"
        page_spec = sys.argv[1]

    print(f"[📄] Page specification: {page_spec}")

    # Parse page numbers or ranges
    try:
        if mode == "split":
            page_ranges = parse_page_ranges(page_spec)
            print(f"[📋] Split ranges: {[r[1] for r in page_ranges]}\n")
        else:
            page_numbers = parse_page_spec(page_spec)
            print(f"[📋] Parsed pages (1-indexed): {[p + 1 for p in page_numbers]}\n")
    except Exception as e:
        print(f"[❌] Error parsing page specification: {e}")
        sys.exit(1)

    # Process each PDF
    for pdf_file in pdf_files:
        print(f"[📝] Processing: {pdf_file.name}")

        if mode == "split":
            split_pages(pdf_file, output_path, page_ranges)
        elif mode == "keep":
            output_pdf = output_path / pdf_file.name
            keep_pages(pdf_file, output_pdf, page_numbers)
        else:
            output_pdf = output_path / pdf_file.name
            remove_pages(pdf_file, output_pdf, page_numbers)

    print(f"\n[✅] Done! Processed {len(pdf_files)} file(s)")