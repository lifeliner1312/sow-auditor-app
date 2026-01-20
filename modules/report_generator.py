"""
Enhanced PDF Report Generator - COMPREHENSIVE FIX
✅ Fixes empty "Key Finding" column
✅ Ensures proper text wrapping in all tables
✅ Handles multiple field name variations from LLM
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import os
import json

class ReportGenerator:
    """Generate comprehensive PDF audit reports with proper text wrapping"""

    def __init__(self, output_path="audit_report.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.page_width, self.page_height = letter
        self.margin = 0.5 * inch

    def _create_custom_styles(self):
        """Create custom paragraph styles for the report"""

        # Main title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=28,
                textColor=HexColor('#667eea'),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))

        # Section title
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=HexColor('#667eea'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ))

        # Subsection title
        if 'SubsectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SubsectionTitle',
                parent=self.styles['Heading3'],
                fontSize=13,
                textColor=HexColor('#333333'),
                spaceAfter=8,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            ))

        # Evidence text
        if 'EvidenceText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='EvidenceText',
                fontSize=10,
                textColor=HexColor('#444444'),
                leftIndent=20,
                rightIndent=20,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            ))

        # Recommendation text
        if 'RecommendationText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='RecommendationText',
                fontSize=10,
                textColor=HexColor('#1e3a5f'),
                leftIndent=20,
                rightIndent=20,
                spaceAfter=6,
                fontName='Helvetica-Bold',
                alignment=TA_JUSTIFY,
                backColor=HexColor('#e3f2fd')
            ))

        # Custom body text
        if 'SOWBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SOWBodyText',
                fontSize=10,
                textColor=HexColor('#333333'),
                alignment=TA_JUSTIFY,
                spaceAfter=8,
                leading=14
            ))

        # Bullet point style
        if 'BulletPoint' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BulletPoint',
                fontSize=10,
                textColor=HexColor('#333333'),
                leftIndent=25,
                spaceAfter=6,
                leading=14
            ))

        # Highlighted text (for important info in summary)
        if 'HighlightText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='HighlightText',
                fontSize=10,
                textColor=HexColor('#1f4788'),
                fontName='Helvetica-Bold',
                alignment=TA_JUSTIFY,
                spaceAfter=8,
                leading=14,
                backColor=HexColor('#fff9c4')
            ))

        # ✨ Table cell text with wrapping
        if 'TableCellText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableCellText',
                fontSize=9,
                textColor=HexColor('#333333'),
                alignment=TA_LEFT,
                spaceAfter=4,
                leading=12,
                wordWrap='CJK'
            ))

        # ✨ Table cell text for labels (bold)
        if 'TableCellLabel' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableCellLabel',
                fontSize=9,
                textColor=HexColor('#333333'),
                fontName='Helvetica-Bold',
                alignment=TA_LEFT,
                spaceAfter=4,
                leading=12
            ))

        # Table header style
        if 'TableHeaderText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableHeaderText',
                fontSize=10,
                textColor=HexColor('#FFFFFF'),
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=4
            ))

    def _extract_key_finding(self, pillar):
        """
        ✨ NEW METHOD: Extract key finding from pillar data
        Handles multiple possible field names from LLM response

        Args:
            pillar: Pillar dictionary from LLM analysis

        Returns:
            str: Key finding text or 'No information provided'
        """
        # Try multiple field names in order of preference
        field_names = [
            'key_finding',
            'details',
            'finding',
            'summary',
            'description',
            'evidence',
            'analysis',
            'compliance_note',
            'observation'
        ]

        for field_name in field_names:
            value = pillar.get(field_name, '').strip()
            if value:
                return value

        # If no field found, create a summary from available data
        status = pillar.get('status', 'Unknown')
        risk = pillar.get('risk_level', pillar.get('risklevel', 'Unknown'))

        if status == 'Not Met':
            return f"This pillar does not meet compliance requirements. Risk Level: {risk}. Immediate action required."
        elif status == 'Partial':
            return f"Partial compliance detected. Risk Level: {risk}. Review and remediation needed."
        elif status == 'Met':
            return f"Compliance requirements fully met. Risk Level: {risk}."
        else:
            return "No detailed information provided."

    def generate_report(self, analysis, sow_filename, document_metadata=None, sow_content_summary=None):
        """
        Main method called by app.py - generates PDF report

        Args:
            analysis: Complete audit analysis dict with pillars
            sow_filename: Name of the SOW file
            document_metadata: Optional document metadata
            sow_content_summary: Optional SOW content summary from LLM

        Returns:
            str: Path to generated PDF file
        """
        try:
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = 'reports'
            os.makedirs(output_dir, exist_ok=True)

            # Clean filename
            safe_filename = "".join(c for c in sow_filename if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_filename:
                safe_filename = "SOW_Document"

            output_path = os.path.join(output_dir, f"SOW_Audit_{safe_filename}_{timestamp}.pdf")

            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )

            # Build story (content elements)
            story = []

            # Add cover page
            story.extend(self._create_cover_page(sow_filename, analysis))
            story.append(PageBreak())

            # Add executive summary
            story.extend(self._create_executive_summary(analysis, document_metadata))
            story.append(PageBreak())

            # ✨ FIXED: Add pillar summary table with proper key findings
            story.extend(self._create_pillar_summary_table(analysis))
            story.append(PageBreak())

            # Add detailed pillar analysis
            story.extend(self._create_detailed_analysis(analysis))
            story.append(PageBreak())

            # Add schedule compliance section if available
            if analysis.get('schedule_compliance') or analysis.get('schedule_analysis'):
                story.extend(self._create_schedule_compliance_section(analysis))
                story.append(PageBreak())

            # Add risk matrix
            story.extend(self._create_risk_analysis(analysis))
            story.append(PageBreak())

            # Add recommendations
            story.extend(self._create_recommendations_section(analysis))

            # Add SOW Content Summary at the END if provided
            if sow_content_summary:
                story.append(PageBreak())
                story.extend(self._create_sow_content_summary_section(sow_content_summary))

            # Build PDF
            doc.build(story, onFirstPage=self._add_page_header, onLaterPages=self._add_page_header)

            return output_path

        except Exception as e:
            raise Exception(f"Failed to generate PDF: {str(e)}")

    def _create_pillar_summary_table(self, analysis):
        """
        ✨✨✨ FIXED: Create pillar summary table with POPULATED key findings and text wrapping ✨✨✨
        """
        elements = []

        elements.append(Paragraph("COMPLIANCE PILLAR SUMMARY", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        # Build table header
        table_data = [[
            Paragraph("<b>#</b>", self.styles['TableHeaderText']),
            Paragraph("<b>Pillar</b>", self.styles['TableHeaderText']),
            Paragraph("<b>Status</b>", self.styles['TableHeaderText']),
            Paragraph("<b>Risk</b>", self.styles['TableHeaderText']),
            Paragraph("<b>Key Finding</b>", self.styles['TableHeaderText'])
        ]]

        # Add pillar rows with properly extracted key findings
        for idx, pillar in enumerate(analysis.get('pillars', []), 1):
            # Row number
            row_num = Paragraph(str(idx), self.styles['TableCellText'])

            # Pillar name
            pillar_name = Paragraph(
                pillar.get('name', 'Unknown'),
                self.styles['TableCellText']
            )

            # Status
            status = Paragraph(
                pillar.get('status', 'Unknown'),
                self.styles['TableCellText']
            )

            # Risk level
            risk = Paragraph(
                pillar.get('risk_level', pillar.get('risklevel', 'Low')),
                self.styles['TableCellText']
            )

            # ✨ KEY FINDING - Extract using smart method
            finding_text = self._extract_key_finding(pillar)

            # Truncate if too long but keep meaningful length
            if len(finding_text) > 200:
                finding_text = finding_text[:197] + '...'

            finding_para = Paragraph(finding_text, self.styles['TableCellText'])

            table_data.append([row_num, pillar_name, status, risk, finding_para])

        # Create table with proper column widths for wrapping
        table_widths = [0.4*inch, 1.4*inch, 0.9*inch, 0.9*inch, 2.6*inch]
        table = Table(table_data, colWidths=table_widths, repeatRows=1)

        # Apply comprehensive styling
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),

            # Body row styling
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#000000')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),

            # Alignment
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # # column
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Pillar column
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),  # Status & Risk columns
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),    # Key Finding column
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),   # ✨ TOP alignment for wrapping

            # Padding for readability
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 1), (-1, -1), 8),
            ('RIGHTPADDING', (0, 1), (-1, -1), 8),

            # Grid and borders
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
            ('LINEABOVE', (0, 0), (-1, 0), 2, HexColor('#1f4788')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, HexColor('#1f4788')),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f9f9f9'), HexColor('#ffffff')])
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_sow_content_summary_section(self, summary):
        """
        ✨ FIXED: Create SOW Content Summary section with proper text wrapping
        """
        elements = []

        # Section title
        elements.append(Paragraph("SOW CONTENT SUMMARY", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        # Overview
        if summary.get('overview'):
            elements.append(Paragraph("<b>Document Overview</b>", self.styles['SubsectionTitle']))
            overview_text = summary['overview']
            paragraphs = overview_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['SOWBodyText']))
            elements.append(Spacer(1, 0.15*inch))

        # ✨ Parties Involved with proper text wrapping
        if summary.get('parties_involved'):
            elements.append(Paragraph("<b>Parties Involved</b>", self.styles['SubsectionTitle']))
            parties = summary['parties_involved']

            # Create table data with Paragraph objects for wrapping
            parties_data = [
                [
                    Paragraph("<b>Vendor:</b>", self.styles['TableCellLabel']),
                    Paragraph(parties.get('vendor_name', 'Not specified'), self.styles['TableCellText'])
                ],
                [
                    Paragraph("<b>Client:</b>", self.styles['TableCellLabel']),
                    Paragraph(parties.get('client_name', 'Not specified'), self.styles['TableCellText'])
                ],
                [
                    Paragraph("<b>Vendor Role:</b>", self.styles['TableCellLabel']),
                    Paragraph(parties.get('vendor_role', 'Not specified'), self.styles['TableCellText'])
                ],
                [
                    Paragraph("<b>Client Role:</b>", self.styles['TableCellLabel']),
                    Paragraph(parties.get('client_role', 'Not specified'), self.styles['TableCellText'])
                ]
            ]

            # Create table with proper column widths
            parties_table = Table(parties_data, colWidths=[1.4*inch, 4.8*inch])
            parties_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc'))
            ]))
            elements.append(parties_table)
            elements.append(Spacer(1, 0.15*inch))

        # Scope Highlights
        if summary.get('scope_highlights'):
            elements.append(Paragraph("<b>Scope Highlights</b>", self.styles['SubsectionTitle']))
            for highlight in summary['scope_highlights']:
                elements.append(Paragraph(f"• {highlight}", self.styles['BulletPoint']))
            elements.append(Spacer(1, 0.15*inch))

        # Key Deliverables
        if summary.get('deliverables'):
            elements.append(Paragraph("<b>Key Deliverables</b>", self.styles['SubsectionTitle']))
            for deliverable in summary['deliverables']:
                elements.append(Paragraph(f"• {deliverable}", self.styles['BulletPoint']))
            elements.append(Spacer(1, 0.15*inch))

        # Timeline Overview
        if summary.get('timeline_overview'):
            elements.append(Paragraph("<b>Project Timeline</b>", self.styles['SubsectionTitle']))
            elements.append(Paragraph(summary['timeline_overview'], self.styles['SOWBodyText']))
            elements.append(Spacer(1, 0.15*inch))

        # Cost Structure
        if summary.get('cost_structure'):
            elements.append(Paragraph("<b>Cost Structure</b>", self.styles['SubsectionTitle']))
            elements.append(Paragraph(summary['cost_structure'], self.styles['HighlightText']))
            elements.append(Spacer(1, 0.15*inch))

        # Technology Stack
        if summary.get('technology_stack'):
            elements.append(Paragraph("<b>Technology Stack</b>", self.styles['SubsectionTitle']))
            tech_items = ", ".join(summary['technology_stack'])
            elements.append(Paragraph(tech_items, self.styles['SOWBodyText']))
            elements.append(Spacer(1, 0.15*inch))

        # Key Sections
        if summary.get('key_sections'):
            elements.append(Paragraph("<b>Document Structure</b>", self.styles['SubsectionTitle']))
            for section in summary['key_sections']:
                elements.append(Paragraph(f"• {section}", self.styles['BulletPoint']))
            elements.append(Spacer(1, 0.15*inch))

        # Special Terms
        if summary.get('special_terms'):
            elements.append(Paragraph("<b>Special Terms & Conditions</b>", self.styles['SubsectionTitle']))
            for term in summary['special_terms']:
                elements.append(Paragraph(f"⚠ {term}", self.styles['HighlightText']))
            elements.append(Spacer(1, 0.15*inch))

        # Assumptions & Constraints
        if summary.get('assumptions_constraints'):
            elements.append(Paragraph("<b>Key Assumptions & Constraints</b>", self.styles['SubsectionTitle']))
            for item in summary['assumptions_constraints']:
                elements.append(Paragraph(f"• {item}", self.styles['BulletPoint']))
            elements.append(Spacer(1, 0.15*inch))

        return elements

    def _create_cover_page(self, sow_filename, analysis):
        """Create professional cover page"""
        elements = []

        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("SOW AUDIT REPORT", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(sow_filename, self.styles['Heading2']))
        elements.append(Spacer(1, 0.4*inch))

        total = len(analysis.get('pillars', []))
        met = sum(1 for p in analysis['pillars'] if p.get('status') == 'Met')
        score = round((met / total) * 100, 1) if total > 0 else 0

        score_text = f"{score}% Overall Compliance Score"
        elements.append(Paragraph(score_text, self.styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))

        date_text = f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}"
        elements.append(Paragraph(date_text, self.styles['Normal']))
        elements.append(Spacer(1, 1*inch))

        summary_data = [
            ['Total Pillars', f"{total}"],
            ['Met Requirements', f"{met}"],
            ['Partial Compliance', f"{sum(1 for p in analysis['pillars'] if p.get('status') == 'Partial')}"],
            ['Not Met', f"{sum(1 for p in analysis['pillars'] if p.get('status') == 'Not Met')}"],
            ['Critical Issues', f"{sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'Critical')}"],
            ['High Risk Issues', f"{sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'High')}"]
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))

        elements.append(summary_table)

        return elements

    def _create_executive_summary(self, analysis, document_metadata):
        """Create executive summary section"""
        elements = []

        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        total = len(analysis.get('pillars', []))
        met = sum(1 for p in analysis['pillars'] if p.get('status') == 'Met')
        partial = sum(1 for p in analysis['pillars'] if p.get('status') == 'Partial')
        not_met = sum(1 for p in analysis['pillars'] if p.get('status') == 'Not Met')
        critical = sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'Critical')
        high = sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'High')
        score = round((met / total) * 100, 1) if total > 0 else 0

        overview = f"""
This comprehensive SOW (Statement of Work) audit report evaluates compliance against nine mandatory
divestment pillars. The analysis resulted in an overall compliance score of {score}%, with {met}
pillars fully compliant and {not_met} areas requiring remediation.

Key Findings:
• {met} of {total} pillars meet all requirements
• {partial} pillars show partial compliance
• {not_met} pillars require immediate remediation
• {critical} critical issues identified
• {high} high-risk items requiring action
"""

        if document_metadata:
            overview += f"""
Document Analysis:
• File: {document_metadata.get('filename', 'Unknown')}
• Format: {document_metadata.get('format', 'Unknown')}
• Size: {document_metadata.get('size_mb', 0)} MB
• Pages: {document_metadata.get('page_count', 'Unknown')}
"""

        elements.append(Paragraph(overview, self.styles['SOWBodyText']))
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_detailed_analysis(self, analysis):
        """Create detailed pillar analysis section with proper key findings"""
        elements = []

        elements.append(Paragraph("DETAILED PILLAR ANALYSIS", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        for idx, pillar in enumerate(analysis.get('pillars', []), 1):
            elements.append(Paragraph(
                f"{idx}. {pillar.get('name', 'Unknown Pillar')}",
                self.styles['SubsectionTitle']
            ))

            status = pillar.get('status', 'Unknown')
            risk = pillar.get('risk_level', pillar.get('risklevel', 'Low'))
            elements.append(Paragraph(
                f"Status: {status} | Risk Level: {risk}",
                self.styles['SOWBodyText']
            ))

            # ✨ Use smart extraction for key finding
            key_finding = self._extract_key_finding(pillar)
            if key_finding:
                elements.append(Paragraph("Key Finding:", self.styles['SOWBodyText']))
                elements.append(Paragraph(key_finding, self.styles['EvidenceText']))

            if pillar.get('evidence'):
                elements.append(Paragraph("Evidence:", self.styles['SOWBodyText']))
                elements.append(Paragraph(pillar.get('evidence', ''), self.styles['EvidenceText']))

            recommendations = pillar.get('recommendation', pillar.get('recommendations', []))
            if recommendations:
                elements.append(Paragraph("Recommendation:", self.styles['SOWBodyText']))
                if isinstance(recommendations, list):
                    for rec in recommendations:
                        elements.append(Paragraph(f"• {rec}", self.styles['RecommendationText']))
                else:
                    elements.append(Paragraph(recommendations, self.styles['RecommendationText']))

            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_schedule_compliance_section(self, analysis):
        """Create schedule compliance section"""
        elements = []

        elements.append(Paragraph("SCHEDULE COMPLIANCE ANALYSIS", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        schedule_data = analysis.get('schedule_compliance', analysis.get('schedule_analysis', {}))
        if schedule_data:
            for key, value in schedule_data.items():
                elements.append(Paragraph(
                    f"{key.replace('_', ' ').title()}: {value}",
                    self.styles['SOWBodyText']
                ))

        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_risk_analysis(self, analysis):
        """Create risk analysis section"""
        elements = []

        elements.append(Paragraph("RISK ANALYSIS MATRIX", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        risk_data = [[
            Paragraph("<b>Risk Level</b>", self.styles['TableHeaderText']),
            Paragraph("<b>Count</b>", self.styles['TableHeaderText']),
            Paragraph("<b>Percentage</b>", self.styles['TableHeaderText'])
        ]]

        total = len(analysis.get('pillars', []))
        if total > 0:
            critical_count = sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'Critical')
            high_count = sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'High')
            medium_count = sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'Medium')
            low_count = sum(1 for p in analysis['pillars'] if p.get('risk_level', p.get('risklevel')) == 'Low')

            risk_data.extend([
                ["Critical", f"{critical_count}", f"{round(critical_count/total*100,1)}%"],
                ["High", f"{high_count}", f"{round(high_count/total*100,1)}%"],
                ["Medium", f"{medium_count}", f"{round(medium_count/total*100,1)}%"],
                ["Low", f"{low_count}", f"{round(low_count/total*100,1)}%"]
            ])

        risk_table = Table(risk_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f9f9f9'), HexColor('#ffffff')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))

        elements.append(risk_table)
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_recommendations_section(self, analysis):
        """Create recommendations section"""
        elements = []

        elements.append(Paragraph("ACTION ITEMS & RECOMMENDATIONS", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.1*inch))

        non_compliant_pillars = [p for p in analysis.get('pillars', []) if p.get('status') != 'Met']

        if not non_compliant_pillars:
            elements.append(Paragraph(
                "All pillars meet compliance requirements. No action items required.",
                self.styles['SOWBodyText']
            ))
        else:
            for idx, pillar in enumerate(non_compliant_pillars, 1):
                risk = pillar.get('risk_level', pillar.get('risklevel', 'Unknown'))
                elements.append(Paragraph(
                    f"{idx}. {pillar.get('name', 'Unknown')} [{risk} Risk]",
                    self.styles['SubsectionTitle']
                ))

                recommendations = pillar.get('recommendation', pillar.get('recommendations', []))
                if isinstance(recommendations, list):
                    for rec in recommendations:
                        elements.append(Paragraph(f"• {rec}", self.styles['RecommendationText']))
                else:
                    elements.append(Paragraph(
                        recommendations or 'No recommendation provided.',
                        self.styles['RecommendationText']
                    ))

                elements.append(Spacer(1, 0.15*inch))

        return elements

    def _add_page_header(self, canvas, doc):
        """Add header to each page"""
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(self.margin, self.page_height - 0.3*inch, "SOW AUDIT REPORT - CONFIDENTIAL")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            self.page_width - self.margin,
            self.page_height - 0.3*inch,
            f"Page {doc.page}"
        )
        canvas.restoreState()

    def generate_json_report(self, analysis, metadata, project_info):
        """Generate JSON report for data integration"""
        report = {
            "audit_date": datetime.now().isoformat(),
            "document_metadata": metadata,
            "project_info": project_info,
            "analysis": analysis
        }

        json_path = self.output_path.replace('.pdf', '.json')
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            return json_path
        except Exception as e:
            raise Exception(f"JSON generation failed: {str(e)}")
