# PDF Report Agent

Generates professional HSG245-compliant PDF investigation reports.

## Features

- ✅ HSG245 framework compliance
- ✅ Professional formatting with headers and footers
- ✅ Automatic page numbering
- ✅ Structured sections (Parts 1-4)
- ✅ Tables for action plans
- ✅ Bullet points for root causes
- ✅ Sign-off section

## Usage

```python
from agents.pdf_report_agent import PDFReportAgent

# Initialize agent
agent = PDFReportAgent(output_dir="outputs/reports")

# Prepare investigation data
investigation_data = {
    'part1': {
        'ref_no': 'INC-001',
        'reported_by': 'John Doe',
        'incident_type': 'Serious injury',
        # ... more fields
    },
    'part2': { ... },
    'part3': { ... },
    'part4': { ... }
}

# Generate PDF report
filepath = agent.generate_report(investigation_data)
print(f"Report saved to: {filepath}")
```

## Output Format

The generated PDF includes:

### Title Page
- Report header
- Reference number
- Generation date
- Document classification

### Part 1: Overview
- Incident reference details
- Reporter information
- Date/time of event
- Incident type
- Brief details (What, Where, When, Who, Emergency measures)

### Part 2: Initial Assessment
- Event classification
- Severity level
- Investigation level
- RIDDOR reportability
- Assessment summary

### Part 3: Investigation
- Root cause analysis
  - Immediate causes
  - Underlying causes
  - Root causes
- Recommendations with descriptions

### Part 4: Action Plan
- Control measures table
- Responsible persons
- Target dates
- Investigation team sign-off

## Testing

Run the test script to generate a sample report:

```bash
python examples/test_pdf_agent.py
```

This will create a complete sample report in `outputs/reports/` directory.

## Requirements

- fpdf2>=2.8.0 (included in requirements.txt)

## Customization

### Adding Company Logo

```python
# In HSG245PDF.header() method
self.image('path/to/logo.png', 10, 8, 25)
```

### Changing Colors

```python
# Modify section_header() method
self.set_fill_color(R, G, B)  # RGB values
```

### Custom Fonts

```python
# In PDF generation methods
pdf.set_font('Arial', 'B', 12)  # Font, Style, Size
```

## Integration with API

```python
# In API endpoint
from agents.pdf_report_agent import PDFReportAgent

@app.post("/api/v1/incidents/{id}/report")
async def generate_report(id: int):
    # Get investigation data from database
    investigation_data = get_investigation_data(id)
    
    # Generate PDF
    agent = PDFReportAgent()
    filepath = agent.generate_report(investigation_data)
    
    # Return file
    return FileResponse(
        filepath,
        media_type='application/pdf',
        filename=f"report_{id}.pdf"
    )
```

## Example Output

See `examples/test_pdf_agent.py` for a complete working example with realistic incident data.

The generated PDF will include:
- Professional formatting
- Clear section headers
- Structured data presentation
- Action plan with accountability
- Sign-off section

## Notes

- PDF files are saved to `outputs/reports/` by default
- Filenames include reference number and timestamp
- Page numbers are automatically added
- Headers and footers on every page
- Compliant with HSG245 structure
