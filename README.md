# Credit Card Statement Parser 🧾

## 📘 Overview
This project is a **Credit Card Statement Parser** that extracts key financial details from PDF statements issued by major banks. It uses **Python** for backend data extraction and **Streamlit** for an interactive frontend interface. Users can upload their credit card statement PDF, and the system will extract and display relevant information such as the card details, billing cycle, payment due date, total balance, and transaction history.

---

## 🎯 Objective
The main goal of this project is to build a **PDF parser** capable of extracting **five key data points** from **credit card statements** across five major issuers:

1. Card Issuer
2. Card Variant / Type
3. Last 4 digits of the Card
4. Billing Cycle
5. Payment Due Date
6. Total Balance
7. Transaction Details *(Bonus)*

The system is designed to handle real-world statement formats and provide a modular foundation for expanding to additional issuers.

---

## 🧠 Key Features

### 🔍 PDF Parsing
- Utilizes **pdfplumber** to extract text and tables from PDF files.
- Works with native (non-scanned) PDFs.
- Extracts and cleans structured data from tables and text blocks.

### 🏦 Issuer Detection
- Automatically detects statement issuer using keyword matching.
- Currently supports:
  - Chase Bank
  - Citibank (Citi)
  - American Express (Amex)
  - Bank of America (BofA)
  - Capital One

### 📊 Data Extraction
- Extracts core information like:
  - **Card last 4 digits**
  - **Card variant/type**
  - **Payment due date**
  - **Billing cycle**
  - **Total balance**
- Heuristics and regex-based pattern recognition for flexibility across layouts.

### 💳 Transaction Extraction
- Parses transaction tables automatically.
- Falls back to text-based extraction when tables aren’t detected.
- Displays parsed transactions in a searchable **Streamlit dataframe** with download option.

### 🧩 Modular Design
- Each issuer has its own parsing function.
- Easily extendable to support more banks or data fields.

---

## 🏗️ System Architecture
```
PDF Upload (Streamlit UI)
        ↓
PDF Text & Table Extraction (pdfplumber)
        ↓
Issuer Detection (heuristic)
        ↓
Issuer-specific Parser (regex & logic)
        ↓
Data Structuring (Pandas DataFrame)
        ↓
Frontend Display + CSV Export
```

---

## ⚙️ Tech Stack
| Component | Technology |
|------------|-------------|
| **Frontend** | Streamlit |
| **Backend** | Python |
| **PDF Parsing** | pdfplumber |
| **Data Handling** | pandas |
| **Date Parsing** | python-dateutil |

---

## 🧩 Folder Structure
```
📂 CreditCardStatementParser/
├── credit_card_statement_parser.py    # Main Streamlit app (single file)
├── README.md                 # Documentation (this file)
└── requirements.txt          # Dependencies list
```

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/credit-card-statement-parser.git
cd credit-card-statement-parser
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

or manually:
```bash
pip install streamlit pdfplumber pandas python-dateutil
```

### 3️⃣ Run the Streamlit App
```bash
streamlit run credit_card_statement_parser.py
```

### 4️⃣ Upload a PDF
- Open the Streamlit interface in your browser.
- Upload a credit card statement.
- View parsed summary and transaction table.

---

## 📋 Example Output
### Summary Section
| Field | Example |
|--------|----------|
| Issuer | CitiBank |
| Card Last 4 | 1234 |
| Card Variant | Rewards+ Card |
| Billing Cycle | Jan 15, 2025 - Feb 15, 2025 |
| Payment Due Date | Mar 10, 2025 |
| Total Balance | 25,432.10 |

### Transactions Table
| Date | Description | Amount |
|------|--------------|---------|
| 01/25/2025 | AMAZON MARKETPLACE | 799.00 |
| 01/27/2025 | STARBUCKS | 250.00 |
| 02/05/2025 | NETFLIX.COM | 499.00 |

---

## 🧩 Key Modules Explained

### 1️⃣ `extract_text_and_tables()`
Extracts both raw text and tabular data from each page of the PDF using `pdfplumber`.

### 2️⃣ `detect_issuer()`
Heuristic-based detection of which issuer’s statement it is by searching for issuer keywords in text.

### 3️⃣ `ISSUER_PARSERS`
Dictionary mapping each issuer’s name to its parsing logic function.

### 4️⃣ `extract_transactions_from_tables()`
Cleans and standardizes transaction tables into a pandas DataFrame.

### 5️⃣ `Streamlit UI`
Displays parsed information interactively, including:
- Summary metrics
- Transaction table with export
- Raw text snippet for debugging

---

## 🧪 Future Enhancements
- [ ] Add OCR (e.g., Tesseract) for scanned PDF support.
- [ ] Enhance issuer-specific regex patterns.
- [ ] Improve multi-page transaction detection.
- [ ] Add visualization for monthly spend summary.
- [ ] Integrate a backend API for multi-user use.

---

## ⚠️ Limitations
- Works best with text-based PDFs (not scanned images).
- Accuracy depends on the layout consistency of each issuer.
- May require fine-tuning regexes for localized statement versions.

---

## 📚 References
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [Streamlit Documentation](https://docs.streamlit.io)
- [python-dateutil](https://dateutil.readthedocs.io/en/stable/)

---

## 🧑‍💻 Author
**Developed by:** [Your Name]

**Email:** your.email@example.com  
**GitHub:** [github.com/yourusername](https://github.com/yourusername)

---

## 🏁 License
This project is licensed under the **MIT License** – you’re free to use, modify, and distribute with attribution.

---

**Made with ❤️ in Python & Streamlit**
