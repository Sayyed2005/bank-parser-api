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

    m = re.search(r'(\d{9,18})', text)

    if m:
        return m.group(1)

    return None


def extract_by_rows(text_data):

    transactions = []

    text_data = text_data.replace(",", "")

    # -------- BoM Pattern --------

    bom_pattern = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(\d+)\s+(\d+\.\d{2}|-)\s+(\d+\.\d{2}|-)\s+(\d+\.\d{2})'

    matches = re.findall(bom_pattern, text_data)

    for m in matches:

        debit = clean_amount(m[3])
        credit = clean_amount(m[4])

        amount = debit if debit else credit

        transactions.append({
            "date": m[0],
            "description": m[1],
            "amount": amount,
            "balance": clean_amount(m[5]),
            "utr": extract_utr(m[1])
        })


    # -------- UCO Pattern --------

    uco_pattern = r'(\d{2}-\d{2}-\d{4})\s+(.*?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})'

    matches = re.findall(uco_pattern, text_data)

    for m in matches:

        transactions.append({
            "date": m[0],
            "description": m[1],
            "amount": clean_amount(m[2]),
            "balance": clean_amount(m[3]),
            "utr": extract_utr(m[1])
        })

    return transactions


def extract_by_tables(pdf):

    transactions = []

    for page in pdf.pages:

        tables = page.extract_tables()

        for table in tables:

            for row in table:

                if not row:
                    continue

                row = [str(x).strip() if x else "" for x in row]

                if len(row) < 5:
                    continue

                if not re.match(r'\d{2}[/-]\d{2}[/-]\d{4}', row[1]):
                    continue

                date = row[1]
                description = row[2]

                debit = clean_amount(row[4] if len(row) > 4 else "")
                credit = clean_amount(row[5] if len(row) > 5 else "")
                balance = clean_amount(row[6] if len(row) > 6 else "")

                amount = debit if debit else credit

                if not amount:
                    continue

                transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "balance": balance,
                    "utr": extract_utr(description)
                })

    return transactions


def extract_transactions(file_path, password=None):

    if not password:
        password = "zahi1207"

    try:

        with pdfplumber.open(file_path, password=password) as pdf:

            # ---------- STEP 1 : ROW BASED ----------

            text_data = ""

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    text_data += text + "\n"

            transactions = extract_by_rows(text_data)

            # ---------- STEP 2 : TABLE FALLBACK ----------

            if not transactions:

                transactions = extract_by_tables(pdf)

            return transactions

    except Exception:
        raise Exception("Unable to open PDF. Password may be incorrect.")
