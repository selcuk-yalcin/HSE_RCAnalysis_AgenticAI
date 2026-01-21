"""
PDF Report Generator Agent
Generates HSG245-compliant investigation reports in PDF format/ format of the pdf file will be updated
We dont use any model here!!!
"""

from fpdf import FPDF
from datetime import datetime
from typing import Dict, Optional
import os
from pathlib import Path


class PDFReportAgent:
    """
    Generates professional PDF reports for incident investigations
    Following HSG245 framework structure
    """
    
    def __init__(self, output_dir: str = "outputs/reports"):
        """
        Initialize PDF Report Agent
        
        Args:
            output_dir: Directory to save generated PDF reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ PDF Report Agent initialized")
        print(f"📁 Output directory: {self.output_dir}")
    
    def generate_report(self, investigation_data: Dict) -> str:
        """
        Generate complete PDF report from investigation data
        
        Args:
            investigation_data: Complete investigation data including all parts
            
        Returns:
            Path to generated PDF file
        """
        print("\n" + "="*80)
        print("📄 GENERATING PDF REPORT")
        print("="*80)
        
        # Create PDF instance
        pdf = HSG245PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add title page
        self._add_title_page(pdf, investigation_data)
        
        # Add Part 1: Overview
        if 'part1' in investigation_data:
            self._add_part1_overview(pdf, investigation_data['part1'])
        
        # Add Part 2: Initial Assessment
        if 'part2' in investigation_data:
            self._add_part2_assessment(pdf, investigation_data['part2'])
        
        # Add Part 3: Investigation
        if 'part3' in investigation_data:
            self._add_part3_investigation(pdf, investigation_data['part3'])
        
        # Add Part 4: Action Plan
        if 'part4' in investigation_data:
            self._add_part4_action_plan(pdf, investigation_data['part4'])
        
        # Generate filename
        ref_no = investigation_data.get('part1', {}).get('ref_no', 'UNKNOWN')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"HSG245_Report_{ref_no}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Save PDF
        pdf.output(str(filepath))
        
        print(f"\n✅ PDF Report Generated Successfully")
        print(f"📄 File: {filepath}")
        print(f"📊 Pages: {pdf.page_no()}")
        
        return str(filepath)
    
    def _add_title_page(self, pdf: 'HSG245PDF', data: Dict):
        """Add title page with report header"""
        pdf.add_page()
        
        # Logo placeholder (add your company logo here)
        # pdf.image('logo.png', x=10, y=8, w=30)
        
        # Title
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 20, '', ln=True)  # Spacing
        pdf.cell(0, 15, 'HSG245 Investigation Report', ln=True, align='C')
        
        # Subtitle
        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 10, 'Root Cause Investigation', ln=True, align='C')
        
        pdf.ln(20)
        
        # Reference info
        pdf.set_font('Arial', 'B', 12)
        ref_no = data.get('part1', {}).get('ref_no', 'N/A')
        pdf.cell(0, 10, f'Reference Number: {ref_no}', ln=True, align='C')
        
        pdf.set_font('Arial', '', 11)
        date_str = datetime.now().strftime("%d %B %Y")
        pdf.cell(0, 8, f'Report Generated: {date_str}', ln=True, align='C')
        
        pdf.ln(30)
        
        # Document info box
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Document Information', ln=True)
        pdf.set_font('Arial', '', 10)
        
        info = [
            ('Status:', 'Investigation Complete'),
            ('Framework:', 'HSG245'),
            ('Version:', '1.0'),
            ('Classification:', 'Internal Use')
        ]
        
        for label, value in info:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(50, 6, label, border=0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, value, border=0, ln=True)
        
        # Footer
        pdf.set_y(-30)
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 10, 'This document contains sensitive incident information', align='C', ln=True)
        pdf.cell(0, 5, 'Handle in accordance with company confidentiality policy', align='C')
    
    def _add_part1_overview(self, pdf: 'HSG245PDF', part1_data: Dict):
        """Add Part 1: Overview section"""
        pdf.add_page()
        
        # Section header
        pdf.section_header('PART 1: OVERVIEW')
        
        # Incident details table
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Incident Details', ln=True)
        pdf.ln(2)
        
        details = [
            ('Reference Number:', part1_data.get('ref_no', 'N/A')),
            ('Reported By:', part1_data.get('reported_by', 'N/A')),
            ('Date/Time of Event:', part1_data.get('date_time', 'N/A')),
            ('Incident Type:', part1_data.get('incident_type', 'N/A')),
            ('Forwarded To:', part1_data.get('forwarded_to', 'N/A')),
        ]
        
        pdf.set_font('Arial', '', 10)
        for label, value in details:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(50, 7, label, border=1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 7, str(value), border=1, ln=True)
        
        pdf.ln(5)
        
        # Brief details
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Brief Details', ln=True)
        pdf.ln(2)
        
        brief_details = part1_data.get('brief_details', {})
        
        sections = [
            ('What happened:', brief_details.get('what', 'N/A')),
            ('Where:', brief_details.get('where', 'N/A')),
            ('When:', brief_details.get('when', 'N/A')),
            ('Who was involved:', brief_details.get('who', 'N/A')),
            ('Emergency measures taken:', brief_details.get('emergency_measures', 'N/A')),
        ]
        
        for label, text in sections:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, label, ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, str(text))
            pdf.ln(3)
    
    def _add_part2_assessment(self, pdf: 'HSG245PDF', part2_data: Dict):
        """Add Part 2: Initial Assessment section"""
        pdf.add_page()
        
        pdf.section_header('PART 2: INITIAL ASSESSMENT')
        
        # Event classification
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Event Classification', ln=True)
        pdf.ln(2)
        
        classification = [
            ('Type of Event:', part2_data.get('event_type', 'N/A')),
            ('Severity Level:', part2_data.get('severity_level', 'N/A')),
            ('Investigation Level:', part2_data.get('investigation_level', 'N/A')),
            ('RIDDOR Reportable:', part2_data.get('riddor_reportable', 'N/A')),
        ]
        
        pdf.set_font('Arial', '', 10)
        for label, value in classification:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(50, 7, label, border=1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 7, str(value), border=1, ln=True)
        
        pdf.ln(5)
        
        # Assessment details
        if 'assessment_summary' in part2_data:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'Assessment Summary', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, part2_data['assessment_summary'])
            pdf.ln(3)
        
        # Further investigation
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, 'Further Investigation Required:', border=1, ln=True)
        further_investigation = part2_data.get('further_investigation_required', 'Yes')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, str(further_investigation), border=1, ln=True)
    
    def _add_part3_investigation(self, pdf: 'HSG245PDF', part3_data: Dict):
        """Add Part 3: Investigation section"""
        pdf.add_page()
        
        pdf.section_header('PART 3: INVESTIGATION')
        
        # Root Cause Analysis
        if 'root_causes' in part3_data:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'Root Cause Analysis', ln=True)
            pdf.ln(2)
            
            root_causes = part3_data['root_causes']
            
            # Immediate causes
            if 'immediate_causes' in root_causes:
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, 'Immediate Causes:', ln=True)
                pdf.set_font('Arial', '', 10)
                for cause in root_causes['immediate_causes']:
                    pdf.cell(5, 5, chr(149), ln=0)  # Bullet point
                    pdf.multi_cell(0, 5, cause, ln=True)
                pdf.ln(2)
            
            # Underlying causes
            if 'underlying_causes' in root_causes:
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, 'Underlying Causes:', ln=True)
                pdf.set_font('Arial', '', 10)
                for cause in root_causes['underlying_causes']:
                    pdf.cell(5, 5, chr(149), ln=0)
                    pdf.multi_cell(0, 5, cause, ln=True)
                pdf.ln(2)
            
            # Root causes
            if 'root_causes' in root_causes:
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, 'Root Causes:', ln=True)
                pdf.set_font('Arial', '', 10)
                for cause in root_causes['root_causes']:
                    pdf.cell(5, 5, chr(149), ln=0)
                    pdf.multi_cell(0, 5, cause, ln=True)
                pdf.ln(2)
        
        pdf.ln(5)
        
        # Recommendations
        if 'recommendations' in part3_data:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'Recommendations', ln=True)
            pdf.ln(2)
            
            pdf.set_font('Arial', '', 10)
            for i, recommendation in enumerate(part3_data['recommendations'], 1):
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f'{i}. {recommendation.get("title", "Recommendation")}', ln=True)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 5, recommendation.get('description', ''))
                pdf.ln(2)
    
    def _add_part4_action_plan(self, pdf: 'HSG245PDF', part4_data: Dict):
        """Add Part 4: Action Plan section"""
        pdf.add_page()
        
        pdf.section_header('PART 4: RISK CONTROL ACTION PLAN')
        
        # Action items table
        if 'actions' in part4_data:
            pdf.set_font('Arial', 'B', 10)
            
            # Table header
            col_widths = [80, 40, 40]
            headers = ['Control Measure', 'Responsible Person', 'Target Date']
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 7, header, border=1, align='C')
            pdf.ln()
            
            # Table rows
            pdf.set_font('Arial', '', 9)
            for action in part4_data['actions']:
                pdf.cell(col_widths[0], 6, action.get('measure', ''), border=1)
                pdf.cell(col_widths[1], 6, action.get('responsible', ''), border=1)
                pdf.cell(col_widths[2], 6, action.get('target_date', ''), border=1)
                pdf.ln()
        
        pdf.ln(10)
        
        # Sign-off section
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Investigation Team Sign-Off', ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, 'Investigation completed by:', border=1, ln=True)
        pdf.cell(0, 10, '', border=1, ln=True)  # Signature space
        
        pdf.ln(3)
        pdf.cell(60, 7, 'Date:', border=1)
        pdf.cell(0, 7, datetime.now().strftime("%d/%m/%Y"), border=1, ln=True)


class HSG245PDF(FPDF):
    """Custom PDF class with HSG245-specific formatting"""
    
    def header(self):
        """Page header"""
        # Logo placeholder
        # self.image('logo.png', 10, 8, 25)
        
        # Company name
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Health & Safety Investigation Report', ln=True, align='R')
        
        # Line break
        self.ln(5)
    
    def footer(self):
        """Page footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
    
    def section_header(self, title: str):
        """Formatted section header"""
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(5)


# Example usage and test function
def test_pdf_generation():
    """Test PDF report generation"""
    
    # Sample investigation data
    sample_data = {
        'part1': {
            'ref_no': 'INC-20250105-001',
            'reported_by': 'John Smith',
            'date_time': '05/01/2025 10:30 AM',
            'incident_type': 'Serious injury',
            'forwarded_to': 'Safety Manager',
            'brief_details': {
                'what': 'Worker fell from ladder while painting',
                'where': 'Main warehouse, Zone A',
                'when': '05/01/2025 at approximately 10:00 AM',
                'who': 'Michael Brown (Painter)',
                'emergency_measures': 'First aid administered, ambulance called, area cordoned off'
            }
        },
        'part2': {
            'event_type': 'Accident',
            'severity_level': 'Serious',
            'investigation_level': 'High level',
            'riddor_reportable': 'Yes',
            'assessment_summary': 'Serious fall from height requiring immediate investigation.',
            'further_investigation_required': 'Yes'
        },
        'part3': {
            'root_causes': {
                'immediate_causes': [
                    'Ladder not properly secured',
                    'Worker overreached while painting'
                ],
                'underlying_causes': [
                    'Inadequate risk assessment for working at height',
                    'Lack of proper equipment (scaffolding)',
                    'Time pressure to complete job'
                ],
                'root_causes': [
                    'Insufficient management oversight of safety procedures',
                    'Inadequate training on working at height',
                    'Poor safety culture regarding equipment use'
                ]
            },
            'recommendations': [
                {
                    'title': 'Replace ladder work with scaffolding',
                    'description': 'Install mobile scaffolding for all painting work above 2 meters'
                },
                {
                    'title': 'Mandatory training',
                    'description': 'All staff to complete working at height certification before similar tasks'
                },
                {
                    'title': 'Review risk assessments',
                    'description': 'Conduct comprehensive review of all working at height risk assessments'
                }
            ]
        },
        'part4': {
            'actions': [
                {
                    'measure': 'Purchase and deploy mobile scaffolding',
                    'responsible': 'Facilities Manager',
                    'target_date': '31/01/2025'
                },
                {
                    'measure': 'Arrange working at height training for all staff',
                    'responsible': 'HR Manager',
                    'target_date': '15/02/2025'
                },
                {
                    'measure': 'Update all risk assessments',
                    'responsible': 'Safety Officer',
                    'target_date': '28/02/2025'
                }
            ]
        }
    }
    
    # Generate PDF
    agent = PDFReportAgent()
    filepath = agent.generate_report(sample_data)
    print(f"\n✅ Test PDF generated: {filepath}")


if __name__ == "__main__":
    test_pdf_generation()
