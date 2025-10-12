"""
Simple PDF Text Extractor using pypdf
Extracts text from PDF files to see the raw structure
"""

import pypdf
from pathlib import Path

# Configuration
INPUT_DIR = "./_input"
OUTPUT_DIR = "./_output"


def extract_text_from_pdf(pdf_path, start_page=0, end_page=None):
    """
    Extract text from PDF file

    Args:
        pdf_path: Path to PDF file
        start_page: Starting page number (0-indexed)
        end_page: Ending page number (0-indexed), None for all pages

    Returns:
        Extracted text as string
    """
    print(f"[📄] Opening PDF: {pdf_path.name}")

    try:
        with open(pdf_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = pypdf.PdfReader(file)

            # Get total number of pages
            total_pages = len(pdf_reader.pages)
            print(f"[💡] Total pages: {total_pages}")

            # Set end_page if not specified
            if end_page is None:
                end_page = total_pages
            else:
                end_page = min(end_page, total_pages)

            # Validate page range
            if start_page >= total_pages:
                print(f"[❌] Error: start_page ({start_page}) >= total pages ({total_pages})")
                return ""

            print(f"[💡] Extracting pages {start_page} to {end_page - 1}")

            # Extract text from specified pages
            extracted_text = []

            for page_num in range(start_page, end_page):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Add page separator
                extracted_text.append(f"\n{'=' * 80}\n")
                extracted_text.append(f"PAGE {page_num + 1}\n")
                extracted_text.append(f"{'=' * 80}\n")
                extracted_text.append(text)

                print(f"[✓] Extracted page {page_num + 1} ({len(text)} characters)")

            return "\n".join(extracted_text)

    except FileNotFoundError:
        print(f"[❌] Error: File not found - {pdf_path}")
        return ""
    except Exception as e:
        print(f"[❌] Error extracting PDF: {str(e)}")
        return ""


def main():
    """Main function to process PDF files"""

    # Create directories
    input_path = Path(INPUT_DIR)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    # Find all PDF files in input directory
    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"[❌] No PDF files found in {INPUT_DIR}")
        return

    print(f"[🔍] Found {len(pdf_files)} PDF file(s)\n")

    # Process each PDF
    for pdf_path in pdf_files:
        print(f"\n[BEGIN] Processing: {pdf_path.name}")
        print("-" * 80)

        # Extract text (starting from page 5, as per your requirement)
        # Page 5 in document = index 4 (0-indexed)
        START_PAGE = 4  # Page 5 in the document

        extracted_text = extract_text_from_pdf(pdf_path, start_page=START_PAGE)

        if extracted_text:
            # Save to text file
            output_file = output_path / f"{pdf_path.stem}_extracted.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

            print(f"\n[✅] Saved to: {output_file.name}")
            print(f"[💡] Total extracted length: {len(extracted_text)} characters")

            # Show preview of first 500 characters
            print(f"\n[👀] PREVIEW (first 500 chars):")
            print("-" * 80)
            print(extracted_text[:500])
            print("-" * 80)
        else:
            print(f"[❌] No text extracted from {pdf_path.name}")

    print(f"\n[FINISHED] Processed {len(pdf_files)} PDF file(s)")


if __name__ == "__main__":
    main()