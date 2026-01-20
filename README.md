# 🛡️ Divestment SOW Auditor v2.0

**Senior Divestment SOW Auditor & IT Contracts Expert for Shell**

AI-powered tool to audit Statement of Work (SOW) documents for IT divestment projects, ensuring fixed-cost compliance, timeline validation, and contract protection.

---

## 📋 Features

### ✅ 9 Mandatory Pillars Analysis
1. **Pricing Model** - Fixed Cost validation (flags Time & Material)
2. **Responsibilities** - Shell vs Vendor clarity
3. **Schedule** - Build/Test/Cutover phase alignment
4. **Licensing** - Temporary licenses with dates/costs
5. **Master Contract Reference** - MSA/Contract linkage
6. **Sign-off Blocks** - Formal signature spaces
7. **Change Management** - Scope change processes
8. **Risk & Terms Mitigation** - Vendor-favoring clauses
9. **Data Handling** - Data verification for extraction

### 🤖 AI-Powered Analysis
- **Deepseek AI** integration for intelligent document analysis
- **OCR Support** for scanned PDFs
- **Table Extraction** for cost breakdown analysis

### 📊 Professional Reporting
- **Executive Summary** (3 sentences + Go/No-Go)
- **Compliance Scorecard** (Met/Partial/Not Met)
- **Critical Risks** (bullet points with escalation flags)
- **Actionable Redlines** (specific text changes)

### 📧 Automated Notifications
- Email reports to Vendor Owner
- PDF attachments with detailed analysis
- HTML-formatted highlights

---

## 🚀 Installation Guide

### Step 1: Prerequisites

**Install Python 3.9 or higher:**
```bash
python --version  # Should be 3.9+
```

**Install Tesseract OCR (for scanned PDFs):**
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Step 2: Project Setup

**1. Create project directory:**
```bash
mkdir SOW_Auditor_Divestment
cd SOW_Auditor_Divestment
```

**2. Create folder structure:**
```
SOW_Auditor_Divestment/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── modules/
│   ├── __init__.py
│   ├── document_parser.py
│   ├── llm_analyzer.py
│   ├── pillar_checker.py
│   ├── report_generator.py
│   └── email_notification.py
└── reports/
    ├── pdf/
    └── json/
```

**3. Create modules directory:**
```bash
mkdir modules
mkdir reports
mkdir reports/pdf
mkdir reports/json
```

### Step 3: Install Files

**Copy all provided files:**
- Place `app.py` in root directory
- Place `config.py` in root directory
- Place `requirements.txt` in root directory
- Place all `modules_*.py` files in `modules/` directory (rename by removing prefix)
  - `modules_document_parser.py` → `modules/document_parser.py`
  - `modules_llm_analyzer.py` → `modules/llm_analyzer.py`
  - `modules_pillar_checker.py` → `modules/pillar_checker.py`
  - `modules_report_generator.py` → `modules/report_generator.py`
  - `modules_email_notification.py` → `modules/email_notification.py`
  - `modules__init__.py` → `modules/__init__.py`

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Or install individually:**
```bash
pip install customtkinter==5.2.2
pip install python-dotenv==1.0.0
pip install PyPDF2==3.0.1
pip install pdfplumber==0.10.3
pip install pdf2image==1.16.3
pip install python-docx==1.1.0
pip install pytesseract==0.3.10
pip install Pillow==10.2.0
pip install requests==2.31.0
pip install reportlab==4.0.9
```

### Step 5: Configuration

**1. Create `.env` file:**
```bash
# Copy template
cp .env.template .env

# Edit .env with your values
```

**2. Configure `.env`:**
```ini
# Deepseek AI API Key (REQUIRED)
DEEPSEEK_API_KEY=sk-your-actual-api-key

# Email Settings (REQUIRED for notifications)
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENT=vendor_owner@company.com

# Optional: Tesseract path (Windows only, if not in PATH)
# TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**3. Get Deepseek API Key:**
- Visit https://platform.deepseek.com/
- Sign up and create API key
- Copy key to `.env` file

**4. Setup Gmail App Password (if using Gmail):**
- Go to Google Account → Security
- Enable 2-Factor Authentication
- Generate App Password for "Mail"
- Use this password in `.env`

---

## 🎯 Usage Guide

### Quick Start

**1. Launch application:**
```bash
python app.py
```

**2. Upload SOW document:**
- Click "📁 Browse SOW Document"
- Select PDF or DOCX file

**3. Enter project timeline:**
- Click "🔍 Start Compliance Audit"
- Fill in:
  - Project Name (e.g., "Shell Penguins Divestment")
  - Build Phase End Date (YYYY-MM-DD)
  - Test Phase End Date (YYYY-MM-DD)
  - Cutover Phase End Date (YYYY-MM-DD)

**4. Wait for analysis:**
- AI will analyze document (10-60 seconds)
- Progress bar shows current step

**5. Review results:**
- Executive Summary
- 9 Pillar Compliance Scorecard
- Critical Risks
- Actionable Redlines

**6. Export/Email:**
- Click "📄 Export PDF Report" to save locally
- Click "📧 Email to Vendor Owner" to send report

---

## 📖 Understanding the 9 Pillars

### 1. Pricing Model (CRITICAL)
**Must Be:** Fixed Cost
**Red Flag:** Time & Material, hourly rates
**Example Pass:** "Total Fixed Cost: $500,000"
**Example Fail:** "Rates: $150/hour"

### 2. Responsibilities
**Must Have:** Clear Shell vs Vendor RACI
**Example Pass:** "Vendor responsible for data extraction. Shell responsible for verification."
**Example Fail:** "Both parties will collaborate on data activities"

### 3. Schedule
**Must Have:** Explicit Build/Test/Cutover dates
**Example Pass:** 
- Build: Jan 1 - Mar 31, 2026
- Test: Apr 1 - May 15, 2026
- Cutover: May 16 - Jun 30, 2026

### 4. Licensing
**Must Have:** Temporary licenses with dates and costs
**Example Pass:** "Test environment license: $5,000, valid Feb 1 - May 31, 2026"

### 5. Master Contract Reference
**Must Have:** Explicit MSA reference
**Example Pass:** "This SOW is governed by MSA #12345 dated Jan 1, 2020"

### 6. Sign-off Blocks
**Must Have:** Signature spaces for Shell and Vendor
**Example:** Space for authorized signatories with date fields

### 7. Change Management
**Must Have:** Clear change request process
**Example Pass:** "All scope changes require written change request approved by both parties within 5 business days"

### 8. Risk & Terms Mitigation
**Check For:** Vendor-favoring clauses
**Red Flag:** "Vendor not liable for delays", "Force majeure applies to all timeline delays"

### 9. Data Handling
**For Extraction Scope:** Data verification step
**Example Pass:** "Data verification phase: 2 weeks post-extraction before final cutover"

---

## 🔍 Troubleshooting

### Issue: "DEEPSEEK_API_KEY not found"
**Solution:** Create `.env` file with valid API key

### Issue: OCR not working on scanned PDFs
**Solution:** 
1. Install Tesseract OCR
2. Add to PATH or set `TESSERACT_PATH` in `.env`

### Issue: Email sending fails
**Solution:**
1. Check Gmail App Password (not regular password)
2. Verify SMTP settings in `config.py`
3. Check firewall/network allows port 587

### Issue: "Invalid pillar: Timeline"
**Solution:** App uses "Schedule" not "Timeline" - already fixed in provided files

### Issue: PDF generation fails
**Solution:**
1. Check `reports/pdf/` directory exists
2. Ensure write permissions
3. Install reportlab: `pip install reportlab`

---

## 📊 Sample Output

### Console Output:
```
📖 Parsing SOW document (OCR if needed)...
📊 Extracting cost tables and schedules...
🤖 Analyzing with Deepseek AI (9 Mandatory Pillars)...
✅ Validating compliance against 9 pillars...
📊 Calculating compliance score...
⚠️ Checking for critical risks...
📝 Preparing audit report...
✅ Audit complete!
✅ PDF report generated: reports/pdf/SOW_Audit_Shell_Penguins_20260103_182430.pdf
```

### Audit Report Sections:
1. **Executive Summary** - 3-sentence overview
2. **Go/No-Go Recommendation** - Clear decision
3. **Compliance Score** - Percentage (0-100%)
4. **9 Pillar Scorecard** - Met/Partial/Not Met for each
5. **Critical Risks** - Bullet points with escalation flags
6. **Actionable Redlines** - Specific text changes

---

## 🛠️ Advanced Configuration

### Customize Pillars (config.py):
```python
PILLARS = [
    'Your Custom Pillar 1',
    'Your Custom Pillar 2',
    ...
]
```

### Adjust AI Temperature (config.py):
```python
DEEPSEEK_TEMPERATURE = 0.3  # Lower = more consistent
```

### Change Email Template (modules/email_notification.py):
Edit `_create_html_body()` method

---

## 📝 License

Internal use only for Shell IT Divestment Projects.

---

## 🆘 Support

For issues or questions:
1. Check troubleshooting section above
2. Review `.env` configuration
3. Verify all dependencies installed
4. Check `reports/` directory permissions

---

## 🎉 Version History

**v2.0 (Current)**
- ✅ 9 Mandatory Pillars implementation
- ✅ Deepseek AI integration
- ✅ OCR support for scanned PDFs
- ✅ Table extraction for cost analysis
- ✅ Professional PDF reports
- ✅ Email notifications
- ✅ Critical risk escalation
- ✅ Actionable redlines

---

**Built with ❤️ for Shell IT Divestment Projects**
