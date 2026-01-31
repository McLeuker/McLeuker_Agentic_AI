"""
McLeuker Agentic AI Platform - Professional PDF Generator

Creates professional, well-formatted PDF documents with proper styling,
headers, footers, and structure like Manus AI.
"""

import os
import io
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem, HRFlowable
)
from reportlab.pdfgen import canvas

from src.config.settings import get_settings


@dataclass
class PDFSection:
    """A section in the PDF document."""
    title: str
    content: str
    level: int = 1  # 1 = main heading, 2 = subheading, etc.
    bullet_points: Optional[List[str]] = None
    table_data: Optional[List[List[str]]] = None


@dataclass
class GeneratedPDFFile:
    """Result of PDF generation."""
    filename: str
    filepath: str
    size_bytes: int
    page_count: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "filepath": self.filepath,
            "size_bytes": self.size_bytes,
            "page_count": self.page_count,
            "created_at": self.created_at.isoformat()
        }


class ProfessionalPDFGenerator:
    """
    Professional PDF document generator.
    
    Creates well-formatted PDF documents with:
    - Professional styling and colors
    - Headers and footers
    - Tables and lists
    - Proper typography
    """
    
    # Professional color scheme
    COLORS = {
        "primary": colors.HexColor("#1F4E79"),
        "secondary": colors.HexColor("#2E75B6"),
        "accent": colors.HexColor("#5B9BD5"),
        "text": colors.HexColor("#333333"),
        "light_gray": colors.HexColor("#F5F5F5"),
        "border": colors.HexColor("#CCCCCC"),
    }
    
    def __init__(self, output_dir: Optional[str] = None):
        self.settings = get_settings()
        self.output_dir = output_dir or self.settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up styles
        self._setup_styles()
    
    def _setup_styles(self):
        """Set up document styles."""
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='DocTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS["primary"],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 1 style
        self.styles.add(ParagraphStyle(
            name='Heading1Custom',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.COLORS["primary"],
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 2 style
        self.styles.add(ParagraphStyle(
            name='Heading2Custom',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.COLORS["secondary"],
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyCustom',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COLORS["text"],
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletCustom',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COLORS["text"],
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3
        ))
    
    async def generate(
        self,
        title: str,
        sections: List[PDFSection],
        filename: Optional[str] = None,
        author: str = "McLeuker AI",
        subtitle: Optional[str] = None
    ) -> GeneratedPDFFile:
        """
        Generate a professional PDF document.
        
        Args:
            title: Document title
            sections: List of document sections
            filename: Optional filename
            author: Document author
            subtitle: Optional subtitle
            
        Returns:
            GeneratedPDFFile with file details
        """
        # Generate filename
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() else "_" for c in title[:30])
            filename = f"{safe_title}_{timestamp}.pdf"
        
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(title, self.styles['DocTitle']))
        
        # Subtitle
        if subtitle:
            story.append(Paragraph(subtitle, self.styles['BodyCustom']))
        
        # Date and author
        date_str = datetime.utcnow().strftime("%B %d, %Y")
        story.append(Paragraph(
            f"<i>Generated by {author} on {date_str}</i>",
            self.styles['BodyCustom']
        ))
        
        story.append(Spacer(1, 20))
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.COLORS["border"],
            spaceBefore=10,
            spaceAfter=20
        ))
        
        # Add sections
        for section in sections:
            story.extend(self._build_section(section))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        # Get file info
        size_bytes = os.path.getsize(filepath)
        
        # Count pages (approximate)
        page_count = max(1, len(sections) // 3 + 1)
        
        return GeneratedPDFFile(
            filename=filename,
            filepath=filepath,
            size_bytes=size_bytes,
            page_count=page_count
        )
    
    def _build_section(self, section: PDFSection) -> List:
        """Build a section's content."""
        elements = []
        
        # Section title
        if section.level == 1:
            style = self.styles['Heading1Custom']
        else:
            style = self.styles['Heading2Custom']
        
        elements.append(Paragraph(section.title, style))
        
        # Section content
        if section.content:
            # Split content into paragraphs
            paragraphs = section.content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['BodyCustom']))
        
        # Bullet points
        if section.bullet_points:
            bullet_items = []
            for point in section.bullet_points:
                bullet_items.append(
                    ListItem(
                        Paragraph(point, self.styles['BulletCustom']),
                        leftIndent=20,
                        bulletColor=self.COLORS["primary"]
                    )
                )
            
            elements.append(ListFlowable(
                bullet_items,
                bulletType='bullet',
                start='•'
            ))
        
        # Table
        if section.table_data:
            elements.append(self._build_table(section.table_data))
        
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_table(self, data: List[List[str]]) -> Table:
        """Build a styled table."""
        if not data:
            return Table([[""]])
        
        table = Table(data)
        
        # Table style
        style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["primary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["border"]),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS["light_gray"]]),
        ])
        
        table.setStyle(style)
        return table
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(self.COLORS["text"])
        
        # Page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(
            doc.pagesize[0] - 72,
            40,
            f"Page {page_num}"
        )
        
        # Footer text
        canvas.drawString(
            72,
            40,
            "Generated by McLeuker AI"
        )
        
        # Footer line
        canvas.setStrokeColor(self.COLORS["border"])
        canvas.line(72, 55, doc.pagesize[0] - 72, 55)
        
        canvas.restoreState()
    
    async def generate_from_text(
        self,
        title: str,
        content: str,
        filename: Optional[str] = None
    ) -> GeneratedPDFFile:
        """
        Generate PDF from plain text content.
        
        Args:
            title: Document title
            content: Text content
            filename: Optional filename
            
        Returns:
            GeneratedPDFFile
        """
        # Parse content into sections
        sections = []
        
        # Split by double newlines or markdown-style headers
        parts = content.split('\n\n')
        
        current_section = None
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check for header markers
            if part.startswith('# '):
                if current_section:
                    sections.append(current_section)
                current_section = PDFSection(
                    title=part[2:].strip(),
                    content="",
                    level=1
                )
            elif part.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = PDFSection(
                    title=part[3:].strip(),
                    content="",
                    level=2
                )
            elif part.startswith('- ') or part.startswith('* '):
                # Bullet points
                if current_section:
                    if current_section.bullet_points is None:
                        current_section.bullet_points = []
                    current_section.bullet_points.append(part[2:].strip())
            else:
                # Regular content
                if current_section:
                    if current_section.content:
                        current_section.content += "\n\n" + part
                    else:
                        current_section.content = part
                else:
                    current_section = PDFSection(
                        title="Overview",
                        content=part,
                        level=1
                    )
        
        if current_section:
            sections.append(current_section)
        
        # If no sections were created, create a single section
        if not sections:
            sections = [PDFSection(
                title="Content",
                content=content,
                level=1
            )]
        
        return await self.generate(title, sections, filename)
    
    async def generate_report(
        self,
        title: str,
        summary: str,
        findings: List[Dict[str, Any]],
        conclusion: str,
        filename: Optional[str] = None
    ) -> GeneratedPDFFile:
        """
        Generate a structured report PDF.
        
        Args:
            title: Report title
            summary: Executive summary
            findings: List of findings with title and content
            conclusion: Conclusion text
            filename: Optional filename
            
        Returns:
            GeneratedPDFFile
        """
        sections = [
            PDFSection(
                title="Executive Summary",
                content=summary,
                level=1
            )
        ]
        
        # Add findings
        for i, finding in enumerate(findings, 1):
            sections.append(PDFSection(
                title=finding.get("title", f"Finding {i}"),
                content=finding.get("content", ""),
                level=2,
                bullet_points=finding.get("points"),
                table_data=finding.get("table")
            ))
        
        # Add conclusion
        sections.append(PDFSection(
            title="Conclusion",
            content=conclusion,
            level=1
        ))
        
        return await self.generate(title, sections, filename)


# Global generator instance
_pdf_generator: Optional[ProfessionalPDFGenerator] = None


def get_pdf_generator(output_dir: Optional[str] = None) -> ProfessionalPDFGenerator:
    """Get or create the global PDF generator."""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = ProfessionalPDFGenerator(output_dir)
    return _pdf_generator
