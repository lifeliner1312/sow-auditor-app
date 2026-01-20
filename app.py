"""
Divestment SOW Auditor Application v2.0 - CALENDAR ONLY VERSION
Senior Divestment SOW Auditor & IT Contracts Expert for Shell

FEATURE: Calendar picker ONLY (no manual entry) - Improved alignment and functionality
"""

import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading

# Calendar widget import
try:
    from tkcalendar import Calendar
    import tkinter as tk
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("⚠️ Error: tkcalendar not installed.")
    print("   Install with: pip install tkcalendar")

# Import modules
from modules.document_parser import DocumentParser
from modules.llm_analyzer import LLMAnalyzer
from modules.pillar_checker import PillarChecker
from modules.report_generator import ReportGenerator
from modules.email_notification import EmailNotifier
from config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CalendarDialog(ctk.CTkToplevel):
    """Custom calendar dialog with proper alignment and date selection"""

    def __init__(self, parent, title="Select Date", initial_date=None):
        super().__init__(parent)

        self.title(title)
        self.geometry("350x400")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"350x400+{x}+{y}")

        self.selected_date = None

        # Create calendar widget
        self._create_calendar(initial_date)

    def _create_calendar(self, initial_date):
        """Create calendar widget with proper configuration"""

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="📅 Select Date",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)

        # Calendar frame (using tkinter frame for proper rendering)
        cal_frame = tk.Frame(self, bg='white')
        cal_frame.pack(pady=10, padx=20)

        # Set initial date
        if initial_date:
            year, month, day = initial_date.year, initial_date.month, initial_date.day
        else:
            today = datetime.now()
            year, month, day = today.year, today.month, today.day

        # Create calendar with proper styling
        self.calendar = Calendar(
            cal_frame,
            selectmode='day',
            year=year,
            month=month,
            day=day,
            date_pattern='yyyy-mm-dd',
            background='#1f4788',
            foreground='white',
            bordercolor='#1f4788',
            headersbackground='#163863',
            headersforeground='white',
            selectbackground='#667eea',
            selectforeground='white',
            weekendbackground='#f0f0f0',
            weekendforeground='black',
            othermonthbackground='#e0e0e0',
            othermonthforeground='gray',
            othermonthwebackground='#e0e0e0',
            othermonthweforeground='gray',
            font=('Arial', 10),
            showweeknumbers=False
        )
        self.calendar.pack(padx=10, pady=10)

        # Selected date display
        self.date_display = ctk.CTkLabel(
            self,
            text=f"Selected: {year}-{month:02d}-{day:02d}",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.date_display.pack(pady=10)

        # Update display on date selection
        self.calendar.bind("<<CalendarSelected>>", self._on_date_selected)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=15, padx=20, fill="x")

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=120,
            height=35,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)

        ok_btn = ctk.CTkButton(
            button_frame,
            text="Select Date",
            command=self._on_ok,
            width=120,
            height=35
        )
        ok_btn.pack(side="right", padx=5)

    def _on_date_selected(self, event):
        """Update display when date is selected"""
        date = self.calendar.get_date()
        self.date_display.configure(text=f"Selected: {date}")

    def _on_ok(self):
        """Confirm selection"""
        self.selected_date = self.calendar.get_date()
        self.destroy()

    def _on_cancel(self):
        """Cancel selection"""
        self.selected_date = None
        self.destroy()

    def get_date(self):
        """Return selected date"""
        return self.selected_date


class SOWAuditorApp(ctk.CTk):
    """Main SOW Auditor Application with Calendar-Only Date Selection"""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title(f"{Config.APP_TITLE} v{Config.APP_VERSION}")
        self.geometry("1000x850")

        # Set theme
        ctk.set_appearance_mode(Config.THEME)
        ctk.set_default_color_theme("blue")

        # Validate configuration
        is_valid, errors = Config.validate_config()
        if not is_valid:
            messagebox.showwarning("Configuration Issues", "\n".join(errors))

        # Initialize components
        self.llm_analyzer = LLMAnalyzer()
        self.pillar_checker = PillarChecker()
        self.report_generator = ReportGenerator()
        self.email_notifier = EmailNotifier()

        # Variables
        self.current_file = None
        self.analysis_result = None
        self.project_info = None

        # Date storage
        self.build_date = None
        self.test_date = None
        self.cutover_date = None

        # Create directories
        Config.create_directories()

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create application UI with calendar-only date selection"""

        # Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1f4788", height=100)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🛡️ Divestment SOW Auditor",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(15, 5))

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Senior IT Contracts Expert • Fixed-Cost Compliance • Timeline Validation • Deepseek AI",
            font=ctk.CTkFont(size=12),
            text_color="#e0e0e0"
        )
        subtitle_label.pack(pady=(0, 15))

        # Main Content Frame with Scrollbar
        main_content = ctk.CTkScrollableFrame(self, corner_radius=0)
        main_content.pack(fill="both", expand=True, padx=0, pady=0)

        # File Selection Frame
        file_frame = ctk.CTkFrame(main_content, corner_radius=10)
        file_frame.pack(pady=20, padx=30, fill="x")

        ctk.CTkLabel(
            file_frame,
            text="📄 1. Upload SOW Document (PDF/DOCX)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")

        self.file_path_label = ctk.CTkLabel(
            file_frame,
            text="No document selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.file_path_label.pack(pady=5, padx=20, anchor="w")

        ctk.CTkButton(
            file_frame,
            text="📁 Browse SOW Document",
            command=self.select_file,
            width=220,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=15, padx=20, anchor="w")

        # ✨✨✨ CALENDAR-ONLY: Project Timeline Frame ✨✨✨
        timeline_frame = ctk.CTkFrame(main_content, corner_radius=10)
        timeline_frame.pack(pady=10, padx=30, fill="x")

        ctk.CTkLabel(
            timeline_frame,
            text="📅 2. Enter Divestment Project Timeline",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")

        ctk.CTkLabel(
            timeline_frame,
            text="Click the calendar button to select dates",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(0, 15), padx=20, anchor="w")

        # Project Name
        ctk.CTkLabel(
            timeline_frame,
            text="Project Name:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(5, 5), padx=20, anchor="w")

        self.project_name_entry = ctk.CTkEntry(
            timeline_frame,
            placeholder_text="e.g., Shell Penguins UKCS Application Divestment",
            width=600,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.project_name_entry.pack(pady=(0, 15), padx=20, anchor="w")

        # Build Phase End Date
        self._create_calendar_button_field(
            timeline_frame,
            "Build Phase End Date:",
            "build",
            "📌 When application cloning completes"
        )

        # Test Phase End Date
        self._create_calendar_button_field(
            timeline_frame,
            "Test Phase End Date:",
            "test",
            "📌 When UAT/Integration testing completes"
        )

        # Cutover Phase End Date
        self._create_calendar_button_field(
            timeline_frame,
            "Cutover Phase End Date:",
            "cutover",
            "📌 Final data extraction & network separation"
        )

        # Audit Button Frame
        audit_frame = ctk.CTkFrame(main_content, corner_radius=10)
        audit_frame.pack(pady=10, padx=30, fill="x")

        ctk.CTkLabel(
            audit_frame,
            text="🔍 3. Start Compliance Audit",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")

        self.audit_btn = ctk.CTkButton(
            audit_frame,
            text="🔍 Audit SOW Against 9 Mandatory Pillars",
            command=self.start_audit,
            width=300,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1f4788",
            hover_color="#163863",
            state="disabled"
        )
        self.audit_btn.pack(pady=15, padx=20)

        # Progress Frame
        progress_frame = ctk.CTkFrame(main_content, corner_radius=10)
        progress_frame.pack(pady=10, padx=30, fill="x")

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to audit SOW document",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=15, padx=20)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(pady=(0, 15), padx=20, fill="x")
        self.progress_bar.set(0)

        # Results Frame
        results_frame = ctk.CTkFrame(main_content, corner_radius=10)
        results_frame.pack(pady=10, padx=30, fill="both", expand=True)

        ctk.CTkLabel(
            results_frame,
            text="📊 Audit Results (9 Mandatory Pillars):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")

        self.results_text = ctk.CTkTextbox(
            results_frame,
            font=ctk.CTkFont(size=11),
            wrap="word",
            height=300
        )
        self.results_text.pack(pady=10, padx=20, fill="both", expand=True)

        # Action Buttons Frame
        action_frame = ctk.CTkFrame(main_content, corner_radius=10)
        action_frame.pack(pady=10, padx=30, fill="x")

        button_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        button_container.pack(pady=15, padx=20)

        self.export_pdf_btn = ctk.CTkButton(
            button_container,
            text="📄 Export PDF Report",
            command=self.export_pdf,
            width=200,
            height=45,
            state="disabled"
        )
        self.export_pdf_btn.pack(side="left", padx=10)

        self.send_email_btn = ctk.CTkButton(
            button_container,
            text="📧 Send Email",
            command=self.send_email,
            width=200,
            height=45,
            state="disabled"
        )
        self.send_email_btn.pack(side="left", padx=10)

        # Status bar
        status_frame = ctk.CTkFrame(self, corner_radius=0, height=30)
        status_frame.pack(fill="x", side="bottom", padx=0, pady=0)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready • Deepseek AI Connected • Shell IT Contracts Expert Mode",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.status_label.pack(pady=5, padx=30, anchor="w")

    def _create_calendar_button_field(self, parent, label_text, field_name, hint_text):
        """
        ✨ Create calendar-only date selection field

        Args:
            parent: Parent frame
            label_text: Label for the date field
            field_name: Field identifier (build/test/cutover)
            hint_text: Hint text to display
        """
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(5, 5), padx=20, anchor="w")

        date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        date_frame.pack(pady=(0, 15), padx=20, fill="x")

        # Calendar button
        cal_button = ctk.CTkButton(
            date_frame,
            text="📅 Select Date",
            width=150,
            height=35,
            command=lambda: self._open_calendar(field_name),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cal_button.pack(side="left", padx=(0, 15))

        # Date display label
        date_label = ctk.CTkLabel(
            date_frame,
            text="No date selected",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            width=200,
            anchor="w"
        )
        date_label.pack(side="left", padx=(0, 15))

        # Store references
        setattr(self, f"{field_name}_button", cal_button)
        setattr(self, f"{field_name}_label", date_label)

        # Hint label
        ctk.CTkLabel(
            date_frame,
            text=hint_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="left")

    def _open_calendar(self, field_name):
        """
        ✨ Open calendar dialog for date selection

        Args:
            field_name: Field identifier (build/test/cutover)
        """
        if not CALENDAR_AVAILABLE:
            messagebox.showerror(
                "Calendar Not Available",
                "tkcalendar library not installed.\n\nInstall with: pip install tkcalendar"
            )
            return

        # Get current date for this field if set
        current_date = getattr(self, f"{field_name}_date", None)
        if current_date:
            try:
                initial_date = datetime.strptime(current_date, "%Y-%m-%d")
            except:
                initial_date = datetime.now()
        else:
            initial_date = datetime.now()

        # Open calendar dialog
        dialog = CalendarDialog(self, title=f"Select {field_name.title()} Date", initial_date=initial_date)
        self.wait_window(dialog)

        # Get selected date
        selected_date = dialog.get_date()

        if selected_date:
            # Store date
            setattr(self, f"{field_name}_date", selected_date)

            # Update label
            label = getattr(self, f"{field_name}_label", None)
            if label:
                label.configure(text=f"✅ {selected_date}", text_color="#1f4788")

            # Update status
            self.status_label.configure(text=f"✅ {field_name.title()} date set to: {selected_date}")

    def select_file(self):
        """Select SOW document"""
        file_types = [
            ("All Supported", "*.pdf;*.docx"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx")
        ]

        filename = filedialog.askopenfilename(
            title="Select SOW Document",
            filetypes=file_types
        )

        if filename:
            self.current_file = filename
            display_name = os.path.basename(filename)
            if len(display_name) > 60:
                display_name = display_name[:57] + "..."
            self.file_path_label.configure(text=f"✅ {display_name}")
            self.audit_btn.configure(state="normal")
            self.status_label.configure(text=f"Document loaded: {os.path.basename(filename)}")

    def validate_date(self, date_str):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_inputs(self):
        """Validate all inputs"""

        # Check file
        if not self.current_file:
            messagebox.showwarning("No Document", "Please select a SOW document first.")
            return False

        # Get values
        project_name = self.project_name_entry.get().strip()

        # Validate project name
        if not project_name:
            messagebox.showwarning("Missing Information", "Please enter a Project Name.")
            self.project_name_entry.focus()
            return False

        # Validate build date
        if not self.build_date:
            messagebox.showwarning("Missing Date", "Please select Build Phase End Date using the calendar.")
            return False

        # Validate test date
        if not self.test_date:
            messagebox.showwarning("Missing Date", "Please select Test Phase End Date using the calendar.")
            return False

        # Validate cutover date
        if not self.cutover_date:
            messagebox.showwarning("Missing Date", "Please select Cutover Phase End Date using the calendar.")
            return False

        return True

    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)
        self.update()

    def start_audit(self):
        """Start audit process"""

        # Validate inputs
        if not self.validate_inputs():
            return

        # Get project info
        project_info = {
            "project_name": self.project_name_entry.get().strip(),
            "build_end_date": self.build_date,
            "test_end_date": self.test_date,
            "cutover_end_date": self.cutover_date
        }
        self.project_info = project_info

        # Disable buttons
        self.audit_btn.configure(state="disabled")
        self.results_text.delete("1.0", "end")
        self.analysis_result = None
        self.export_pdf_btn.configure(state="disabled")
        self.send_email_btn.configure(state="disabled")

        # Start audit in background thread
        thread = threading.Thread(target=self.perform_audit, daemon=True)
        thread.start()

    def perform_audit(self):
        """Perform SOW audit"""
        try:
            # Step 1: Parse document
            self.update_progress(0.15, "📖 Parsing SOW document (OCR if needed)...")
            document_parser = DocumentParser(self.current_file)
            document_text = document_parser.parse()

            if not document_text:
                raise Exception("Failed to extract text from document")

            metadata = document_parser.get_metadata()

            # Step 2: Extract tables
            self.update_progress(0.25, "📊 Extracting cost tables and schedules...")
            tables = []
            try:
                tables = document_parser.extract_tables()
            except:
                pass

            # Step 3: Analyze with Deepseek AI (9 Pillars)
            self.update_progress(0.45, "🤖 Analyzing with Deepseek AI (9 Mandatory Pillars)...")
            analysis_result = self.llm_analyzer.analyze_sow(
                document_text=document_text,
                project_timeline=self.project_info,
                tables=tables
            )

            # Step 3.5: Generate SOW Content Summary
            self.update_progress(0.55, "📝 Generating SOW content summary...")
            try:
                sow_content_summary = self.llm_analyzer.generate_sow_content_summary(
                    document_text=document_text,
                    tables=tables
                )
            except Exception as e:
                self.status_label.configure(text=f"⚠️ Warning: Could not generate content summary: {str(e)}")
                sow_content_summary = None

            # Step 4: Validate pillars
            self.update_progress(0.65, "✅ Validating compliance against 9 pillars...")
            is_valid, message = self.pillar_checker.validate_analysis(analysis_result)

            if not is_valid:
                raise Exception(f"Validation failed: {message}")

            # Step 5: Calculate compliance score
            self.update_progress(0.75, "📊 Calculating compliance score...")
            compliance_score = self.pillar_checker.calculate_compliance_score(analysis_result)
            analysis_result['compliance_score'] = compliance_score

            # Step 6: Check for critical failures
            self.update_progress(0.85, "⚠️ Checking for critical risks...")
            critical_failures = self.pillar_checker.get_critical_failures(analysis_result)
            analysis_result['critical_failures'] = critical_failures

            # Step 7: Display results
            self.update_progress(0.95, "📝 Preparing audit report...")
            self.analysis_result = analysis_result
            self.analysis_result['project_info'] = self.project_info
            self.analysis_result['metadata'] = metadata
            self.analysis_result['sow_content_summary'] = sow_content_summary

            self.display_results(analysis_result, compliance_score)

            # Complete
            self.update_progress(1.0, "✅ Audit complete!")

            # Enable action buttons
            self.export_pdf_btn.configure(state="normal")
            self.send_email_btn.configure(state="normal")
            self.audit_btn.configure(state="normal")
            self.status_label.configure(text="✅ Audit completed successfully")

            # Show critical warnings if any
            if critical_failures:
                messagebox.showwarning(
                    "Critical Issues Found",
                    f"⚠️ {len(critical_failures)} CRITICAL issues require immediate attention!\n\nCheck the audit report for details."
                )

        except Exception as e:
            self.update_progress(0, "❌ Audit failed")
            self.status_label.configure(text=f"Error: {str(e)}")
            messagebox.showerror("Audit Error", f"Audit failed:\n\n{str(e)}")
            self.audit_btn.configure(state="normal")

    def display_results(self, analysis, compliance_score):
        """Display audit results"""
        self.results_text.delete("1.0", "end")

        # Header
        self.results_text.insert("end", "="*85 + "\n")
        self.results_text.insert("end", f"DIVESTMENT SOW AUDIT REPORT\n")
        self.results_text.insert("end", f"Project: {self.project_info['project_name']}\n")
        self.results_text.insert("end", "="*85 + "\n\n")

        # Executive Summary
        self.results_text.insert("end", "📋 EXECUTIVE SUMMARY:\n")
        self.results_text.insert("end", f"{analysis.get('executive_summary', 'N/A')}\n\n")

        # Go/No-Go Decision
        go_no_go = analysis.get('go_no_go', 'No-Go')
        decision_icon = "🟢" if go_no_go == "Go" else "🔴"
        self.results_text.insert("end", f"{decision_icon} RECOMMENDATION: {go_no_go}\n\n")

        # Compliance Score
        risk_level = "🟢 LOW RISK" if compliance_score >= 80 else "🟡 MEDIUM RISK" if compliance_score >= 60 else "🔴 HIGH RISK"
        self.results_text.insert("end", f"📊 COMPLIANCE SCORE: {compliance_score}% ({risk_level})\n\n")

        # Project Timeline
        self.results_text.insert("end", "📅 DIVESTMENT TIMELINE:\n")
        self.results_text.insert("end", f" • Build Phase End: {self.project_info['build_end_date']}\n")
        self.results_text.insert("end", f" • Test Phase End: {self.project_info['test_end_date']}\n")
        self.results_text.insert("end", f" • Cutover Phase End: {self.project_info['cutover_end_date']}\n\n")
        self.results_text.insert("end", "-"*85 + "\n\n")

        # Compliance Scorecard (9 Pillars)
        self.results_text.insert("end", "✅ COMPLIANCE SCORECARD - 9 MANDATORY PILLARS:\n\n")

        for idx, pillar in enumerate(analysis.get('pillars', []), 1):
            status = pillar['status']
            risk = pillar['risk_level']
            status_icon = "✅" if status == "Met" else "⚠️" if status == "Partial" else "❌"
            risk_icon = "🔴" if risk == "Critical" else "🟠" if risk == "High" else "🟡" if risk == "Medium" else "🟢"

            self.results_text.insert("end", f"{idx}. {status_icon} {pillar['name']} - {status} ({risk_icon} {risk})\n")
            self.results_text.insert("end", f"   Evidence: {pillar.get('evidence', 'Not found')[:150]}...\n")

            if pillar.get('recommendation'):
                self.results_text.insert("end", f"   ⚡ Action: {pillar['recommendation']}\n")

            self.results_text.insert("end", "\n")

        # Critical Risks
        if analysis.get('critical_risks'):
            self.results_text.insert("end", "-"*85 + "\n\n")
            self.results_text.insert("end", "🚨 CRITICAL RISKS (Immediate Escalation Required):\n\n")
            for i, risk in enumerate(analysis['critical_risks'], 1):
                self.results_text.insert("end", f"{i}. {risk}\n\n")

        # Actionable Redlines
        if analysis.get('actionable_redlines'):
            self.results_text.insert("end", "-"*85 + "\n\n")
            self.results_text.insert("end", "✏️ ACTIONABLE REDLINES (Protect Shell's Interests):\n\n")
            for i, redline in enumerate(analysis['actionable_redlines'], 1):
                self.results_text.insert("end", f"{i}. {redline}\n\n")

        self.results_text.insert("end", "="*85 + "\n")

    def export_pdf(self):
        """Export PDF report"""
        if not self.analysis_result:
            messagebox.showwarning("No Results", "Please run an audit first.")
            return

        try:
            self.status_label.configure(text="Generating PDF report...")
            self.update()

            pdf_path = self.report_generator.generate_report(
                self.analysis_result,
                os.path.basename(self.current_file),
                sow_content_summary=self.analysis_result.get('sow_content_summary')
            )

            self.status_label.configure(text=f"PDF saved: {pdf_path}")
            messagebox.showinfo("PDF Generated", f"Report saved to:\n{pdf_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF:\n\n{str(e)}")

    def send_email(self):
        """Send email with PDF report"""
        if not self.analysis_result:
            messagebox.showwarning("No Results", "Please run an audit first.")
            return

        # Create custom dialog for email input
        email_dialog = ctk.CTkToplevel(self)
        email_dialog.title("Send Email Report")
        email_dialog.geometry("500x250")
        email_dialog.resizable(False, False)
        email_dialog.transient(self)
        email_dialog.grab_set()

        # Center dialog
        email_dialog.update_idletasks()
        x = (email_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (email_dialog.winfo_screenheight() // 2) - (250 // 2)
        email_dialog.geometry(f"500x250+{x}+{y}")

        result = {"email": None}

        # Title
        title_label = ctk.CTkLabel(
            email_dialog,
            text="Send SOW Audit Report",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)

        # Info label
        info_label = ctk.CTkLabel(
            email_dialog,
            text="Enter recipient email address to send the audit report",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(pady=(0, 20))

        # Email entry
        email_frame = ctk.CTkFrame(email_dialog)
        email_frame.pack(pady=10, padx=40, fill="x")

        email_label = ctk.CTkLabel(
            email_frame,
            text="Recipient Email:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        email_label.pack(pady=(15, 5), anchor="w", padx=15)

        email_entry = ctk.CTkEntry(
            email_frame,
            placeholder_text="e.g., vendor@example.com",
            width=400,
            height=35
        )
        email_entry.pack(pady=(0, 15), padx=15)
        email_entry.focus()

        # Buttons
        button_frame = ctk.CTkFrame(email_dialog, fg_color="transparent")
        button_frame.pack(pady=20, padx=40, fill="x")

        def on_cancel():
            result["email"] = None
            email_dialog.destroy()

        def on_send():
            email = email_entry.get().strip()
            if not email:
                messagebox.showerror("Validation Error", "Please enter an email address", parent=email_dialog)
                return
            if '@' not in email or '.' not in email.split('@')[-1]:
                messagebox.showerror("Invalid Email", "Please enter a valid email address", parent=email_dialog)
                return
            result["email"] = email
            email_dialog.destroy()

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=120,
            height=35,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)

        send_btn = ctk.CTkButton(
            button_frame,
            text="Send Email",
            command=on_send,
            width=120,
            height=35
        )
        send_btn.pack(side="right", padx=5)

        # Bind Enter key to send
        email_entry.bind('<Return>', lambda e: on_send())

        # Wait for dialog to close
        self.wait_window(email_dialog)

        # If user cancelled
        if not result["email"]:
            return

        recipient_email = result["email"]

        # Now send the email via SMTP
        try:
            self.status_label.configure(text="Generating PDF report...")
            self.update()

            pdf_path = self.report_generator.generate_report(
                self.analysis_result,
                os.path.basename(self.current_file),
                sow_content_summary=self.analysis_result.get('sow_content_summary')
            )

            self.status_label.configure(text=f"Sending email to {recipient_email}...")
            self.update()

            # Calculate compliance score
            compliance_score = self.analysis_result.get('compliance_score', 0)
            project_name = self.project_info.get('project_name', 'SOW Audit')

            # Send email with attachment
            success = self.email_notifier.send_email_with_attachment(
                recipient_email=recipient_email,
                subject=f"SOW Audit Report - {project_name} - {compliance_score}% Compliance",
                pdf_path=pdf_path,
                compliance_score=compliance_score,
                project_name=project_name,
                analysis=self.analysis_result
            )

            if success:
                self.status_label.configure(text=f"✅ Email sent successfully to {recipient_email}")
                messagebox.showinfo(
                    "Email Sent",
                    f"SOW Audit Report has been sent successfully!\n\n"
                    f"Recipient: {recipient_email}\n"
                    f"Report: {os.path.basename(pdf_path)}"
                )
            else:
                raise Exception("Email sending failed")

        except Exception as e:
            self.status_label.configure(text="❌ Email sending failed")
            messagebox.showerror(
                "Email Error",
                f"Failed to send email:\n\n{str(e)}\n\n"
                f"Please check your .env file has:\n"
                f"SMTP_SERVER=smtp.gmail.com\n"
                f"SMTP_PORT=587\n"
                f"SMTP_EMAIL=your-email@gmail.com\n"
                f"SMTP_PASSWORD=your-app-password"
            )


def main():
    """Main entry point"""
    if not CALENDAR_AVAILABLE:
        print("ERROR: tkcalendar library not installed!")
        print("Install with: pip install tkcalendar")
        input("Press Enter to exit...")
        return

    app = SOWAuditorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
