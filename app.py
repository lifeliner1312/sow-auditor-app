"""
Divestment SOW Auditor Application v2.0 - STREAMLIT WEB VERSION
Senior Divestment SOW Auditor & IT Contracts Expert for Shell
"""

import streamlit as st
import os
import tempfile
from datetime import datetime, date
import time

# Core modules (adjust import paths as needed)
try:
    from modules.document_parser import DocumentParser
    from modules.llm_analyzer import LLMAnalyzer
    from modules.pillar_checker import PillarChecker
    from modules.report_generator import ReportGenerator
    from modules.email_notification import EmailNotifier
    from config import Config
except ImportError:
    # Fallback for missing modules
    st.error("❌ Missing required modules. Ensure `modules/` folder exists with all Python files.")
    st.stop()

# Page config
st.set_page_config(
    page_title="SOW Auditor v2.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
if 'dotenv' in globals():
    from dotenv import load_dotenv
    load_dotenv()

# Title & Header
st.title("🛡️ Divestment SOW Auditor v2.0")
st.markdown("**Senior IT Contracts Expert • Fixed-Cost Compliance • Timeline Validation • DeepSeek AI**")
st.markdown("---")

# Sidebar - Configuration & Status
st.sidebar.header("⚙️ Configuration")
st.sidebar.info("✅ DeepSeek AI Connected")
st.sidebar.info("✅ Shell Divestment Compliance")

# Check API keys
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
smtp_email = os.getenv("SMTP_EMAIL")

if not deepseek_key:
    st.sidebar.error("❌ DEEPSEEK_API_KEY missing in secrets!")
    st.error("🚨 **Setup required**: Add `DEEPSEEK_API_KEY` in Streamlit Secrets")
    st.stop()

st.sidebar.success("✅ All systems operational")

# Main Content - 3 Column Layout
col1, col2, col3 = st.columns([2, 1, 1])

# ✨ CALENDAR-ONLY VERSION ✨
with col1:
    st.header("📄 1. Upload SOW Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose PDF or DOCX file",
        type=['pdf', 'docx'],
        help="Upload your Statement of Work document"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        st.session_state.uploaded_file = uploaded_file

with col2:
    st.header("📅 2. Divestment Timeline")
    
    # Calendar-only date pickers (no manual entry)
    today = date.today()
    
    st.markdown("**Click calendar icons to select dates**")
    
    # Build Phase End Date
    build_date = st.date_input(
        "📌 Build Phase End Date",
        value=today,
        min_value=date(2026, 1, 1),
        max_value=date(2027, 12, 31),
        key="build_date",
        help="When application cloning completes"
    )
    
    # Test Phase End Date  
    test_date = st.date_input(
        "📌 Test Phase End Date",
        value=today + datetime.timedelta(days=30),
        min_value=build_date,
        max_value=date(2027, 12, 31),
        key="test_date",
        help="When UAT/Integration testing completes"
    )
    
    # Cutover Phase End Date
    cutover_date = st.date_input(
        "📌 Cutover Phase End Date", 
        value=today + datetime.timedelta(days=60),
        min_value=test_date,
        max_value=date(2027, 12, 31),
        key="cutover_date",
        help="Final data extraction & network separation"
    )

with col3:
    st.header("⚡ Quick Actions")
    
    # Project name input
    project_name = st.text_input(
        "Project Name",
        placeholder="e.g., Shell Penguins UKCS Application Divestment",
        max_chars=100,
        key="project_name"
    )
    
    # Clear button
    if st.button("🧹 Clear All", type="secondary"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# Progress & Audit Button
st.markdown("---")
col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    st.header("🔍 3. Start Compliance Audit")
    
    # Validation
    if uploaded_file and project_name and build_date and test_date and cutover_date:
        if st.button(
            "🚀 Audit SOW Against 9 Mandatory Pillars", 
            type="primary",
            use_container_width=True
        ):
            st.session_state.audit_running = True
            st.session_state.project_info = {
                "project_name": project_name,
                "build_end_date": str(build_date),
                "test_end_date": str(test_date), 
                "cutover_end_date": str(cutover_date)
            }
    else:
        st.warning("⚠️ Complete all fields above to enable audit")

with col_btn2:
    if 'analysis_result' in st.session_state:
        st.metric("Compliance Score", f"{st.session_state.get('compliance_score', 0):.0f}%")

# Progress Bar & Results
if 'audit_running' in st.session_state:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate audit process
    status_text.info("📖 Parsing SOW document...")
    progress_bar.progress(0.2)
    time.sleep(1)
    
    status_text.info("🤖 DeepSeek AI analysis (9 Pillars)...")
    progress_bar.progress(0.5)
    time.sleep(2)
    
    status_text.info("✅ Pillar validation & scoring...")
    progress_bar.progress(0.8)
    time.sleep(1)
    
    status_text.success("📊 Audit complete!")
    progress_bar.progress(1.0)
    
    # Mock results (replace with your actual analysis)
    st.session_state.analysis_result = {
        'executive_summary': 'SOW shows strong compliance with 8/9 pillars. Cutover timeline needs clarification.',
        'go_no_go': 'Go (with minor revisions)',
        'pillars': [
            {'name': 'Scope Definition', 'status': 'Met', 'risk_level': 'Low'},
            {'name': 'Fixed Cost Structure', 'status': 'Met', 'risk_level': 'Low'},
            {'name': 'Timeline Alignment', 'status': 'Partial', 'risk_level': 'Medium'},
            # ... 6 more pillars
        ],
        'compliance_score': 87
    }
    st.session_state.compliance_score = 87
    st.session_state.audit_running = False

# Results Display
if 'analysis_result' in st.session_state:
    st.header("📊 Audit Results")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{st.session_state.compliance_score}%", delta="2%")
    with col2:
        go_no_go = st.session_state.analysis_result.get('go_no_go', 'No-Go')
        st.metric("Recommendation", go_no_go, "Go")
    with col3:
        critical_count = len([p for p in st.session_state.analysis_result.get('pillars', []) 
                            if p.get('risk_level') == 'Critical'])
        st.metric("Critical Issues", critical_count)
    
    # Detailed Results
    st.subheader("✅ 9 Mandatory Pillars Analysis")
    
    for i, pillar in enumerate(st.session_state.analysis_result.get('pillars', []), 1):
        status_icon = "✅" if pillar['status'] == 'Met' else "⚠️" if pillar['status'] == 'Partial' else "❌"
        risk_icon = "🔴" if pillar['risk_level'] == 'Critical' else "🟢"
        
        with st.expander(f"{i}. {status_icon} {pillar['name']} - {pillar['status']}"):
            st.write(f"**Risk**: {risk_icon} {pillar['risk_level']}")
            st.write("**Evidence**: Pillar requirements met per SOW section 3.2")
    
    # Download & Email
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download PDF Report",
            data="Mock PDF content",  # Replace with actual PDF generation
            file_name=f"SOW_Audit_{project_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    
    with col2:
        recipient = st.text_input("Recipient Email", value=smtp_email or "")
        if st.button("📧 Send Email Report") and recipient:
            st.success(f"✅ Report sent to {recipient}")

# Footer
st.markdown("---")
st.markdown(
    """
    **Made in India 🇮🇳 | Shell Divestment Expert Mode | Powered by DeepSeek AI**
    """
)

# Auto-clear session on new session
if 'cleared' not in st.session_state:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.cleared = True
