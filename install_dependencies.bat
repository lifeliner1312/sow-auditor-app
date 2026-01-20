@echo off
echo ============================================================
echo  Divestment SOW Auditor - Dependency Installer (Python 3.13)
echo ============================================================
echo.

echo [1/10] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [2/10] Installing CustomTkinter...
pip install customtkinter==5.2.2

echo.
echo [3/10] Installing python-dotenv...
pip install python-dotenv==1.0.0

echo.
echo [4/10] Installing PyPDF2...
pip install PyPDF2==3.0.1

echo.
echo [5/10] Installing pdfplumber...
pip install pdfplumber==0.11.4

echo.
echo [6/10] Installing python-docx...
pip install python-docx==1.1.2

echo.
echo [7/10] Installing requests...
pip install requests==2.31.0

echo.
echo [8/10] Installing reportlab...
pip install reportlab==4.2.5

echo.
echo [9/10] Installing Pillow (may take a moment)...
pip install Pillow --upgrade --no-cache-dir

echo.
echo [10/10] Installing pytesseract...
pip install pytesseract==0.3.13

echo.
echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo Testing imports...
python -c "import customtkinter; print('✓ CustomTkinter OK')" || echo ✗ CustomTkinter FAILED
python -c "import pdfplumber; print('✓ PDFplumber OK')" || echo ✗ PDFplumber FAILED
python -c "import docx; print('✓ python-docx OK')" || echo ✗ python-docx FAILED
python -c "import requests; print('✓ Requests OK')" || echo ✗ Requests FAILED
python -c "import reportlab; print('✓ Reportlab OK')" || echo ✗ Reportlab FAILED
python -c "from dotenv import load_dotenv; print('✓ python-dotenv OK')" || echo ✗ python-dotenv FAILED

echo.
echo ============================================================
echo  Next Steps:
echo  1. Copy .env.template to .env
echo  2. Add your Deepseek API key to .env
echo  3. Run: python app.py
echo ============================================================
echo.
pause
