import csv
import re
from pathlib import Path

# Load RTF text that was already extracted
file_path = Path("./Untitled.rtf")
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()

# Remove RTF formatting if any (keep plain text)
# A crude strip of RTF control sequences
plain_text = re.sub(r"{\\.*?}", "", raw_text)
plain_text = re.sub(r"\\[a-z]+\d*", "", plain_text)
plain_text = re.sub(r"[{}]", "", plain_text)
plain_text = re.sub(r"\n\s*\n", "\n\n", plain_text)

# Split entries
entries = plain_text.strip().split("\n\n")

parsed_data = []

for entry in entries:
    lines = [line.strip().replace("\r", "") for line in entry.split("\n") if line.strip()]
    if len(lines) < 2:
        continue

    fullname = lines[0]
    nim = lines[1]

    # find email
    email = next((l for l in lines if "@" in l), "")

    # find phone
    phone = next((l for l in lines if l.lower().startswith("tel")), "")
    phone = phone.replace("Tel.", "").strip()

    # address between NIM and email
    address_lines = [l for l in lines[2:] if "@" not in l and not l.lower().startswith("tel")]
    address = " ".join(address_lines)

    parsed_data.append([nim, fullname, email, phone, address])

# Save CSV
output_csv = "./alumnis_from_rtf.csv"
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["NIM", "Fullname", "Email", "Phone Number", "Address"])
    writer.writerows(parsed_data)

output_csv
