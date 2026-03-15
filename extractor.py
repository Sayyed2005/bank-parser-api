import pdfplumber
import re

def extract_transactions(file_path, password=None):

    # default password if none provided
    if not password:
        password = "9167641708"

    text_data = ""

    try:

        with pdfplumber.open(file_path, password=password) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    text_data += text + "\n"

    except Exception as e:

        raise Exception("Unable to open PDF. Password may be incorrect.")

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
