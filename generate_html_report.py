"""
HTML RAPOR OLUŞTURUCU - MPT RAMAK KALA ANALIZI
==============================================

JSON sonuçlarından modern HTML rapor oluştur
"""

import json
from pathlib import Path
from datetime import datetime


def create_html_report(json_file_path, output_path):
    """JSON analiz dosyasından HTML rapor oluştur."""
    
    # JSON'u oku
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Yeni format (part1, part2, etc.) veya eski format (overview, assessment, etc.)
    overview = data.get('part1', data.get('overview', {}))
    assessment = data.get('part2', data.get('assessment', {}))
    rca = data.get('part3_rca', data.get('root_cause_analysis', {}))
    actions = data.get('part4_actions', data.get('action_plan', {}))
    
    # HTML template oluştur
    incident_ref = (data.get('incident_ref') or 
                   rca.get('incident_ref') or 
                   overview.get('ref_no') or 
                   'N/A')
    
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HSE RCA Raporu - {incident_ref}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header h2 {{
            font-size: 1.3em;
            font-weight: 300;
            opacity: 0.9;
        }}
        
        .meta-info {{
            background: #f8f9fa;
            padding: 20px 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
        }}
        
        .meta-item strong {{
            color: #667eea;
            margin-right: 10px;
            min-width: 120px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 25px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .section h3 {{
            color: #764ba2;
            font-size: 1.3em;
            margin: 20px 0 10px 0;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin: 5px;
        }}
        
        .badge-critical {{
            background: #ff4444;
            color: white;
        }}
        
        .badge-high {{
            background: #ff8800;
            color: white;
        }}
        
        .badge-medium {{
            background: #ffbb33;
            color: white;
        }}
        
        .badge-info {{
            background: #33b5e5;
            color: white;
        }}
        
        ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        ul li {{
            padding: 10px 15px;
            margin: 8px 0;
            background: white;
            border-left: 3px solid #667eea;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .why-chain {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        
        .why-chain p {{
            margin: 8px 0;
            padding: 5px 10px;
        }}
        
        .why-chain strong {{
            color: #d32f2f;
        }}
        
        .action-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .action-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        
        .action-card h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .action-meta {{
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }}
        
        .root-cause-box {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            border: 2px solid #667eea;
        }}
        
        .root-cause-box h4 {{
            color: #667eea;
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .meta-root {{
            background: linear-gradient(135deg, #ff6b6b15 0%, #ee5a6f15 100%);
            border: 3px solid #ff6b6b;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .meta-root h3 {{
            color: #d32f2f;
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        
        .success-criteria {{
            background: #e8f5e9;
            padding: 15px;
            border-left: 4px solid #4caf50;
            border-radius: 4px;
            margin: 10px 0;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            border-top: 2px solid #667eea;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>🛡️ HSE ROOT CAUSE ANALYSIS RAPORU</h1>
            <h2>MPT Test Sahası - Sarmal Kapı Düşen Parça Ramak Kala Olayı</h2>
        </div>
        
        <!-- META INFO -->
        <div class="meta-info">
            <div class="meta-item">
                <strong>📋 Referans No:</strong>
                <span>{incident_ref}</span>
            </div>
            <div class="meta-item">
                <strong>📅 Rapor Tarihi:</strong>
                <span>{datetime.now().strftime('%d.%m.%Y %H:%M')}</span>
            </div>
            <div class="meta-item">
                <strong>🔬 Analiz Yöntemi:</strong>
                <span>5-Why Root Cause Analysis</span>
            </div>
            <div class="meta-item">
                <strong>🏢 Olay Yeri:</strong>
                <span>{overview.get('location', 'MPT Test Sahası')}</span>
            </div>
            <div class="meta-item">
                <strong>⏰ Olay Tarihi:</strong>
                <span>{overview.get('date_time', overview.get('date', '20.01.2026 09:10'))}</span>
            </div>
            <div class="meta-item">
                <strong>⚠️ Ciddiyet:</strong>
                <span class="badge badge-critical">{overview.get('severity_level', assessment.get('investigation_level', 'N/A'))}</span>
            </div>
        </div>
        
        <!-- CONTENT -->
        <div class="content">
            
            <!-- 1. OLAY ÖZETI -->
            <div class="section">
                <h2>1️⃣ OLAY ÖZETI</h2>
                
                <p><strong>Olay Tipi:</strong> <span class="badge badge-critical">{overview.get('incident_type', 'N/A')}</span></p>
                
                <h3>Potansiyel Zararlar:</h3>
                <ul>
"""
    
    potential_harm = overview.get('potential_harm', [])
    if not potential_harm and 'potential_harm' in assessment:
        potential_harm = [assessment.get('potential_harm', 'N/A')]
    
    for harm in potential_harm:
        html += f"                    <li>⚠️ {harm}</li>\n"
    
    description = (overview.get('description') or 
                  rca.get('incident_summary') or 
                  overview.get('summary', 'N/A'))
    
    html += f"""                </ul>
                
                <h3>Olay Açıklaması:</h3>
                <p style="background: white; padding: 15px; border-radius: 6px; margin-top: 10px;">
                    {description}
                </p>
            </div>
            
            <!-- 2. RİSK DEĞERLENDİRMESİ -->
            <div class="section">
                <h2>2️⃣ RİSK DEĞERLENDİRMESİ</h2>
                
                <p><strong>Değerlendirme:</strong> {assessment.get('assessment_result', 'N/A')}</p>
                <p><strong>RIDDOR Rapor Edilebilir:</strong> <span class="badge badge-info">{assessment.get('riddor_reportable', 'Hayır')}</span></p>
                <p><strong>Araştırma Seviyesi:</strong> <span class="badge badge-high">{assessment.get('investigation_level', 'N/A')}</span></p>
                
                <h3>Potansiyel Sonuçlar:</h3>
                <ul>
"""
    
    potential_consequences = assessment.get('potential_consequences', [])
    if not potential_consequences:
        potential_consequences = [assessment.get('assessment_result', 'N/A')]
    
    for consequence in potential_consequences:
        html += f"                    <li>🚨 {consequence}</li>\n"
    
    html += f"""                </ul>
                
                <h3>Ramak Kala Analizi:</h3>
                <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 4px; margin-top: 10px;">
                    <strong>⚠️ Şans Faktörü:</strong><br>
                    {assessment.get('near_miss_analysis', 'N/A')}
                </div>
            </div>
            
            <!-- 3. KÖK NEDEN ANALİZİ -->
            <div class="section">
                <h2>3️⃣ KÖK NEDEN ANALİZİ (5-WHY)</h2>
"""
    
    # Meta Root Cause
    meta = rca.get('meta_root_cause', {})
    if meta:
        html += f"""
                <div class="meta-root">
                    <h3>🔗 META KÖK NEDEN (Ortak Payda)</h3>
                    <h4>[{meta.get('code', '?')}] {meta.get('name', 'N/A')}</h4>
                    <p>{meta.get('description', 'N/A')}</p>
                </div>
"""
    
    # Kök Nedenler
    html += """
                <h3>📌 Tespit Edilen Kök Nedenler:</h3>
"""
    
    for i, rc in enumerate(rca.get('final_root_causes', []), 1):
        html += f"""
                <div class="root-cause-box">
                    <h4>{i}. [{rc.get('code', '?')}] {rc.get('name', 'N/A')}</h4>
                    <p>{rc.get('description', 'N/A')}</p>
                </div>
"""
    
    # Analiz Dalları
    html += """
                <h3>🔀 Analiz Dalları (5-WHY Zinciri):</h3>
"""
    
    for i, branch in enumerate(rca.get('analysis_branches', []), 1):
        direct = branch.get('direct_cause', {})
        root = branch.get('root_cause', {})
        
        html += f"""
                <div class="why-chain">
                    <p><strong>DAL {i}:</strong></p>
                    <p><strong>Doğrudan Neden:</strong> {direct.get('name', 'N/A')}</p>
                    <p><strong>Kök Neden:</strong> {root.get('name', 'N/A')}</p>
                    <p style="margin-top: 15px;"><strong>5-WHY Zinciri:</strong></p>
"""
        
        for why in branch.get('five_why_chain', []):
            html += f"""
                    <p style="margin-left: 20px;">
                        <strong>WHY:</strong> {why.get('why', 'N/A')}<br>
                        <span style="margin-left: 20px;">→ BECAUSE: {why.get('because', 'N/A')}</span>
                    </p>
"""
        
        html += """
                </div>
"""
    
    html += """
            </div>
            
            <!-- 4. DÜZELTICI TEDİRLER -->
            <div class="section">
                <h2>4️⃣ DÜZELTICI VE ÖNLEYICI TEDİRLER</h2>
                
                <h3>🔴 Acil Tedbirler (KRITIK):</h3>
                <div class="action-grid">
"""
    
    immediate_actions = actions.get('immediate_actions', [])
    if not immediate_actions:
        immediate_actions = []
    
    for action in immediate_actions:
        priority = action.get('priority', 'YÜKSEK')
        if priority == 'KRITIK' or priority == 'CRITICAL':
            priority_class = 'critical'
        elif priority == 'YÜKSEK' or priority == 'HIGH':
            priority_class = 'high'
        else:
            priority_class = 'medium'
            
        html += f"""
                    <div class="action-card">
                        <h4>• {action.get('description', action.get('action', 'N/A'))}</h4>
                        <div class="action-meta">
                            <span class="badge badge-{priority_class}">{priority}</span>
                            <p>👤 Owner: {action.get('responsible', action.get('owner', 'N/A'))}</p>
                            <p>⏰ Deadline: {action.get('deadline', action.get('target_date', 'N/A'))}</p>
                        </div>
                    </div>
"""
    
    html += """
                </div>
                
                <h3>🟢 Kısa ve Uzun Vadeli Önleyici Tedbirler:</h3>
                <ul>
"""
    
    # Kısa ve uzun vadeli tedbirleri birleştir
    all_measures = []
    all_measures.extend(actions.get('short_term_actions', []))
    all_measures.extend(actions.get('long_term_actions', []))
    all_measures.extend(actions.get('preventive_measures', []))
    
    for i, measure in enumerate(all_measures, 1):
        desc = measure.get('description', measure.get('action', 'N/A'))
        owner = measure.get('responsible', measure.get('owner', 'N/A'))
        timeline = measure.get('timeline', measure.get('target_date', 'N/A'))
        
        html += f"""
                    <li>
                        <strong>{i}. {desc}</strong>
                        <div class="action-meta">
                            👤 Owner: {owner} | 
                            ⏰ Timeline: {timeline}
                        </div>
                    </li>
"""
    
    html += """
                </ul>
            </div>
            
            <!-- 5. BAŞARI KRİTERLERİ -->
            <div class="section">
                <h2>5️⃣ BAŞARI KRİTERLERİ VE İZLEME</h2>
                
                <div class="success-criteria">
                    <h3>✅ Başarı Kriterleri:</h3>
                    <ul>
"""
    
    success_criteria = actions.get('success_criteria', [])
    if not success_criteria:
        success_criteria = [
            "Tüm acil tedbirler tamamlandı",
            "Kısa vadeli tedbirler devam ediyor",
            "Benzer olaylar yaşanmadı (6 ay)"
        ]
    
    for criterion in success_criteria:
        html += f"                        <li>✓ {criterion}</li>\n"
    
    html += """                    </ul>
                </div>
            </div>
            
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p><strong>HSE Root Cause Analysis System</strong></p>
            <p>Rapor Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Bu rapor otomatik olarak HSE RCA sistemleri tarafından oluşturulmuştur.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # HTML kaydet
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    import glob
    
    # En son JSON dosyasını bul
    json_pattern = "outputs/mpt_falling_part_near_miss/full_pipeline_*.json"
    json_files = sorted(glob.glob(json_pattern), reverse=True)
    
    if not json_files:
        # Fallback - eski dosya
        json_file = "outputs/mpt_falling_part_near_miss/full_analysis_20260417_185804.json"
    else:
        json_file = json_files[0]  # En son dosya
    
    output_file = json_file.replace('.json', '.html')
    
    if not Path(json_file).exists():
        print(f"❌ JSON dosyası bulunamadı: {json_file}")
        sys.exit(1)
    
    print("🤖 HTML Rapor Oluşturuluyor...")
    print(f"   📄 Giriş: {json_file}")
    
    try:
        result = create_html_report(json_file, output_file)
        
        file_size = Path(result).stat().st_size
        
        print(f"\n✅ HTML RAPOR BAŞARIYLA OLUŞTURULDU!")
        print(f"   📄 Çıkış: {result}")
        print(f"   📊 Dosya Boyutu: {file_size:,} bytes")
        print(f"\n   Raporun Özellikleri:")
        print(f"      • Modern responsive design")
        print(f"      • Gradient renkler ve card layout")
        print(f"      • 5 ana bölüm")
        print(f"      • Print-friendly CSS")
        print(f"      • Türkçe karakter desteği")
        print(f"\n   Tarayıcıda açmak için:")
        print(f"      open {result}")
        print(f"      # veya")
        print(f"      chrome {result}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
