import io
import re
import tempfile
from datetime import datetime
from dateutil import parser as dateparser

import pdfplumber
import pandas as pd
import streamlit as st

def safe_search(patterns, text, flags=0):
    """Return first non-empty match group from given pattern list."""
    for p in patterns:
        m = re.search(p, text, flags)
        if m:
            for g in m.groups():
                if g and g.strip():
                    return g.strip()
            return m.group(0).strip()
    return None


def find_all_dates(text):
    candidates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
    parsed = []
    for c in candidates:
        try:
            parsed.append(dateparser.parse(c, dayfirst=False))
        except Exception:
            pass
    return parsed


def generic_card_last4(text):
    m = re.search(r"(\*{2,4}|X{2,4}|#){0,4}\s*(\d{4})\b", text)
    if m:
        return m.group(2)
    m = re.search(r"(?:Account|Card).*?(\d{4})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def generic_total_balance(text):
    patterns = [r"New\s+Balance[:\s\$]*([\d,]+\.\d{2})",
                r"Total\s+Balance[:\s\$]*([\d,]+\.\d{2})",
                r"Amount\s+Due[:\s\$]*([\d,]+\.\d{2})",
                r"Statement\s+Balance[:\s\$]*([\d,]+\.\d{2})"]
    v = safe_search(patterns, text, flags=re.IGNORECASE)
    if v:
        return v.replace(',', '')
    return None


def generic_due_date(text):
    patterns = [r"Payment\s+Due\s+Date[:\s]*([A-Za-z0-9,\s/\-]+)",
                r"Due\s+Date[:\s]*([A-Za-z0-9,\s/\-]+)",
                r"Payment\s+Due[:\s]*([A-Za-z0-9,\s/\-]+)"]
    v = safe_search(patterns, text, flags=re.IGNORECASE)
    if v:
        try:
            return str(dateparser.parse(v, fuzzy=True).date())
        except Exception:
            return v
    m = re.search(r"Due[^\n]{0,40}(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    if m:
        try:
            return str(dateparser.parse(m.group(1)).date())
        except Exception:
            return m.group(1)
    return None


# ----------------------- Issuer-specific heuristics -----------------------

def parse_chase(text, tables):
    out = {}
    out['issuer'] = 'Chase'
    out['card_last4'] = generic_card_last4(text)
    out['card_variant'] = safe_search([r"Card\s+Member\s+Since[:\s]*(\w+)", r"Chase\s+([A-Za-z &]+)\s+Card"], text, flags=re.IGNORECASE) or 'Chase Card'
    out['total_balance'] = generic_total_balance(text)
    out['payment_due_date'] = generic_due_date(text)
    out['billing_cycle'] = safe_search([r"Statement\s+period[:\s]*(\w+ \d{1,2},? \d{4}\s*-\s*\w+ \d{1,2},? \d{4})",
                                       r"Statement Date[:\s]*(\w+ \d{1,2},? \d{4})"], text, flags=re.IGNORECASE)
    tx = extract_transactions_from_tables(tables)
    if tx.empty:
        tx = extract_transactions_from_text(text)
    out['transactions'] = tx
    return out


def parse_citi(text, tables):
    out = {}
    out['issuer'] = 'Citi'
    out['card_last4'] = generic_card_last4(text)
    out['card_variant'] = safe_search([r"Citi\s+([A-Za-z &]+)\s+Card", r"Account Type[:\s]*(\w+)"], text, flags=re.IGNORECASE) or 'Citi Card'
    out['total_balance'] = generic_total_balance(text)
    out['payment_due_date'] = generic_due_date(text)
    out['billing_cycle'] = safe_search([r"Statement\s+period[:\s]*(\w+ \d{1,2},? \d{4}\s*-\s*\w+ \d{1,2},? \d{4})"], text, flags=re.IGNORECASE)
    tx = extract_transactions_from_tables(tables)
    if tx.empty:
        tx = extract_transactions_from_text(text)
    out['transactions'] = tx
    return out


def parse_amex(text, tables):
    out = {}
    out['issuer'] = 'American Express'
    out['card_last4'] = generic_card_last4(text)
    out['card_variant'] = safe_search([r"American Express\s+([A-Za-z &]+)", r"Member Since[:\s]*(\d{4})"], text, flags=re.IGNORECASE) or 'Amex'
    out['total_balance'] = generic_total_balance(text)
    out['payment_due_date'] = generic_due_date(text)
    out['billing_cycle'] = safe_search([r"Period\s+Covered[:\s]*(\w+ \d{1,2},? \d{4}\s*-\s*\w+ \d{1,2},? \d{4})"], text, flags=re.IGNORECASE)
    tx = extract_transactions_from_tables(tables)
    if tx.empty:
        tx = extract_transactions_from_text(text)
    out['transactions'] = tx
    return out


def parse_bofa(text, tables):
    out = {}
    out['issuer'] = 'Bank of America'
    out['card_last4'] = generic_card_last4(text)
    out['card_variant'] = safe_search([r"Bank of America\s+([A-Za-z &]+)\s+Card"], text, flags=re.IGNORECASE) or 'BofA Card'
    out['total_balance'] = generic_total_balance(text)
    out['payment_due_date'] = generic_due_date(text)
    out['billing_cycle'] = safe_search([r"Statement\s+Period[:\s]*(\w+ \d{1,2},? \d{4}\s*-\s*\w+ \d{1,2},? \d{4})"], text, flags=re.IGNORECASE)
    tx = extract_transactions_from_tables(tables)
    if tx.empty:
        tx = extract_transactions_from_text(text)
    out['transactions'] = tx
    return out


def parse_capital_one(text, tables):
    out = {}
    out['issuer'] = 'Capital One'
    out['card_last4'] = generic_card_last4(text)
    out['card_variant'] = safe_search([r"Capital One\s+([A-Za-z &]+)\s+Card"], text, flags=re.IGNORECASE) or 'Capital One Card'
    out['total_balance'] = generic_total_balance(text)
    out['payment_due_date'] = generic_due_date(text)
    out['billing_cycle'] = safe_search([r"Statement\s+period[:\s]*(\w+ \d{1,2},? \d{4}\s*-\s*\w+ \d{1,2},? \d{4})"], text, flags=re.IGNORECASE)
    tx = extract_transactions_from_tables(tables)
    if tx.empty:
        tx = extract_transactions_from_text(text)
    out['transactions'] = tx
    return out


ISSUER_PARSERS = {
    'chase': parse_chase,
    'jpmorgan chase': parse_chase,
    'citi': parse_citi,
    'citibank': parse_citi,
    'american express': parse_amex,
    'amex': parse_amex,
    'bank of america': parse_bofa,
    'bofa': parse_bofa,
    'capital one': parse_capital_one,
    'capitalone': parse_capital_one,
}



def extract_transactions_from_tables(tables):
    for t in tables:
        df = t.copy()
        cols = [str(c).lower() for c in df.columns]
        if any('date' in c for c in cols) and any('amount' in c or 'charge' in c or 'credit' in c for c in cols):
            rename_map = {}
            for c in df.columns:
                lc = str(c).lower()
                if 'date' in lc:
                    rename_map[c] = 'date'
                elif 'description' in lc or 'merchant' in lc or 'trans' in lc:
                    rename_map[c] = 'description'
                elif 'amount' in lc or 'charge' in lc or 'debit' in lc or 'credit' in lc:
                    rename_map[c] = 'amount'
            df = df.rename(columns=rename_map)
            if 'date' in df.columns and 'amount' in df.columns:
                df['amount'] = df['amount'].astype(str).str.replace('[^0-9\.-]', '', regex=True)
                def tryparse(d):
                    try:
                        return dateparser.parse(str(d), fuzzy=True).date()
                    except Exception:
                        return str(d)
                df['date'] = df['date'].apply(tryparse)
                return df[['date', 'description', 'amount']]
    return pd.DataFrame()


def extract_transactions_from_text(text):
    lines = text.splitlines()
    tx_rows = []
    for ln in lines:
        ln = ln.strip()
        if len(ln) < 8:
            continue
        m = re.match(r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+(-?\$?\d{1,3}[,\d]*\.\d{2})$", ln)
        if m:
            date_s, desc, amt = m.groups()
            try:
                date_v = dateparser.parse(date_s).date()
            except Exception:
                date_v = date_s
            amt = amt.replace('$', '').replace(',', '')
            tx_rows.append({'date': date_v, 'description': desc.strip(), 'amount': amt})
            continue
        m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}).*?([\-]?\$?\d{1,3}[,\d]*\.\d{2})$", ln)
        if m:
            date_s = m.group(1)
            amt = m.group(2)
            desc = ln[:m.start(2)].strip()
            try:
                date_v = dateparser.parse(date_s).date()
            except Exception:
                date_v = date_s
            amt = amt.replace('$', '').replace(',', '')
            tx_rows.append({'date': date_v, 'description': desc, 'amount': amt})
    if tx_rows:
        return pd.DataFrame(tx_rows)
    return pd.DataFrame()


def extract_text_and_tables(pdf_bytes):
    text_parts = []
    tables = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            try:
                pt = page.extract_text()
                if pt:
                    text_parts.append(pt)
            except Exception:
                pass
            try:
                p_tables = page.extract_tables()
                for t in p_tables:
                    if t and len(t) > 0:
                        df = pd.DataFrame(t[1:], columns=t[0]) if len(t) > 1 else pd.DataFrame()
                        if not df.empty:
                            tables.append(df)
            except Exception:
                pass
    whole_text = '\n'.join(text_parts)
    return whole_text, tables


def detect_issuer(text):
    l = text.lower()
    for key in ISSUER_PARSERS.keys():
        if key in l:
            return ISSUER_PARSERS[key]
    return None


def parse_credit_card_statement(pdf_bytes):
    text, tables = extract_text_and_tables(pdf_bytes)
    parser = detect_issuer(text)
    if parser:
        parsed = parser(text, tables)
    else:
        parsed = {
            'issuer': 'Unknown',
            'card_last4': generic_card_last4(text),
            'card_variant': None,
            'total_balance': generic_total_balance(text),
            'payment_due_date': generic_due_date(text),
            'billing_cycle': None,
            'transactions': extract_transactions_from_tables(tables) if extract_transactions_from_tables(tables).empty is False else extract_transactions_from_text(text)
        }
    parsed['raw_text_snippet'] = (text[:500] + '...') if text else None
    return parsed



st.set_page_config(page_title="Credit Card Statement Parser", layout="wide")
st.title("Credit Card Statement Parser")

uploaded = st.file_uploader("Upload statement (PDF)", type=['pdf'])

if uploaded is not None:
    bytes_data = uploaded.read()
    with st.spinner('Parsing PDF...'):
        try:
            result = parse_credit_card_statement(bytes_data)
        except Exception as e:
            st.error(f"Failed to parse PDF: {e}")
            st.stop()

    st.subheader("Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Issuer", result.get('issuer', ''))
    col2.metric("Card last 4", result.get('card_last4', ''))
    col3.metric("Total balance", result.get('total_balance', ''))
    col4.metric("Payment due", result.get('payment_due_date', ''))
    col5.metric("Billing cycle", result.get('billing_cycle', ''))

    st.markdown("---")
    st.subheader("Transactions (best-effort)")
    tx = result.get('transactions')
    if isinstance(tx, pd.DataFrame) and not tx.empty:
        st.dataframe(tx)
        csv = tx.to_csv(index=False)
        st.download_button("Download transactions CSV", data=csv, file_name='transactions.csv', mime='text/csv')
    else:
        st.info("No transactions table recognized. The parser includes heuristics; try a different statement or check raw text below.")

    st.markdown("---")
    st.subheader("Raw text snippet")
    st.code(result.get('raw_text_snippet', 'No text extracted'))

