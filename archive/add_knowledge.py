"""
Quick Knowledge Upload Script
Add your HSG245 text directly to RAG system
"""

from shared.rag_system import get_rag_system

#  HSG245 Root Cause Analysis Taxonomy
# Format: Her doküman için ayrı string
KNOWLEDGE_TEXTS = {
    "hsg245_immediate_causes_actions": """
A. IMMEDIATE CAUSES – ACTIONS (İLK GÖRÜNÜR NEDENLER – DAVRANIŞ)

A1. Procedure and Rule Noncompliance
A1.1 Individual rule/procedure violation
A1.2 Group/team rule violation
A1.3 Supervisory/managerial rule violation
A1.4 Deliberate deviation without authorization
A1.5 Use of incorrect or outdated procedure
A1.6 Procedure exists but not usable in field conditions
A1.7 Conflicting procedures or instructions
A1.8 Procedure requires unrealistic assumptions (time, tools, access)

A2. Improper Use of Tools, Equipment, Facilities, or Vehicles
A2.1 Incorrect or inappropriate use of equipment/facility/vehicle
A2.2 Incorrect or inappropriate use of hand tools
A2.3 Use of equipment/vehicle with known defect
A2.4 Use of tools with known defect
A2.5 Incorrect placement or storage of tools, equipment, or materials
A2.6 Use beyond design limits or operating envelope
A2.7 Temporary modification or makeshift use of equipment

A3. Failure in Use of Protective Equipment or Methods
A3.1 Failure to recognize need for PPE/protective methods
A3.2 Failure to use required PPE/protective methods
A3.3 Incorrect use of PPE/protective methods
A3.4 PPE/protective methods unavailable or unsuitable
A3.5 Removal, bypass, or deactivation of safety/protective devices
A3.6 PPE/protection interferes with task performance
A3.7 PPE selection not matched to hazard severity

A4. Human Error, Attention, and Behavioral Lapses
A4.1 Distraction or divided attention
A4.2 Failure to recognize environmental hazards
A4.3 Inappropriate or unsafe workplace behavior
A4.4 Failure to warn others
A4.5 Unintentional human error (slip/lapse)
A4.6 Automatic/routine actions performed without conscious control
A4.7 Task complexity exceeds human capability without aids
A4.8 Time pressure leading to cognitive shortcut
    """,
    
    "hsg245_immediate_causes_conditions": """
B. IMMEDIATE CAUSES – CONDITIONS

B1. Protective and Warning System Failures
B1.1 Protective devices ineffective
B1.2 Protective devices faulty
B1.3 Faulty personal protective equipment
B1.4 Warning/alarm systems ineffective
B1.5 Warning/alarm systems faulty or unavailable
B1.6 Protective systems overridden without management control

B2. Equipment, Tool, and Vehicle Condition or Preparation
B2.1 Equipment/facility failure
B2.2 Inadequate equipment/facility preparation
B2.3 Tool failure
B2.4 Inadequate tool preparation
B2.5 Vehicle failure
B2.6 Inadequate vehicle preparation
B2.7 Latent defect not detectable by operator

B3. Hazardous Energy or Substance Exposure
B3.1 Fire or explosion
B3.2 Electrical energy (energized systems)
B3.3 Non-electrical energy (pressure, mechanical, hydraulic, gravity)
B3.4 Hazardous chemicals or toxic substances
B3.5 Combustible dust / dust explosion
B3.6 Oxygen-deficient atmosphere (N₂, inerting)
B3.7 Radiation (ionizing / non-ionizing)
B3.8 Extreme temperature (heat/cold)
B3.9 Noise or vibration
B3.10 Natural events (storm, earthquake, flooding)
B3.11 Stored energy not identified or released unexpectedly

B4. Work Area Layout and Environmental Conditions
B4.1 Congested or poorly arranged layout
B4.2 Inadequate lighting
B4.3 Inadequate ventilation
B4.4 Unprotected height or fall hazard
B4.5 Equipment located in inappropriate position
B4.6 Poor housekeeping/order/cleanliness
B4.7 Poor or illegible labeling/signage
B4.8 Inappropriate environmental conditions (temperature, humidity, microclimate)
B4.9 Work area design increases error likelihood
    """,
    
    "hsg245_systemic_causes_personal": """
C. SYSTEMIC CAUSES – PERSONAL FACTORS

C1. Physical Capacity and Health
C1.1 Sensory impairments (vision, hearing, perception)
C1.2 Physical limitations (strength, reach, anthropometry)
C1.3 Medical conditions or illness
C1.4 Fatigue (acute or chronic)
C1.5 Effects of drugs, alcohol, or medication

C2. Cognitive and Mental Capability
C2.1 Memory or attention limitations
C2.2 Poor coordination or reaction time
C2.3 Poor mechanical or system comprehension
C2.4 Inadequate judgment or decision-making ability
C2.5 Emotional state affecting performance (stress, fear, anxiety)
C2.6 Lack of task-specific mental models

C3. Skill, Competence, and Behavioral Conditioning
C3.1 Inadequate skill assessment
C3.2 Inadequate skill application
C3.3 Lack of coaching or feedback
C3.4 Skill rarely practiced or maintained
C3.5 Unsafe behavior reinforced or uncorrected
C3.6 Correct behavior not positively reinforced
    """,
    
    "hsg245_systemic_causes_organizational": """
D. SYSTEMIC CAUSES – WORK & ORGANIZATIONAL FACTORS

D1. Leadership, Supervision, and Safety Culture
D1.1 Weak leadership commitment to safety
D1.2 Inadequate supervision or oversight
D1.3 Lack of accountability
D1.4 Production pressure over safety
D1.5 Normalization of deviation
D1.6 Ineffective Stop-Work authority
D1.7 Weak reporting and learning culture
D1.8 Insufficient visible field leadership
D1.9 Management tolerance of known deviations

D2. Communication and Information Management
D2.1 Ineffective communication (verbal/written/digital)
D2.2 Misunderstanding or ambiguity of instructions
D2.3 Lack of standard terminology
D2.4 Poor quality of communication infrastructure
D2.5 Inadequate incident reporting and follow-up
D2.6 Inadequate shift handover of critical information
D2.7 Information overload or poor prioritization

D3. Training, Competence, and Workforce Management
D3.1 Training not provided or inadequate
D3.2 Training needs not identified
D3.3 Inadequate practical/OJT training
D3.4 Competence not verified
D3.5 Inadequate staffing or workload planning
D3.6 Training effectiveness not evaluated

D4. Risk, Change, and Work Control Systems
D4.1 Risk analysis not performed or inadequate (PHA/JSA/HAZOP)
D4.2 Failure to implement or follow up risk controls
D4.3 Change management (MOC) ineffective or bypassed
D4.4 Permit-to-work system ineffective
D4.5 Energy isolation (LOTO/SIMOPS) ineffective
D4.6 Temporary risk controls treated as permanent

D5. Engineering, Design, and Technical Systems
D5.1 Design input/output errors or nonconformance
D5.2 Inadequate design review, PSSR, or ORR
D5.3 Poor HMI/ergonomics/alarm management
D5.4 Inadequate hazardous area classification or Ex compliance
D5.5 Inadequate integration of risk studies into design (failure to incorporate HAZID/HAZOP/LOPA outputs into the design)
D5.6 Design did not consider human error tolerance

D6. Maintenance, Asset Integrity, and Reliability
D6.1 Inadequate maintenance strategy or planning
D6.2 Inadequate execution or workmanship
D6.3 Inadequate inspection, testing, or calibration
D6.4 Inadequate documentation, records, or CMMS data
D6.5 Failure to learn from recurring failures
D6.6 Deferred maintenance accepted as normal

D7. Contractor and Supply Chain Management
D7.1 Inadequate contractor pre-qualification
D7.2 Inadequate contractor supervision
D7.3 Contractor competence not verified
D7.4 Weak contractor safety culture integration
D7.5 Defective materials, components, or equipment supplied
D7.6 Contractor incentives misaligned with safety

D8. Emergency Preparedness and External Factors
D8.1 Emergency plans or drills inadequate
D8.2 Emergency equipment unavailable or ineffective
D8.3 Poor coordination with external agencies
D8.4 External events beyond organizational control
D8.5 Emergency response roles unclear or conflicting
    """,
}

def main():
    print("=" * 60)
    print("HSG245 Knowledge Upload")
    print("=" * 60)
    
    # Initialize RAG system
    rag = get_rag_system()
    
    # Show current stats
    print("\n Current Knowledge Base:")
    stats = rag.stats()
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Sources: {stats['source_count']}")
    
    # Upload each document
    print("\n Uploading documents...")
    total_chunks = 0
    
    for source_name, text in KNOWLEDGE_TEXTS.items():
        if "[BURAYA" in text or len(text.strip()) < 50:
            print(f"     Skipping {source_name} (placeholder text)")
            continue
        
        print(f"\n    Processing: {source_name}")
        chunks = rag.add_text(text, source=source_name)
        total_chunks += chunks
    
    # Show final stats
    print("\n" + "=" * 60)
    print("Upload Complete!")
    print("=" * 60)
    
    final_stats = rag.stats()
    print(f"\n📊 Final Knowledge Base Stats:")
    print(f"   Total chunks: {final_stats['total_chunks']}")
    print(f"   Sources: {final_stats['source_count']}")
    for source in final_stats['sources']:
        print(f"   - {source}")
    
    # Test query
    print("\n Testing query: 'accident investigation'")
    results = rag.query("accident investigation", n_results=2)
    
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i} [Similarity: {result['similarity']:.2%}]:")
        print(f"   {result['text'][:150]}...")

if __name__ == "__main__":
    main()
