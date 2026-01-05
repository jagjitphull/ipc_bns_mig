"""
PDF Generation Utilities for Legal Memorandums
Creates professional legal documents with proper formatting
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
import re


class LegalMemoPDFGenerator:
    """Generate professional legal memorandums in PDF format"""

    def __init__(self, page_size=letter):
        self.page_size = page_size
        self.styles = self._create_styles()

    def _create_styles(self):
        """Create custom styles for legal memo"""
        styles = getSampleStyleSheet()

        # Title style
        styles.add(ParagraphStyle(
            name='MemoTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e3c72'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Header style
        styles.add(ParagraphStyle(
            name='MemoHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        # Section heading
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1e3c72'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='MemoBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Footer style
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER
        ))

        return styles

    def _add_header(self, story, case_info):
        """Add memo header with case information"""
        # Letterhead/Title
        story.append(Paragraph("LEGAL MEMORANDUM", self.styles['MemoTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Header information table
        header_data = [
            ['TO:', case_info.get('to', 'Client/Court')],
            ['FROM:', case_info.get('from', 'Legal Team')],
            ['DATE:', datetime.now().strftime('%B %d, %Y')],
            ['RE:', case_info.get('subject', 'IPC to BNS Transition Analysis')],
        ]

        header_table = Table(header_data, colWidths=[1*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3c72')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))

        # Horizontal line
        line_table = Table([['']], colWidths=[6.5*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1e3c72')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.2*inch))

    def _format_text(self, text):
        """Format text for PDF (handle markdown-like formatting)"""
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

        # Convert *italic* to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)

        # Convert section numbers to bold (e.g., "Section 302" or "IPC 376")
        text = re.sub(r'(Section \d+[A-Z]?)', r'<b>\1</b>', text)
        text = re.sub(r'(IPC \d+[A-Z]?)', r'<b>\1</b>', text)
        text = re.sub(r'(BNS \d+[A-Z]?)', r'<b>\1</b>', text)

        return text

    def _add_section(self, story, heading, content):
        """Add a section with heading and content"""
        # Section heading
        story.append(Paragraph(heading, self.styles['SectionHeading']))

        # Section content
        if isinstance(content, list):
            for paragraph in content:
                formatted_text = self._format_text(paragraph)
                story.append(Paragraph(formatted_text, self.styles['MemoBody']))
        else:
            formatted_text = self._format_text(content)
            story.append(Paragraph(formatted_text, self.styles['MemoBody']))

        story.append(Spacer(1, 0.1*inch))

    def _add_sections_table(self, story, sections_data):
        """Add IPC to BNS sections comparison table"""
        if not sections_data:
            return

        story.append(Paragraph("IPC to BNS Section Mapping", self.styles['SectionHeading']))

        # Table data
        table_data = [['IPC Section', 'BNS Section', 'Changes']]

        for section in sections_data:
            table_data.append([
                f"Section {section.get('ipc_section', 'N/A')}",
                f"Section {section.get('bns_section', 'N/A')}",
                section.get('change_type', 'None')
            ])

        sections_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
        sections_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(sections_table)
        story.append(Spacer(1, 0.2*inch))

    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()

        # Page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawRightString(7.5*inch, 0.5*inch, text)

        # Disclaimer
        disclaimer = "This document is generated by IPC/BNS Legal Reasoning Agent"
        canvas.drawCentredString(4.25*inch, 0.5*inch, disclaimer)

        canvas.restoreState()

    def generate(self, memo_data, case_info=None):
        """
        Generate PDF memorandum

        Args:
            memo_data: Dict with memo content or string
            case_info: Dict with case information (to, from, subject)

        Returns:
            BytesIO object containing PDF
        """
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=1*inch,
            title="Legal Memorandum"
        )

        # Build content
        story = []

        # Default case info
        if case_info is None:
            case_info = {
                'to': 'Client',
                'from': 'Legal Counsel',
                'subject': 'IPC to BNS Transition Analysis'
            }

        # Add header
        self._add_header(story, case_info)

        # Parse memo content
        if isinstance(memo_data, str):
            # Simple string memo - parse into sections
            sections = self._parse_text_memo(memo_data)
            for section_title, section_content in sections.items():
                self._add_section(story, section_title, section_content)
        elif isinstance(memo_data, dict):
            # Structured memo data
            if 'executive_summary' in memo_data:
                self._add_section(story, 'EXECUTIVE SUMMARY', memo_data['executive_summary'])

            if 'sections' in memo_data:
                self._add_sections_table(story, memo_data['sections'])

            if 'analysis' in memo_data:
                self._add_section(story, 'LEGAL ANALYSIS', memo_data['analysis'])

            if 'relevant_cases' in memo_data:
                self._add_section(story, 'RELEVANT CASE LAW', memo_data['relevant_cases'])

            if 'recommendation' in memo_data:
                self._add_section(story, 'RECOMMENDATION', memo_data['recommendation'])

            if 'conclusion' in memo_data:
                self._add_section(story, 'CONCLUSION', memo_data['conclusion'])

        # Add disclaimer
        story.append(Spacer(1, 0.3*inch))
        disclaimer_text = (
            "<i>Disclaimer: This memorandum is generated by an AI-powered legal reasoning system. "
            "While every effort has been made to ensure accuracy, this should not be considered "
            "as legal advice. Please consult with qualified legal professionals for specific legal matters.</i>"
        )
        story.append(Paragraph(disclaimer_text, self.styles['Footer']))

        # Build PDF with footer
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        buffer.seek(0)
        return buffer

    def _parse_text_memo(self, text):
        """Parse plain text memo into sections"""
        sections = {}
        current_section = "Summary"
        current_content = []

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is a section header (ALL CAPS or ends with :)
            if line.isupper() or (line.endswith(':') and len(line.split()) <= 5):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)

                # Start new section
                current_section = line.rstrip(':')
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections


def generate_memo_pdf(memo_content, case_info=None, page_size=letter):
    """
    Convenience function to generate PDF

    Args:
        memo_content: String or dict with memo content
        case_info: Dict with case information
        page_size: Page size (letter or A4)

    Returns:
        BytesIO object containing PDF
    """
    generator = LegalMemoPDFGenerator(page_size=page_size)
    return generator.generate(memo_content, case_info)
