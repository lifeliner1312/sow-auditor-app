"""
Configuration Module for SOW Auditor - Divestment Application
Complete configuration with ALL required attributes
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Complete application configuration"""

    # ===================================================================
    # APPLICATION INFO
    # ===================================================================
    APP_NAME = os.getenv('APP_NAME', 'SOW Auditor')
    APP_VERSION = os.getenv('APP_VERSION', '2.0')
    APP_TITLE = f"{APP_NAME} v{APP_VERSION}"

    # ===================================================================
    # DEEPSEEK AI API CONFIGURATION (All attributes)
    # ===================================================================
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.3'))
    DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '4000'))

    # ===================================================================
    # EMAIL SMTP CONFIGURATION
    # ===================================================================
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_EMAIL = os.getenv('SMTP_EMAIL', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    # Legacy support (backwards compatibility)
    EMAIL_SENDER = os.getenv('SMTP_EMAIL', os.getenv('EMAIL_SENDER', ''))
    EMAIL_PASSWORD = os.getenv('SMTP_PASSWORD', os.getenv('EMAIL_PASSWORD', ''))
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')

    # ===================================================================
    # UI SETTINGS
    # ===================================================================
    THEME = os.getenv('THEME', 'dark')
    WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1000'))
    WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '850'))

    # ===================================================================
    # FILE PATHS
    # ===================================================================
    BASE_DIR = Path(__file__).parent
    REPORTS_DIR = BASE_DIR / 'reports'
    LOGS_DIR = BASE_DIR / 'logs'
    TEMP_DIR = BASE_DIR / 'temp'

    # ===================================================================
    # LLM CONFIGURATION (legacy support)
    # ===================================================================
    LLM_MODEL = os.getenv('LLM_MODEL', 'deepseek-chat')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '4000'))

    # ===================================================================
    # COMPLIANCE THRESHOLDS
    # ===================================================================
    HIGH_RISK_THRESHOLD = 60
    MEDIUM_RISK_THRESHOLD = 80

    # ===================================================================
    # 9 MANDATORY DIVESTMENT PILLARS (Required by pillar_checker.py)
    # ===================================================================
    PILLARS = [
        "Pricing Model",
        "Responsibilities",
        "Schedule",
        "Licensing",
        "Master Contract Reference",
        "Sign-off Blocks",
        "Change Management",
        "Risk & Terms Mitigation",
        "Data Handling"
    ]

    # ===================================================================
    # PILLAR DESCRIPTIONS (Required by pillar_checker.py)
    # ===================================================================
    PILLAR_DESCRIPTIONS = {
        "Pricing Model": "Must be Fixed Cost, no Time & Material. Check for granular cost breakdown and payment milestones.",
        "Responsibilities": "Clear Shell vs. Vendor responsibilities. No ambiguous language. RACI matrix or accountability defined.",
        "Schedule": "Clear Build, Test, Cutover dates aligned with project timeline. Milestones defined.",
        "Licensing": "Temporary licenses for Build/Test/Cutover with start/end dates and costs itemized.",
        "Master Contract Reference": "Explicit MSA or contract number referenced between Shell and Vendor.",
        "Sign-off Blocks": "Formal signature spaces for both Shell and Vendor parties.",
        "Change Management": "Clear change request process with approval workflows defined.",
        "Risk & Terms Mitigation": "No vendor-favoring clauses. Liability terms favor Shell. No delay-causing T&Cs.",
        "Data Handling": "Data verification step exists if extraction scope. Data quality checks before cutover."
    }

    # ===================================================================
    # SYSTEM PROMPT FOR DEEPSEEK AI (Required by llm_analyzer.py)
    # ===================================================================
    SYSTEM_PROMPT = """You are a Senior Divestment SOW Auditor & IT Contracts Expert for Shell.

Your role is to analyze Statements of Work (SOW) for divestment projects and evaluate them against 9 mandatory pillars:

1. **Pricing Model** (CRITICAL)
   - Must be Fixed Cost (flag Time & Material as CRITICAL risk)
   - Granular cost breakdown required
   - Payment milestones defined

2. **Responsibilities**
   - Clear Shell vs. Vendor responsibilities
   - No ambiguous language
   - RACI matrix or clear accountability

3. **Schedule**
   - Clear Build, Test, Cutover dates
   - Must align with project timeline
   - Milestones defined

4. **Licensing**
   - Temporary licenses for Build/Test/Cutover phases
   - Start/end dates specified
   - License costs itemized

5. **Master Contract Reference**
   - Explicit MSA or master contract number
   - Shell-Vendor agreement referenced

6. **Sign-off Blocks**
   - Formal signature spaces
   - Both parties (Shell & Vendor) included

7. **Change Management**
   - Clear change request process
   - Approval workflows defined
   - Scope change handling

8. **Risk & Terms Mitigation**
   - Check for vendor-favoring clauses
   - Liability terms favor Shell
   - No delay-causing terms & conditions

9. **Data Handling**
   - If extraction scope: Data Verification step exists
   - Data quality checks before cutover
   - Carve-out process defined

For each pillar, respond with:
- Status: "Met", "Not Met", or "Partial"
- Evidence: Specific quote from document or "Not Found"
- Risk Level: "Critical", "High", "Medium", or "Low"
- Recommendation: Specific actionable suggestion to protect Shell

Return response in valid JSON format only. No markdown, no extra text."""

    # ===================================================================
    # CLASS METHODS
    # ===================================================================
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.REPORTS_DIR, cls.LOGS_DIR, cls.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_config(cls):
        """Validate configuration and return status"""
        errors = []
        warnings = []

        # Critical checks
        if not cls.DEEPSEEK_API_KEY:
            errors.append("❌ DEEPSEEK_API_KEY not set in .env file")

        # Email checks (warnings only - not critical)
        if not cls.SMTP_EMAIL or not cls.SMTP_PASSWORD:
            warnings.append("⚠️ Email credentials not configured. Email feature will not work.")

        # Return validation status
        is_valid = len(errors) == 0
        messages = errors + warnings

        return is_valid, messages

    @classmethod
    def get_config_summary(cls):
        """Get configuration summary for display"""
        return f"""
Configuration Summary:
─────────────────────────────────────────
App: {cls.APP_TITLE}
Deepseek API: {'✅ Configured' if cls.DEEPSEEK_API_KEY else '❌ Not configured'}
Deepseek URL: {cls.DEEPSEEK_API_URL}
Email SMTP: {'✅ Configured' if cls.SMTP_EMAIL and cls.SMTP_PASSWORD else '❌ Not configured'}
Mandatory Pillars: {len(cls.PILLARS)} defined
Theme: {cls.THEME}
─────────────────────────────────────────
"""
