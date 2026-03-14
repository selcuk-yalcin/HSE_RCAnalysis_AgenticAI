import React from 'react';
import './IshikawaDiagram.css';

/**
 * Ishikawa (Fishbone) Diagram Component - 6M Analizi
 * Kök neden analizini görselleştirir
 */
export const IshikawaDiagram = ({ rootCauses = [], problemTitle = "İş Kazası" }) => {
  // Kök nedenleri 6M kategorilerine ayır
  const categorized = {
    manpower: rootCauses.filter(c => c.category === 'MANPOWER' || c.category === 'İnsan'),
    machine: rootCauses.filter(c => c.category === 'MACHINE' || c.category === 'Makine'),
    material: rootCauses.filter(c => c.category === 'MATERIAL' || c.category === 'Malzeme'),
    method: rootCauses.filter(c => c.category === 'METHOD' || c.category === 'Metod'),
    measurement: rootCauses.filter(c => c.category === 'MEASUREMENT' || c.category === 'Ölçüm'),
    environment: rootCauses.filter(c => c.category === 'ENVIRONMENT' || c.category === 'Çevre')
  };

  // Test verisi - eğer veri yoksa
  const hasData = rootCauses.length > 0;
  
  const testData = {
    manpower: [
      { description: 'Eğitim eksikliği' },
      { description: 'İş izni almadan çalışma' }
    ],
    machine: [
      { description: 'Bakım eksikliği' },
      { description: 'Güvenlik sistemleri devre dışı' }
    ],
    material: [
      { description: 'Hatalı malzeme kullanımı' },
      { description: 'Kalite standardı dışı' }
    ],
    method: [
      { description: 'İş talimatına uymama' },
      { description: 'Risk analizi yapılmamış' }
    ],
    measurement: [
      { description: 'Denetim eksikliği' },
      { description: 'Gözlem yetersiz' }
    ],
    environment: [
      { description: 'Kötü hava koşulları' },
      { description: 'Aydınlatma yetersiz' }
    ]
  };

  const data = hasData ? categorized : testData;

  return (
    <div className="ishikawa-container">
      <h3 className="ishikawa-title">
        Kök Neden Analizi - Ishikawa Diyagramı (6M Metodu)
      </h3>
      
      <div className="ishikawa-legend">
        <span className="legend-item">
          <span className="legend-color manpower"></span>
          Manpower (İnsan)
        </span>
        <span className="legend-item">
          <span className="legend-color machine"></span>
          Machine (Makine)
        </span>
        <span className="legend-item">
          <span className="legend-color material"></span>
          Material (Malzeme)
        </span>
        <span className="legend-item">
          <span className="legend-color method"></span>
          Method (Metod)
        </span>
        <span className="legend-item">
          <span className="legend-color measurement"></span>
          Measurement (Ölçüm)
        </span>
        <span className="legend-item">
          <span className="legend-color environment"></span>
          Environment (Çevre)
        </span>
      </div>

      <svg viewBox="0 0 1200 700" className="ishikawa-svg">
        <defs>
          {/* Arrow marker for main spine */}
          <marker id="arrowhead" markerWidth="10" markerHeight="10" 
                  refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#1e293b" />
          </marker>
          
          {/* Gradient for problem box */}
          <linearGradient id="problemGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#667eea', stopOpacity: 1 }} />
            <stop offset="100%" style={{ stopColor: '#764ba2', stopOpacity: 1 }} />
          </linearGradient>
        </defs>

        {/* Main spine (omurga) */}
        <line x1="100" y1="350" x2="950" y2="350" 
              stroke="#1e293b" strokeWidth="4" 
              markerEnd="url(#arrowhead)" />
        
        {/* Problem box (sağda) */}
        <rect x="950" y="310" width="220" height="80" 
              fill="url(#problemGradient)" rx="12" 
              filter="drop-shadow(0 4px 6px rgba(0,0,0,0.1))" />
        <text x="1060" y="355" textAnchor="middle" 
              fill="white" fontSize="20" fontWeight="bold">
          {problemTitle}
        </text>

        {/* MANPOWER (Üst-Sol) */}
        <line x1="250" y1="150" x2="350" y2="350" 
              stroke="#ef4444" strokeWidth="3" />
        <line x1="250" y1="150" x2="220" y2="120" 
              stroke="#ef4444" strokeWidth="2" />
        <text x="200" y="115" fontSize="18" fontWeight="bold" 
              fill="#ef4444">
          MANPOWER
        </text>
        <text x="205" y="135" fontSize="13" fill="#6b7280">(İnsan Faktörü)</text>
        
        {data.manpower.slice(0, 3).map((cause, idx) => (
          <g key={idx}>
            <line x1={250 + idx * 30} y1={160 + idx * 30} 
                  x2={250 + idx * 30} y2={190 + idx * 30} 
                  stroke="#ef444480" strokeWidth="1.5" />
            <text x={260 + idx * 30} y={180 + idx * 30} 
                  fontSize="11" fill="#374151">
              • {cause.description}
            </text>
          </g>
        ))}

        {/* MACHINE (Üst-Orta) */}
        <line x1="450" y1="180" x2="500" y2="350" 
              stroke="#f59e0b" strokeWidth="3" />
        <line x1="450" y1="180" x2="420" y2="150" 
              stroke="#f59e0b" strokeWidth="2" />
        <text x="400" y="145" fontSize="18" fontWeight="bold" 
              fill="#f59e0b">
          MACHINE
        </text>
        <text x="405" y="165" fontSize="13" fill="#6b7280">(Makine/Ekipman)</text>
        
        {data.machine.slice(0, 3).map((cause, idx) => (
          <g key={idx}>
            <line x1={450 + idx * 30} y1={190 + idx * 30} 
                  x2={450 + idx * 30} y2={220 + idx * 30} 
                  stroke="#f59e0b80" strokeWidth="1.5" />
            <text x={460 + idx * 30} y={210 + idx * 30} 
                  fontSize="11" fill="#374151">
              • {cause.description}
            </text>
          </g>
        ))}

        {/* MATERIAL (Üst-Sağ) */}
        <line x1="650" y1="200" x2="680" y2="350" 
              stroke="#8b5cf6" strokeWidth="3" />
        <line x1="650" y1="200" x2="620" y2="170" 
              stroke="#8b5cf6" strokeWidth="2" />
        <text x="600" y="165" fontSize="18" fontWeight="bold" 
              fill="#8b5cf6">
          MATERIAL
        </text>
        <text x="605" y="185" fontSize="13" fill="#6b7280">(Malzeme)</text>
        
        {data.material.slice(0, 3).map((cause, idx) => (
          <g key={idx}>
            <line x1={650 + idx * 30} y1={210 + idx * 30} 
                  x2={650 + idx * 30} y2={240 + idx * 30} 
                  stroke="#8b5cf680" strokeWidth="1.5" />
            <text x={660 + idx * 30} y={230 + idx * 30} 
                  fontSize="11" fill="#374151">
              • {cause.description}
            </text>
          </g>
        ))}

        {/* ENVIRONMENT (Alt-Sol) */}
        <line x1="250" y1="550" x2="350" y2="350" 
              stroke="#10b981" strokeWidth="3" />
        <line x1="250" y1="550" x2="220" y2="580" 
              stroke="#10b981" strokeWidth="2" />
        <text x="190" y="595" fontSize="18" fontWeight="bold" 
              fill="#10b981">
          ENVIRONMENT
        </text>
        <text x="195" y="615" fontSize="13" fill="#6b7280">(Çevre Koşulları)</text>
        
        {data.environment.slice(0, 3).map((cause, idx) => (
          <g key={idx}>
            <line x1={250 + idx * 30} y1={540 - idx * 30} 
                  x2={250 + idx * 30} y2={510 - idx * 30} 
                  stroke="#10b98180" strokeWidth="1.5" />
            <text x={260 + idx * 30} y={530 - idx * 30} 
                  fontSize="11" fill="#374151">
              • {cause.description}
            </text>
          </g>
        ))}

        {/* METHOD (Alt-Orta) */}
        <line x1="450" y1="520" x2="500" y2="350" 
              stroke="#3b82f6" strokeWidth="3" />
        <line x1="450" y1="520" x2="420" y2="550" 
              stroke="#3b82f6" strokeWidth="2" />
        <text x="405" y="565" fontSize="18" fontWeight="bold" 
              fill="#3b82f6">
          METHOD
        </text>
        <text x="410" y="585" fontSize="13" fill="#6b7280">(Çalışma Metodu)</text>
        
        {data.method.slice(0, 3).map((cause, idx) => (
          <g key={idx}>
            <line x1={450 + idx * 30} y1={510 - idx * 30} 
                  x2={450 + idx * 30} y2={480 - idx * 30} 
                  stroke="#3b82f680" strokeWidth="1.5" />
            <text x={460 + idx * 30} y={500 - idx * 30} 
                  fontSize="11" fill="#374151">
              • {cause.description}
            </text>
          </g>
        ))}

        {/* MEASUREMENT (Alt-Sağ) */}
        <line x1="650" y1="500" x2="680" y2="350" 
              stroke="#ec4899" strokeWidth="3" />
        <line x1="650" y1="500" x2="620" y2="530" 
              stroke="#ec4899" strokeWidth="2" />
        <text x="590" y="545" fontSize="18" fontWeight="bold" 
              fill="#ec4899">
          MEASUREMENT
        </text>
        <text x="595" y="565" fontSize="13" fill="#6b7280">(Ölçüm/Kontrol)</text>
        
        {data.measurement.slice(0, 3).map((cause, idx) => (
          <g key={idx}>
            <line x1={650 + idx * 30} y1={490 - idx * 30} 
                  x2={650 + idx * 30} y2={460 - idx * 30} 
                  stroke="#ec489980" strokeWidth="1.5" />
            <text x={660 + idx * 30} y={480 - idx * 30} 
                  fontSize="11" fill="#374151">
              • {cause.description}
            </text>
          </g>
        ))}
      </svg>

      {!hasData && (
        <div className="ishikawa-test-notice">
          <p>📊 Bu test verisidir. Gerçek kök neden verileri analiz sonucunda gösterilecektir.</p>
        </div>
      )}
    </div>
  );
};

export default IshikawaDiagram;
