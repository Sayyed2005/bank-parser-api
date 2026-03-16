import pdfplumber
import re

DEFAULT_PASSWORDS = [
    "9167641708",
    "zahi1207"
]


def open_pdf(path, password):

    passwords = []

    if password:
        passwords.append(password)

    passwords.extend(DEFAULT_PASSWORDS)
    passwords.append(None)

    for p in passwords:
        try:
            return pdfplumber.open(path, password=p)
        except:
            continue

    raise Exception("Unable to open PDF. Password incorrect")


def extract_utr(text):

    match = re.search(r'\d{10,16}', text)

    if match:
        return match.group()

    return None


def parse_amount(val):

    if not val:
        return None

    val = str(val).replace(",", "").strip()

    try:
        return float(val)
    except:
        return None


def table_method(page):

    transactions = []

    tables = page.extract_tables()

    for table in tables:

        if not table:
            continue

        headers = [str(x).lower() if x else "" for x in table[0]]

        if not any("date" in h for h in headers):
            continue

        for row in table[1:]:

            try:

                date = row[0]
                description = row[1]

                withdrawal = parse_amount(row[3] if len(row) > 3 else "")
                deposit = parse_amount(row[4] if len(row) > 4 else "")
                balance = parse_amount(row[5] if len(row) > 5 else "")

                amount = withdrawal if withdrawal else deposit

                utr = extract_utr(description)

                transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "balance": balance,
                    "utr": utr
                })

            except:
                continue

    return transactions


def row_method(page):

    transactions = []

    text = page.extract_text()

    if not text:
        return transactions

    lines = text.split("\n")

    pattern = re.compile(
        r'(\d{2}-\d{2}-\d{4})\s+(.*?)\s+(\d+\.\d{2})?\s*(\d+\.\d{2})?\s+(\d+\.\d{2})'
    )

    for line in lines:

        match = pattern.search(line)

        if match:

            date = match.group(1)
            description = match.group(2)

            withdrawal = parse_amount(match.group(3))
            deposit = parse_amount(match.group(4))
            balance = parse_amount(match.group(5))

            amount = withdrawal if withdrawal else deposit

            utr = extract_utr(description)

            transactions.append({
                "date": date,
                "description": description,
                "amount": amount,
                "balance": balance,
                "utr": utr
            })

    return transactions


def regex_method(page):

    transactions = []

    text = page.extract_text()

    if not text:
        return transactions

    pattern = re.findall(
        r'(\d{2}-\d{2}-\d{4})\s+(MPAY\/UPI\/.*?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})',
        text
    )

    for p in pattern:

        date = p[0]
        description = p[1]
        amount = parse_amount(p[2])
        balance = parse_amount(p[3])

        utr = extract_utr(description)

        transactions.append({
            "date": date,
            "description": description,
            "amount": amount,
            "balance": balance,
            "utr": utr
        })

    return transactions


def extract_transactions(path, password=None):

    transactions = []

    with open_pdf(path, password) as pdf:

        for page in pdf.pages:

            # METHOD 1: TABLE
            data = table_method(page)

            if data:
                transactions.extend(data)
                continue

            # METHOD 2: ROW TEXT
            data = row_method(page)

            if data:
                transactions.extend(data)
                continue

            # METHOD 3: REGEX
            data = regex_method(page)

            if data:
                transactions.extend(data)

    return transactions
