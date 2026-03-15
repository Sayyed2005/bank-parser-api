import pdfplumber
import re


def extract_transactions(file_path, password=None):

    passwords_to_try = []

    if password:
        passwords_to_try.append(password)

    # default password
    passwords_to_try.append("9167641708")

    # try without password
    passwords_to_try.append(None)

    text_data = ""

    pdf = None

    # try opening with multiple passwords
    for pwd in passwords_to_try:

        try:
            pdf = pdfplumber.open(file_path, password=pwd)
            break
        except Exception:
            continue

    if not pdf:
        raise Exception("Unable to open PDF. Password may be incorrect.")

    # extract text
    for page in pdf.pages:

        text = page.extract_text()

        if text:
            text_data += text + "\n"

    pdf.close()

    # transaction regex
    pattern = r'(\d{2}-\d{2}-\d{4})\s+(.*?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})'

    matches = re.findall(pattern, text_data)

    transactions = []

    for m in matches:

        transactions.append({
            "date": m[0],
            "description": m[1],
            "amount": m[2],
            "balance": m[3]
        })

    return transactions
