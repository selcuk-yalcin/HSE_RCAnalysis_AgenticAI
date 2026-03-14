"""
MongoDB Cache Key Generator - Kritik Alanlara Göre Optimized
================================================================

Cache key'leri sadece kritik alanlara dayandırarak:
1. Lightweight ve efficient cache keys
2. Daha yüksek cache hit rates
3. Farklı descriptions aynı core data = aynı cache
4. Production'da daha az API call, daha az maliyet

Kritik Alanlar:
- Incident Type (accident, near-miss, etc.)
- Equipment/Machinery
- Injury Type (cut, burn, fracture, etc.)
- Activity/Operation
- Root Category (NOT description)
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class CacheKeyManager:
    """MongoDB cache key'lerini generate ve manage eder"""
    
    # Entity tiplerine göre kritik alanlar
    CRITICAL_FIELDS = {
        "incident": [
            "incident_type",      # accident, near-miss, unsafe condition
            "equipment",          # forklift, mixer, pump, etc.
            "injury_type",        # cut, burn, fracture, none, etc.
            "activity",           # loading, maintenance, operation
            "hazard_category",    # mechanical, chemical, thermal, etc.
        ],
        "causes": [
            "code",               # A1.1, B2.3, etc.
            "cause_type",         # immediate_cause, root_cause
            "category",           # human factors, technical, organizational
        ],
        "taxonomy": [
            "code",               # taxonomy code
            "category",           # main category
            "severity_level",     # critical, high, medium, low
        ],
        "analysis": [
            "incident_type",
            "equipment",
            "analysis_version",   # v1, v2, v3 for consistency
        ]
    }
    
    # Field normalization mappings
    FIELD_ALIASES = {
        "equipment_type": "equipment",
        "injury_description": "injury_type",
        "activity_type": "activity",
        "incident_category": "incident_type",
        "machine": "equipment",
        "task": "activity",
    }
    
    @staticmethod
    def normalize_field(field_name: str) -> str:
        """
        Alan adını normalize et - aliases'i çöz
        
        Örnek:
        - "equipment_type" → "equipment"
        - "machine" → "equipment"
        """
        return CacheKeyManager.FIELD_ALIASES.get(field_name, field_name)
    
    @staticmethod
    def normalize_value(value: Any) -> str:
        """
        Değeri normalize et - consistent hashing için
        
        - None/empty → ""
        - Upper/mixed case → lowercase
        - Extra whitespace → trim
        - Lists → join with comma
        """
        if value is None or value == "":
            return ""
        
        if isinstance(value, list):
            # Listeyi join et, her item'i normalize et
            return ",".join(str(v).strip().lower() for v in value if v)
        
        if isinstance(value, (int, float, bool)):
            return str(value).lower()
        
        if isinstance(value, dict):
            # Dictionary'i JSON'a çevir ve hash'le
            return json.dumps(value, sort_keys=True, default=str)
        
        # String: lowercase, trim, normalize internal whitespace
        return " ".join(str(value).strip().split()).lower()
    
    @staticmethod
    def generate_cache_key(
        entity_type: str,
        entity_data: Dict[str, Any],
        include_fields: Optional[List[str]] = None,
        version: str = "v1"
    ) -> str:
        """
        Kritik alanlara dayalı cache key oluştur
        
        Args:
            entity_type: "incident", "causes", "taxonomy", "analysis"
            entity_data: Entity verisi (dict)
            include_fields: Ek dahil edilecek custom alanlar
            version: Cache version (versioning için)
        
        Returns:
            Format: "{entity_type}:{version}:{hash16}"
            
        Örnek:
        - incident:v1:a1b2c3d4e5f6g7h8
        - causes:v1:x9y8z7w6v5u4t3s2
        """
        # Kritik alanları belirle
        critical_fields = CacheKeyManager.CRITICAL_FIELDS.get(
            entity_type,
            ["_id"]  # Fallback
        )
        
        # Custom alanlar ekle
        if include_fields:
            critical_fields = list(set(critical_fields + include_fields))
        
        # Cache data'sını oluştur (sadece kritik alanlardan)
        cache_data = {}
        
        for field in critical_fields:
            # Field alias'ı çöz
            normalized_field = CacheKeyManager.normalize_field(field)
            
            # Field'ı bul (original veya normalized name ile)
            value = entity_data.get(field) or entity_data.get(normalized_field)
            
            if value is not None:
                # Değeri normalize et
                normalized_value = CacheKeyManager.normalize_value(value)
                cache_data[normalized_field] = normalized_value
        
        # JSON'a çevir (sorted keys için consistency)
        cache_string = json.dumps(cache_data, sort_keys=True, default=str)
        
        # SHA256 ile hash et (MD5 yerine daha güvenli)
        cache_hash = hashlib.sha256(
            cache_string.encode()
        ).hexdigest()[:16]  # İlk 16 karakter
        
        # Format: entity_type:version:hash
        return f"{entity_type}:{version}:{cache_hash}"
    
    @staticmethod
    def generate_bulk_cache_keys(
        entity_type: str,
        entities: List[Dict[str, Any]],
        version: str = "v1"
    ) -> Dict[str, str]:
        """
        Toplu cache key'ler oluştur
        
        Returns:
            {entity_id: cache_key} mapping
        """
        result = {}
        
        for entity in entities:
            # Entity ID'sini belirle
            entity_id = str(entity.get("_id") or entity.get("id") or entity.get("code"))
            
            # Cache key'i oluştur
            cache_key = CacheKeyManager.generate_cache_key(
                entity_type,
                entity,
                version=version
            )
            
            result[entity_id] = cache_key
        
        return result
    
    @staticmethod
    def is_cache_key_valid(cache_key: str) -> bool:
        """
        Cache key'in format'ının doğru olup olmadığını kontrol et
        
        Format: {entity_type}:{version}:{hash16}
        """
        parts = cache_key.split(":")
        
        if len(parts) != 3:
            return False
        
        entity_type, version, hash_part = parts
        
        # Basic validation
        if not entity_type or len(entity_type) < 2:
            return False
        
        if not version.startswith("v"):
            return False
        
        if len(hash_part) != 16:
            return False
        
        return True


class CacheKeyDebugger:
    """Cache key generation debug ve comparison tools"""
    
    @staticmethod
    def debug_generate_key(entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cache key generation'ı debug et - hangi alanlar kullanıldı göster
        
        Returns:
            {
                "cache_key": "incident:v1:a1b2c3d4e5f6g7h8",
                "critical_fields": [...],
                "extracted_data": {...},
                "normalized_data": {...}
            }
        """
        critical_fields = CacheKeyManager.CRITICAL_FIELDS.get(
            entity_type,
            ["_id"]
        )
        
        # Extracted data (raw)
        extracted_data = {}
        
        # Normalized data
        normalized_data = {}
        
        for field in critical_fields:
            normalized_field = CacheKeyManager.normalize_field(field)
            raw_value = entity_data.get(field) or entity_data.get(normalized_field)
            
            if raw_value is not None:
                extracted_data[field] = raw_value
                normalized_data[normalized_field] = CacheKeyManager.normalize_value(raw_value)
        
        cache_key = CacheKeyManager.generate_cache_key(
            entity_type,
            entity_data
        )
        
        return {
            "cache_key": cache_key,
            "entity_type": entity_type,
            "critical_fields": critical_fields,
            "extracted_data": extracted_data,
            "normalized_data": normalized_data,
            "is_valid": CacheKeyManager.is_cache_key_valid(cache_key)
        }
    
    @staticmethod
    def compare_keys(
        entity_type: str,
        entity_data_1: Dict[str, Any],
        entity_data_2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        İki entity'nin cache key'lerini karşılaştır
        
        Aynı key'se → cache hit olacak
        Farklı key'se → cache miss olacak
        """
        key1 = CacheKeyManager.generate_cache_key(entity_type, entity_data_1)
        key2 = CacheKeyManager.generate_cache_key(entity_type, entity_data_2)
        
        debug1 = CacheKeyDebugger.debug_generate_key(entity_type, entity_data_1)
        debug2 = CacheKeyDebugger.debug_generate_key(entity_type, entity_data_2)
        
        return {
            "key_1": key1,
            "key_2": key2,
            "match": key1 == key2,
            "debug_1": debug1,
            "debug_2": debug2,
            "differences": {
                "field": [k for k in debug1["normalized_data"] if debug1["normalized_data"].get(k) != debug2["normalized_data"].get(k)]
            } if key1 != key2 else {}
        }


class CacheEntryMetadata:
    """MongoDB cache entry'si için metadata"""
    
    @staticmethod
    def create_metadata(
        cache_key: str,
        entity_type: str,
        entity_data: Dict[str, Any],
        analysis_result: Dict[str, Any],
        ttl_days: int = 30
    ) -> Dict[str, Any]:
        """
        MongoDB cache entry'si oluştur
        
        Returns:
            {
                "cache_key": "incident:v1:a1b2c3d4e5f6g7h8",
                "entity_type": "incident",
                "entity_id": "REF-001",
                "critical_fields": {...},
                "analysis_result": {...},
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=30),
                "metadata": {
                    "version": "v1",
                    "generated_by": "CacheKeyManager",
                    "hit_count": 0
                }
            }
        """
        expires_at = datetime.now() + timedelta(days=ttl_days)
        
        entity_id = str(entity_data.get("_id") or entity_data.get("ref_no") or entity_data.get("id"))
        
        return {
            "cache_key": cache_key,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "critical_fields": {
                field: entity_data.get(field)
                for field in CacheKeyManager.CRITICAL_FIELDS.get(entity_type, [])
                if field in entity_data
            },
            "analysis_result": analysis_result,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "metadata": {
                "version": "v1",
                "ttl_days": ttl_days,
                "generated_by": "CacheKeyManager",
                "hit_count": 0  # Track how many times this was used
            }
        }


# ============================================================================
# KULLANIM ÖRNEKLERI
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 MONGODB CACHE KEY GENERATOR - DEMO")
    print("="*80)
    
    # Örnek incident data
    incident_1 = {
        "_id": "INC-001",
        "ref_no": "OIL-2026-001",
        "incident_type": "ACCIDENT",
        "equipment": "Oil Purifier",
        "injury_type": "BURN",
        "activity": "Maintenance",
        "description": "Detailed incident description...",
        "location": "Workshop",
        "date": "2026-03-14"
    }
    
    incident_2 = {
        "_id": "INC-002",
        "ref_no": "OIL-2026-002",
        "incident_type": "Accident",  # Farklı case
        "equipment": "oil purifier",  # Farklı case
        "injury_type": "burn",        # Farklı case
        "activity": "MAINTENANCE",    # Farklı case
        "description": "Completely different description with more details...",
        "location": "Workshop Area",
        "date": "2026-03-15"
    }
    
    # 1. Cache key oluştur
    print("\n1️⃣  CACHE KEY GENERATION")
    print("-"*80)
    
    key1 = CacheKeyManager.generate_cache_key("incident", incident_1)
    key2 = CacheKeyManager.generate_cache_key("incident", incident_2)
    
    print(f"Incident 1 Cache Key: {key1}")
    print(f"Incident 2 Cache Key: {key2}")
    
    if key1 == key2:
        print("✅ SAME KEYS! → Cache hit! (description difference ignored)")
    else:
        print("❌ DIFFERENT KEYS! → Cache miss! (difference detected)")
    
    # 2. Debug mode
    print("\n2️⃣  DEBUG MODE - Hangi alanlar kullanıldı?")
    print("-"*80)
    
    debug_info = CacheKeyDebugger.debug_generate_key("incident", incident_1)
    print(json.dumps(debug_info, indent=2, default=str, ensure_ascii=False))
    
    # 3. Comparison
    print("\n3️⃣  COMPARISON MODE - İki incident'ı karşılaştır")
    print("-"*80)
    
    comparison = CacheKeyDebugger.compare_keys("incident", incident_1, incident_2)
    print(f"Match: {comparison['match']}")
    if comparison['match']:
        print("✅ Same cache key - cache hit expected!")
    else:
        print("❌ Different cache keys - differences:")
        print(json.dumps(comparison['differences'], indent=2, ensure_ascii=False))
    
    # 4. Bulk keys
    print("\n4️⃣  BULK CACHE KEY GENERATION")
    print("-"*80)
    
    incidents = [incident_1, incident_2]
    bulk_keys = CacheKeyManager.generate_bulk_cache_keys("incident", incidents)
    
    for entity_id, cache_key in bulk_keys.items():
        print(f"  {entity_id} → {cache_key}")
    
    # 5. Metadata creation
    print("\n5️⃣  CREATE CACHE METADATA (for MongoDB)")
    print("-"*80)
    
    metadata = CacheEntryMetadata.create_metadata(
        cache_key=key1,
        entity_type="incident",
        entity_data=incident_1,
        analysis_result={"root_cause": "Valve not opened", "severity": "HIGH"},
        ttl_days=30
    )
    
    print(json.dumps(metadata, indent=2, default=str, ensure_ascii=False))
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)
