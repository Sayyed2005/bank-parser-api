import pdfplumber
import re

def extract_transactions(file_path):

    text_data=""

    with pdfplumber.open(file_path,password="9167641708") as pdf:
        for page in pdf.pages:
            text=page.extract_text()
            if text:
                text_data+=text+"\n"

    pattern=r'(\d{2}-\d{2}-\d{4})\s+(.*?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})'

    matches=re.findall(pattern,text_data)

    transactions=[]

    for m in matches:

        transactions.append({
            "date":m[0],
            "description":m[1],
            "amount":m[2],
            "balance":m[3]
        })

    return transactions