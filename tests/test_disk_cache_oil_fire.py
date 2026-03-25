#!/usr/bin/env python3
"""
Oil Fire Scenario - Disk Cache Test
Local cache'te kaydı kontrol et
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("🔥 OIL FIRE DISK CACHE TEST")
print("=" * 80)
print()

# Incident data
incident_data = {
    "ref_no": "OIL-2026-002-FIRE",
    "description": "Yağ tasfiye cihazı yanması - yanlış devreye alma sırası"
}

print("📊 Test Incident:")
print(f"   ref_no: {incident_data['ref_no']}")
print(f"   description: {incident_data['description'][:60]}...")
print()

# Cache key oluştur (pipeline ile aynı yöntem)
from agents.unified_analysis_pipeline import AnalysisCache

cache = AnalysisCache()

# Cache key'i hesapla
normalized = f"{incident_data['ref_no']}:{incident_data['description']}".strip().lower()
normalized = " ".join(normalized.split())
cache_key = hashlib.md5(normalized.encode()).hexdigest()

print(f"📝 Cache Key: {cache_key[:16]}...")
print()

# Cache directory kontrol et
cache_dir = Path.home() / ".hse_cache"
print(f"💾 Cache Directory: {cache_dir}")
print(f"   Exists: {cache_dir.exists()}")

if cache_dir.exists():
    # Cache dosyaları listele
    cache_files = list(cache_dir.glob("*.json"))
    print(f"   Files: {len(cache_files)} dosya")
    print()
    
    if cache_files:
        print("📋 Cache Dosyaları:")
        for f in cache_files[:10]:
            print(f"   • {f.name}")
        print()
    
    # Oil fire incident'ı ara
    cache_file = cache_dir / f"{cache_key}.json"
    
    if cache_file.exists():
        print(f"✅ CACHE HIT! Oil fire dokümanlı bulundu:")
        with open(cache_file) as f:
            data = json.load(f)
        print(f"   File: {cache_file.name}")
        print(f"   Size: {cache_file.stat().st_size} bytes")
        print(f"   Keys: {list(data.keys())}")
        if 'timestamp' in data:
            print(f"   Timestamp: {data['timestamp']}")
    else:
        print(f"❌ CACHE MISS - Oil fire dokümanlı bulunamadı:")
        print(f"   Expected: {cache_file.name}")
        print()
        print("   ℹ️  Cache belki disk'te saklanmış, fakat bu özel incident için henüz yazılmamış.")
        print("   Analiz yapılırsa cache'e yazılacak.")
else:
    print("❌ Cache directory henüz oluşturulmamış")
    print("   Analiz yapılırsa ilk kez oluşturulacak.")

print()
print("=" * 80)
print()
print("💡 SONUÇ:")
print("   • MongoDB bağlantısı şu an timeout'a giriyorsa, disk cache kullanılıyor")
print("   • Analiz yapılırsa: ~/.hse_cache/ altına JSON dosyaları yazılacak")
print("   • Production (Railway): MongoDB cache kullanılacak")
print()
