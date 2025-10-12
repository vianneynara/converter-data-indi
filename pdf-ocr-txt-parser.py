"""
PDF Text Extractor with OCR fallback using Tesseract
Extracts text from PDF files, uses OCR if pages are images
"""

import PyPDF2
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import io

# Configuration
INPUT_DIR = "./_input"
OUTPUT_DIR = "./_output"

# Tesseract configuration (adjust path if needed)
# Windows example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Linux/Mac: usually works by default if installed via package manager

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_with_ocr(pdf_path, page_num):
    """
    Extract text from a PDF page using OCR

    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)

    Returns:
        Extracted text as string
    """
    try:
        # Convert specific page to image
        # Note: page numbers in convert_from_path are 1-indexed
        images = convert_from_path(
            pdf_path,
            first_page=page_num + 1,
            last_page=page_num + 1,
            dpi=300  # Higher DPI = better quality = better OCR
        )

        if not images:
            return ""

        # Perform OCR on the image
        text = pytesseract.image_to_string(images[0], lang='eng')

        return text

    except Exception as e:
        print(f"[❌] OCR Error on page {page_num + 1}: {str(e)}")
        return ""


def extract_text_from_pdf(pdf_path, start_page=0, end_page=None):
    """
    Extract text from PDF file, with OCR fallback for image-based pages

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
            pdf_reader = PyPDF2.PdfReader(file)

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

            print(f"[💡] Extracting pages {start_page} to {end_page-1}")

            # Extract text from specified pages
            extracted_text = []
            ocr_count = 0
            text_count = 0

            for page_num in range(start_page, end_page):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Check if text extraction worked
                text_length = len(text.strip())

                # If no text or very little text, use OCR
                if text_length < 50:  # Threshold: less than 50 chars = likely an image
                    print(f"[🔍] Page {page_num + 1}: No text found ({text_length} chars), using OCR...")
                    text = extract_text_with_ocr(pdf_path, page_num)
                    ocr_count += 1
                    method = "OCR"
                else:
                    text_count += 1
                    method = "TEXT"

                # Add page separator
                extracted_text.append(f"\n{'='*80}\n")
                extracted_text.append(f"PAGE {page_num + 1} [{method}]\n")
                extracted_text.append(f"{'='*80}\n")
                extracted_text.append(text)

                print(f"[✓] Extracted page {page_num + 1} via {method} ({len(text)} characters)")

            print(f"\n[📊] Summary: {text_count} pages via text extraction, {ocr_count} pages via OCR")

            return "\n".join(extracted_text)

    except FileNotFoundError:
        print(f"[❌] Error: File not found - {pdf_path}")
        return ""
    except Exception as e:
        print(f"[❌] Error extracting PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""


def main():
    """Main function to process PDF files"""

    print("[🚀] PDF Text Extractor with OCR Support")
    print("=" * 80)

    # Check if Tesseract is available
    try:
        pytesseract.get_tesseract_version()
        print("[✅] Tesseract OCR is available")
    except Exception as e:
        print("[⚠️] Warning: Tesseract not found or not configured properly")
        print("    Install: https://github.com/tesseract-ocr/tesseract")
        print("    Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("    Mac: brew install tesseract")
        print("    Windows: Download from GitHub releases")
        print()

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

            # Show preview of first 800 characters
            print(f"\n[👀] PREVIEW (first 800 chars):")
            print("-" * 80)
            print(extracted_text[:800])
            print("-" * 80)
        else:
            print(f"[❌] No text extracted from {pdf_path.name}")

    print(f"\n[FINISHED] Processed {len(pdf_files)} PDF file(s)")


if __name__ == "__main__":
    main()