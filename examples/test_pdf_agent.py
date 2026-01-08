"""
Test PDF Report Agent
Generates a sample HSG245 investigation report
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.pdf_report_agent import PDFReportAgent


def main():
    """Test PDF report generation with sample data"""
    
    print("="*80)
    print("PDF REPORT AGENT - TEST SCRIPT")
    print("="*80)
    
    # Sample investigation data
    investigation_data = {
        'part1': {
            'ref_no': 'INC-20250105-A7B2',
            'reported_by': 'Sarah Johnson - Safety Officer',
            'date_time': '05/01/2025 09:45 AM',
            'incident_type': 'Serious injury',
            'forwarded_to': 'Operations Manager & HSE Director',
            'brief_details': {
                'what': 'Warehouse operative sustained laceration to hand from sharp edge on damaged pallet',
                'where': 'Distribution Center, Loading Bay 3',
                'when': '05/01/2025 at 09:30 AM during morning shift',
                'who': 'David Martinez (Warehouse Operative, 3 years experience)',
                'emergency_measures': 'Immediate first aid applied, wound cleaned and bandaged. Employee transported to local hospital for assessment. Area secured and damaged pallets removed from use.'
            }
        },
        'part2': {
            'event_type': 'Accident',
            'severity_level': 'Serious - Medical treatment required',
            'investigation_level': 'High level investigation',
            'riddor_reportable': 'Yes - Reportable injury requiring hospital treatment',
            'assessment_summary': 'Serious injury occurred due to damaged equipment. Immediate hazard identified and removed. Full investigation required to prevent recurrence. Multiple contributing factors identified requiring management attention.',
            'further_investigation_required': 'Yes - High priority'
        },
        'part3': {
            'root_causes': {
                'immediate_causes': [
                    'Sharp protruding nail on damaged wooden pallet',
                    'Employee did not notice damage before handling',
                    'Inadequate lighting in loading bay area',
                    'No gloves worn at time of incident'
                ],
                'underlying_causes': [
                    'No formal inspection process for incoming pallets',
                    'Damaged pallets not segregated upon arrival',
                    'PPE policy not consistently enforced',
                    'Maintenance backlog for bay lighting',
                    'Lack of training on identifying damaged equipment',
                    'Time pressure during peak loading periods'
                ],
                'root_causes': [
                    'Inadequate management system for equipment inspection',
                    'Insufficient safety culture regarding PPE compliance',
                    'Poor communication of maintenance issues',
                    'No risk assessment for pallet handling operations',
                    'Lack of accountability for safety procedures',
                    'Inadequate resources allocated to preventive maintenance'
                ]
            },
            'recommendations': [
                {
                    'title': 'Implement Pallet Inspection System',
                    'description': 'Establish mandatory visual inspection process for all incoming pallets. Damaged pallets to be immediately marked and segregated. Weekly inspection schedule for stored pallets.'
                },
                {
                    'title': 'Upgrade Loading Bay Lighting',
                    'description': 'Replace all lighting in Loading Bay 3 with LED high-bay lights (minimum 500 lux). Extend to all loading bays within 3 months. Include emergency backup lighting.'
                },
                {
                    'title': 'Mandatory PPE Enforcement',
                    'description': 'Issue cut-resistant gloves (EN388 Level 3+) to all warehouse staff. Implement 100% compliance checks by supervisors. Include PPE compliance in performance reviews.'
                },
                {
                    'title': 'Risk Assessment Update',
                    'description': 'Conduct comprehensive risk assessment for all manual handling operations. Include pallet handling, damaged equipment procedures, and PPE requirements.'
                },
                {
                    'title': 'Enhanced Training Program',
                    'description': 'Develop and deliver training module on equipment inspection, hazard identification, and PPE use. Mandatory for all warehouse staff with annual refresher.'
                },
                {
                    'title': 'Preventive Maintenance Schedule',
                    'description': 'Establish preventive maintenance program for facility infrastructure including lighting, flooring, and equipment. Monthly safety walk-throughs by management.'
                }
            ]
        },
        'part4': {
            'actions': [
                {
                    'measure': 'Purchase 100 pairs of cut-resistant gloves (EN388 Level 3)',
                    'responsible': 'Warehouse Manager - Mike Thompson',
                    'target_date': '12/01/2025'
                },
                {
                    'measure': 'Install inspection station for incoming pallets with clear signage',
                    'responsible': 'Facilities Supervisor - Anna Lee',
                    'target_date': '19/01/2025'
                },
                {
                    'measure': 'Replace all lighting in Loading Bay 3 (8x LED high-bay 200W)',
                    'responsible': 'Maintenance Manager - Robert Chen',
                    'target_date': '26/01/2025'
                },
                {
                    'measure': 'Conduct pallet handling risk assessment (HSE template)',
                    'responsible': 'Safety Officer - Sarah Johnson',
                    'target_date': '15/01/2025'
                },
                {
                    'measure': 'Develop and deliver PPE/equipment inspection training (2-hour module)',
                    'responsible': 'Training Coordinator - Lisa Brown',
                    'target_date': '31/01/2025'
                },
                {
                    'measure': 'Train all warehouse staff (25 people) on new procedures',
                    'responsible': 'Training Coordinator - Lisa Brown',
                    'target_date': '15/02/2025'
                },
                {
                    'measure': 'Implement daily PPE compliance checks by supervisors',
                    'responsible': 'Shift Supervisors - All',
                    'target_date': '01/02/2025'
                },
                {
                    'measure': 'Upgrade lighting in all remaining loading bays (Bays 1,2,4)',
                    'responsible': 'Maintenance Manager - Robert Chen',
                    'target_date': '31/03/2025'
                },
                {
                    'measure': 'Establish monthly management safety walk-through schedule',
                    'responsible': 'Operations Manager - James Wilson',
                    'target_date': '01/02/2025'
                },
                {
                    'measure': 'Review and update all warehouse risk assessments',
                    'responsible': 'Safety Officer - Sarah Johnson',
                    'target_date': '28/02/2025'
                }
            ]
        }
    }
    
    # Initialize PDF Report Agent
    agent = PDFReportAgent(output_dir="outputs/reports")
    
    # Generate report
    print("\n🔄 Generating comprehensive HSG245 investigation report...")
    filepath = agent.generate_report(investigation_data)
    
    print("\n" + "="*80)
    print("✅ PDF REPORT GENERATION COMPLETE")
    print("="*80)
    print(f"\n📄 Report saved to: {filepath}")
    print(f"📊 Report includes:")
    print("   • Title page with document information")
    print("   • Part 1: Overview and incident details")
    print("   • Part 2: Initial assessment and classification")
    print("   • Part 3: Root cause analysis and recommendations")
    print("   • Part 4: Risk control action plan with responsibilities")
    print("\n💡 Open the PDF to view the complete investigation report")
    

if __name__ == "__main__":
    main()
