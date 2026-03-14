import React, { useState } from 'react';
import IshikawaDiagram from './IshikawaDiagram';
import './IshikawaDiagramTest.css';

/**
 * Ishikawa Diagram Test Sayfası
 * Bağımsız test için kullanılır
 */
const IshikawaDiagramTest = () => {
  const [useRealData, setUseRealData] = useState(false);

  // Test verisi - gerçek bir kök neden analizi örneği
  const realRootCauses = [
    { category: 'MANPOWER', description: 'Emniyet kemeri takılmamış' },
    { category: 'MANPOWER', description: 'İş izni alınmadan çalışılmış' },
    { category: 'MANPOWER', description: 'Eğitim yetersizliği' },
    
    { category: 'MACHINE', description: 'Korkuluk montajı eksik' },
    { category: 'MACHINE', description: 'Güvenlik sistemleri devre dışı' },
    { category: 'MACHINE', description: 'Periyodik bakım yapılmamış' },
    
    { category: 'MATERIAL', description: 'Standart dışı malzeme kullanımı' },
    { category: 'MATERIAL', description: 'Hatalı ekipman seçimi' },
    { category: 'MATERIAL', description: 'Kalite kontrolü yapılmamış' },
    
    { category: 'METHOD', description: 'İş talimatına uyulmamış' },
    { category: 'METHOD', description: 'Risk analizi yapılmamış' },
    { category: 'METHOD', description: 'Acil durum prosedürü yok' },
    
    { category: 'MEASUREMENT', description: 'Denetim sıklığı yetersiz' },
    { category: 'MEASUREMENT', description: 'Gözlem eksikliği' },
    { category: 'MEASUREMENT', description: 'Ölçüm yapılmamış' },
    
    { category: 'ENVIRONMENT', description: 'Kötü hava koşulları' },
    { category: 'ENVIRONMENT', description: 'Yetersiz aydınlatma' },
    { category: 'ENVIRONMENT', description: 'Yüksek gürültü seviyesi' }
  ];

  return (
    <div className="ishikawa-test-page">
      <header className="test-header">
        <h1>🐟 Ishikawa (Fishbone) Diagram Test</h1>
        <p>Kök Neden Analizi Görselleştirme - 6M Metodu</p>
      </header>

      <div className="test-controls">
        <button 
          className={`control-btn ${useRealData ? '' : 'active'}`}
          onClick={() => setUseRealData(false)}
        >
          📊 Test Verisi (Varsayılan)
        </button>
        <button 
          className={`control-btn ${useRealData ? 'active' : ''}`}
          onClick={() => setUseRealData(true)}
        >
          🎯 Gerçek Veri Örneği
        </button>
      </div>

      <div className="test-info">
        <h3>ℹ️ Test Bilgileri</h3>
        <ul>
          <li><strong>Veri Kaynağı:</strong> {useRealData ? 'Gerçek kök neden analizi örneği' : 'Varsayılan test verisi'}</li>
          <li><strong>Kategori Sayısı:</strong> 6M (Manpower, Machine, Material, Method, Measurement, Environment)</li>
          <li><strong>Toplam Kök Neden:</strong> {useRealData ? realRootCauses.length : 'Varsayılan'}</li>
          <li><strong>Görselleştirme:</strong> SVG tabanlı, responsive, print-friendly</li>
        </ul>
      </div>

      <div className="diagram-wrapper">
        <IshikawaDiagram 
          rootCauses={useRealData ? realRootCauses : []}
          problemTitle="Yüksekten Düşme Kazası"
        />
      </div>

      <div className="test-features">
        <h3>✨ Özellikler</h3>
        <div className="features-grid">
          <div className="feature-card">
            <span className="feature-icon">🎨</span>
            <h4>Renkli Kodlama</h4>
            <p>Her kategori için farklı renk</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">📱</span>
            <h4>Responsive</h4>
            <p>Tüm ekran boyutlarında uyumlu</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🖨️</span>
            <h4>Print Ready</h4>
            <p>Yazdırma için optimize</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🌙</span>
            <h4>Dark Mode</h4>
            <p>Karanlık tema desteği</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">⚡</span>
            <h4>Performanslı</h4>
            <p>SVG tabanlı, hızlı render</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">♿</span>
            <h4>Accessible</h4>
            <p>Erişilebilirlik standartları</p>
          </div>
        </div>
      </div>

      <div className="test-usage">
        <h3>💡 Kullanım</h3>
        <pre className="code-block">
{`import IshikawaDiagram from './components/IshikawaDiagram';

// Rapor içinde kullanım
<IshikawaDiagram 
  rootCauses={analyzedRootCauses}
  problemTitle="İş Kazası"
/>

// Veri formatı
const rootCauses = [
  { category: 'MANPOWER', description: 'Açıklama' },
  { category: 'MACHINE', description: 'Açıklama' },
  // ...
];`}
        </pre>
      </div>
    </div>
  );
};

export default IshikawaDiagramTest;
