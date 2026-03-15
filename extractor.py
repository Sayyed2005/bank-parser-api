import pdfplumber
import re


def clean_amount(val):

    if not val:
        return None

    val = str(val).replace(",", "").strip()

    if val == "-" or val == "":
        return None

    return val


def extract_utr(text):

    m = re.search(r'\b\d{12}\b', text)

    if m:
        return m.group(0)

    return None


def is_number(val):
    return re.match(r'^\d+(\.\d{2})?$', str(val).replace(",", "").strip())


def extract_transactions(file_path, password=None):

    transactions = []

    if not password:
        password = "zahi1207"

    with pdfplumber.open(file_path, password=password) as pdf:

        current_txn = None

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                for row in table:

                    if not row:
                        continue

                    row = [str(x).strip() if x else "" for x in row]

                    if len(row) < 7:
                        continue

                    sr = row[0]
                    date = row[1]

                    # ---------- NEW TRANSACTION ----------
                    if sr.isdigit() and re.match(r'\d{2}/\d{2}/\d{4}', date):

                        if current_txn:
                            transactions.append(current_txn)

                        description = row[2]

                        debit = clean_amount(row[4])
                        credit = clean_amount(row[5])
                        balance = clean_amount(row[6])

                        amount = debit if debit else credit

                        current_txn = {
                            "date": date,
                            "description": description,
                            "amount": amount,
                            "balance": balance,
                            "utr": extract_utr(description)
                        }

                    # ---------- CONTINUATION ROW ----------
                    elif current_txn and not sr and not date:

                        extra_text = row[2]

                        if extra_text:
                            current_txn["description"] += " " + extra_text

        if current_txn:
            transactions.append(current_txn)

    return transactions
