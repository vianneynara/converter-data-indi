"""
Tool built with AI to convert TXT files to CSV given an explicit format.

Format:

FULL NAME
NIM
ALAMAT 1
ALAMAT 2 (kontinuasi)
EMAIL@DOMAIN
Tel. NOMOR TELPON
"""
# ... existing code ...
import csv
import re
from pathlib import Path

# Load text data
INPUT_DIR = "./_input"
OUTPUT_DIR = "./_output"

# Get all .txt files from INPUT_DIR
input_path = Path(INPUT_DIR)
txt_files = list(input_path.glob("*.txt"))


# Function to read file with multiple encoding attempts
def read_file_with_encoding(file_path):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'macroman']

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
                print(f"[💡] Successfully read with encoding: {encoding}")
                return content
        except (UnicodeDecodeError, LookupError):
            continue

    # Last resort: read with errors='ignore'
    with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
        print(f"  Warning: Read with UTF-8 ignoring errors")
        return f.read()


def clean_text(text):
    """Clean up encoding artifacts and standardize special characters"""
    # Replace common encoding artifacts with dash
    text = text.replace('Ð', '-')
    text = text.replace('—', '-')  # em dash
    text = text.replace('–', '-')  # en dash
    text = text.replace('�', '-')  # whatever weird thing this is
    text = text.replace('\x92', "'")  # curly apostrophe
    text = text.replace('\x93', '"')  # opening quote
    text = text.replace('\x94', '"')  # closing quote
    text = text.replace('\x96', '-')  # dash
    text = text.replace('\x97', '-')  # longer dash

    return text


def extract_fullnames_from_txt(raw_text):
    """
    Extract all full names from the TXT file by finding patterns:
    - Name followed by a numeric NIM (8-10 digits)
    Returns a list of full names found in the text
    """
    fullnames = []

    # Pattern: capture text before a NIM (8-10 consecutive digits)
    # This pattern looks for: Any text followed by 8-10 digits
    pattern = r'([A-Za-z][A-Za-z\s\.]+?)(\d{8,10})'

    matches = re.finditer(pattern, raw_text)

    for match in matches:
        name = match.group(1).strip()
        nim = match.group(2)

        # Filter out false positives
        # Skip if name contains @ (email domain)
        if '@' in name:
            continue

        # Skip if name is just "Tel" or ends with "Tel."
        if name.lower() in ['tel', 'tel.'] or name.lower().endswith('tel.'):
            continue

        # Skip if name contains common email/web keywords
        invalid_keywords = ['.com', '.co.', '.id', 'yahoo', 'gmail', 'hotmail', 'email']
        if any(keyword in name.lower() for keyword in invalid_keywords):
            continue

        # Skip if name contains forward slashes or dashes followed by numbers (likely phone numbers)
        if re.search(r'[/\-]\s*\d', name):
            continue

        # Skip names that are too short or contain too many special chars
        if len(name) < 3 or name.count('.') >= 3:
            continue

        # Skip if the name is mostly numbers or special characters
        alpha_chars = sum(c.isalpha() for c in name)
        if alpha_chars < len(name) * 0.5:  # At least 50% should be letters
            continue

        fullnames.append(name)

    return fullnames


def validate_csv_against_txt(txt_path, csv_path):
    """
    Validate that all names from TXT file exist in the CSV file
    Returns (missing_names, total_txt_names, total_csv_names)
    """
    print("<< STAGE 2 >>")

    print(f"[🔍] Validating: \"{txt_path.name}\" against \"{csv_path.name}\"")

    # Read TXT and extract names
    raw_text = read_file_with_encoding(txt_path)
    raw_text = clean_text(raw_text)
    txt_fullnames = extract_fullnames_from_txt(raw_text)

    # Remove duplicates while preserving order
    seen = set()
    txt_fullnames_unique = []
    for name in txt_fullnames:
        if name not in seen or not name.endswith("Tel."):
            seen.add(name)
            txt_fullnames_unique.append(name)

    print(f"[💡] Found {len(txt_fullnames_unique)} unique names in TXT file")

    # Read CSV and get all fullnames
    csv_fullnames = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Fullname' in row:
                    csv_fullnames.append(row['Fullname'].strip())
    except Exception as e:
        print(f"[💡] ❌ Error reading CSV: {e}")
        return [], len(txt_fullnames_unique), 0

    print(f"[💡] Found {len(csv_fullnames)} names in CSV file")

    # Find missing names
    missing_names = []
    csv_fullnames_lower = [name.lower() for name in csv_fullnames]

    for txt_name in txt_fullnames_unique:
        # Check if name exists in CSV (case-insensitive)
        if txt_name.lower() not in csv_fullnames_lower:
            missing_names.append(txt_name)

    return missing_names, len(txt_fullnames_unique), len(csv_fullnames)


# Process each file
for file_path in txt_files:
    print(f"[BEGIN] Processing: \"{file_path.name}\"")

    print("<< STAGE 1 >>")

    raw_text = read_file_with_encoding(file_path)
    raw_text = clean_text(raw_text)

    # Split by double newlines (each entry seems separated this way)
    entries = raw_text.strip().split("\n\n")
    print(f"[💡] Found {len(entries)} entries")

    # Prepare parsed data
    parsed_data = []
    warnings_count = 0

    for idx, entry in enumerate(entries, 1):
        lines = [line.strip() for line in entry.split("\n") if line.strip()]

        if len(lines) > 7:
            print(
                f"[⚠️] WARNING at entry {idx}: Too many lines ({len(lines)} lines). Entry might be concatenated."
            )

        if len(lines) < 4:
            print(
                f"[⚠️] WARNING at entry {idx}: Too few lines ({len(lines)} lines). Entry might be malformed or incomplete.")
            warnings_count += 1
            continue

        # Basic structure: [Fullname, NIM, Address..., Email, Tel. ...]
        fullname = lines[0]
        nim = lines[1]

        # Validate NIM format (should be numeric and reasonable length)
        if not nim.isdigit():
            print(f"[⚠️] WARNING at entry {idx}: NIM '{nim}' is not numeric. Entry may be corrupted.")
            warnings_count += 1

        if len(nim) < 8 or len(nim) > 15:
            print(
                f"[⚠️] WARNING at entry {idx}: NIM '{nim}' has unusual length ({len(nim)} digits). Expected 8-15 digits.")
            warnings_count += 1

        # find email (contains @)
        email = next((l for l in lines if "@" in l), "")
        if not email:
            print(f"[⚠️] WARNING at entry {idx}: No email found for '{fullname}'. Entry might be incomplete.")
            warnings_count += 1
        elif email.count("@") > 1:
            print(f"[⚠️] WARNING at entry {idx}: Multiple '@' symbols found: '{email}'. Possible data concatenation.")
            warnings_count += 1

        # find phone (starts with Tel.)
        phone = next((l for l in lines if l.lower().startswith("tel")), "")
        if not phone:
            print(f"[⚠️] WARNING at entry {idx}: No phone field found for '{fullname}'.")
            warnings_count += 1
        else:
            phone_cleaned = phone.replace("Tel.", "").strip()
            # Check if phone line contains letters (possible concatenation)
            if any(c.isalpha() for c in phone_cleaned.replace("-", "").replace("/", "").replace(" ", "")):
                print(
                    f"[⚠️] WARNING at entry {idx}: Phone field contains letters: '{phone}'. Possible data concatenation.")
                warnings_count += 1

        phone = phone.replace("Tel.", "").strip()

        # Address is between NIM and email (exclude lines containing @ or Tel)
        address_lines = [l for l in lines[2:] if "@" not in l and not l.lower().startswith("tel")]
        address = " ".join(address_lines)

        if not address:
            print(f"[⚠️] WARNING at entry {idx}: No address found for '{fullname}'.")
            warnings_count += 1

        # Check for suspiciously long lines (potential concatenated entries)
        for line in lines:
            if len(line) > 200:
                print(
                    f"[⚠️] WARNING at entry {idx}: Suspiciously long line ({len(line)} chars). Possible concatenated entries.")
                warnings_count += 1
                break

        parsed_data.append([nim, fullname, email, phone, address])

    # Save as CSV with the same name in OUTPUT_DIR
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)  # Create output directory if it doesn't exist

    output_csv = output_path / f"{file_path.stem}.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["NIM", "Fullname", "Email", "Phone Number", "Address"])
        writer.writerows(parsed_data)

    print(f"[✅] Saved: {output_csv.name} ({len(parsed_data)} records)")
    if warnings_count > 0:
        print(f"[⚠️] WARNING Total warnings for this file: {warnings_count}")

    # Validate the CSV against the original TXT
    missing_names, total_txt, total_csv = validate_csv_against_txt(file_path, output_csv)

    if missing_names:
        print(f"\n[❌ VALIDATION FAILED]: {len(missing_names)} names from TXT not found in CSV:")
        for name in missing_names[:10]:  # Show first 10 missing names
            print(f"-> {name}")
        if len(missing_names) > 10:
            print(f"-> ... and {len(missing_names) - 10} more")
    else:
        print(f"[✅] VALIDATION PASSED: All {total_txt} names from TXT found in CSV")

    # Check if CSV has more entries than expected
    if total_csv > total_txt:
        print(f"[⚠️] WARNING: CSV has MORE entries ({total_csv}) than TXT names found ({total_txt})")
    elif total_csv < total_txt:
        print(f"[⚠️] WARNING: CSV has FEWER entries ({total_csv}) than TXT names found ({total_txt})")

print(f"[FINISHED] Processed {len(txt_files)} file(s)")
