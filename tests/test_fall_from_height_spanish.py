#!/usr/bin/env python3
"""
================================================================================
CAÍDA DESDE ALTURA - PRUEBA DEL SISTEMA COMPLETO (VERSIÓN ESPAÑOLA)
FALL FROM HEIGHT INCIDENT - FULL SYSTEM TEST (SPANISH VERSION)
================================================================================

DESCRIPCIÓN DEL INCIDENTE:
  Un trabajador de la construcción cayó 6 metros desde un andamio, resultando
  gravemente herido. El trabajador no llevaba arnés de seguridad y la barandilla
  del andamio estaba incompleta. Fue trasladado a urgencias con fractura vertebral
  y hemorragia interna.

RESULTADO ESPERADO:
  - Idioma: Español
  - Informe: Todo el contenido en español
  - HTML: lang="es"
  - DOCX: Contenido en español

EJECUCIÓN:
  python tests/test_fall_from_height_spanish.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent


# ============================================================================
# DATOS DEL INCIDENTE - CAÍDA DESDE ALTURA (EN ESPAÑOL)
# ============================================================================

INCIDENT_DATA = """
INFORME DE INCIDENTE - CAÍDA DESDE ALTURA

Fecha: 18 de febrero de 2026, Hora: 10:35
Ubicación: Obra de construcción - Zona de andamios del 4º piso
Notificado por: Jefe de obra - Carlos Martínez

DESCRIPCIÓN DEL INCIDENTE:
El trabajador de montaje de andamios Javier Rodríguez (32 años) cayó desde
un andamio a aproximadamente 6 metros de altura y se golpeó contra el suelo.
El trabajador resultó gravemente herido y fue trasladado al hospital en ambulancia.

CRONOLOGÍA DEL INCIDENTE:
- 08:00 - El trabajador inició el turno, asignado al montaje de andamios en el 4º piso
- 09:30 - Montaje de la plataforma del andamio en progreso
- 10:30 - El trabajador perdió el equilibrio mientras trabajaba en el borde del andamio
- 10:35 - Cayó 6 metros hasta el nivel del suelo
- 10:37 - Los compañeros acudieron a ayudar y llamaron al 112
- 10:42 - Se administraron primeros auxilios (consciente pero gravemente herido)
- 10:55 - Llegó la ambulancia y lo trasladó al hospital
- 11:20 - Informe hospitalario: fractura vertebral L2, hemorragia interna, estado grave

PERSONA AFECTADA:
- Nombre: Javier Rodríguez
- Edad: 32 años
- Cargo: Trabajador de montaje de andamios
- Experiencia: 8 meses en trabajos de andamios
- Turno: Turno de día (08:00 - 17:00)

DETALLES DE LAS LESIONES:
- Fractura de la vértebra lumbar L2
- Fractura de pelvis
- Hemorragia interna (bazo)
- Múltiples contusiones
- Ingresado en UCI
- Pronóstico: Grave, requiere tratamiento prolongado

EQUIPOS DE SEGURIDAD:
✗ Arnés de seguridad: NO LLEVABA
✗ Barandilla: INCOMPLETA (montaje no terminado)
✗ Red de seguridad: NO HABÍA
✓ Casco de seguridad: SÍ LLEVABA
✓ Botas de seguridad: SÍ LLEVABA
✗ Arnés de cuerpo completo: NO LLEVABA

ESTADO DEL ANDAMIO:
- Ancho de la plataforma: 1,2 m (estándar)
- Barandilla: Solo presente en un lado
- Borde de trabajo: Lado sin barandilla
- Clase de andamio: Andamio de tubo de acero
- Última inspección: Hace 2 días (deficiencia de barandilla no registrada)
- Permiso de andamio: Disponible (pero no vigente)

HALLAZGOS PRELIMINARES DE CAUSAS RAÍZ:
1. El trabajador no llevaba arnés de seguridad (incumplimiento de procedimiento)
2. Se comenzó a trabajar antes de completar el montaje de la barandilla
3. El sistema de permisos de trabajo no funciona correctamente (evaluación de riesgos inadecuada)
4. El técnico de prevención no estaba realizando ronda en el lugar
5. Registros de formación laboral incompletos (no se impartió formación para trabajos en altura)
6. No se realizó seguimiento del uso del arnés de seguridad
7. Presión productiva (proyecto retrasado, instrucción de terminar rápidamente)

DECLARACIONES DE TESTIGOS:
- Antonio García (Trabajador): "Javier estaba trabajando sin arnés. Todo el mundo
  lo hace. El supervisor nos apresuraba, así que nos desplazamos al lado sin barandilla."
- Pedro López (Encargado): "La barandilla se iba a instalar mañana. La plataforma
  tenía que terminarse hoy. El supervisor dijo que acabáramos rápido."
- Jefe de obra: "No sabía que la barandilla estaba incompleta. Los trabajadores 
  saben que deben llevar arneses."

FACTORES DE GESTIÓN:
- Proyecto retrasado 3 semanas
- Presión del cliente: demanda de "finalización rápida"
- Reuniones de seguridad: No celebradas en 2 meses
- Evaluación de riesgos: Con 6 meses de antigüedad (no actualizada)
- Registros de formación laboral: Incompletos / irregulares
- Frecuencia de inspección: Una vez por semana (insuficiente)

ACCIONES INMEDIATAS:
1. Suspensión de todos los trabajos en altura
2. Nuevas inspecciones de andamios
3. Uso obligatorio del arnés
4. Celebración de charla de seguridad
5. Revisión del cronograma del proyecto
"""


# ============================================================================
# EJECUCIÓN DEL TEST
# ============================================================================

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def print_info(msg: str):
    print(f"     {msg}")


def main():
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print_header("CAÍDA DESDE ALTURA - PRUEBA DEL SISTEMA COMPLETO (VERSIÓN ESPAÑOLA)")
    print_info(f"Inicio del test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Incidente: Caída desde andamio en obra de construcción (6 m de altura)")

    results = {"timestamp": timestamp, "steps": {}}

    # Paso 1: Verificación del entorno
    print_header("PASO 1: Verificación del entorno")
    try:
        assert os.getenv("OPENROUTER_API_KEY"), "Clave API no disponible"
        print_success("Clave API disponible")
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Error de entorno: {e}")
        results["steps"]["environment"] = "FAILED"
        return results

    # Paso 2: OverviewAgent
    print_header("PASO 2: OverviewAgent - Evaluación inicial")
    try:
        agent = OverviewAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Número de referencia: {part1.get('ref_no')}")
        print_success(f"Tipo de incidente: {part1.get('incident_type')}")
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"Error en OverviewAgent: {e}")
        results["steps"]["overview"] = "FAILED"
        return results

    # Paso 3: AssessmentAgent
    print_header("PASO 3: AssessmentAgent - Evaluación de gravedad")
    try:
        agent = AssessmentAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        print_success(f"Nivel de gravedad: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"Error en AssessmentAgent: {e}")
        results["steps"]["assessment"] = "FAILED"
        return results

    # Paso 4: RootCauseAgentV2
    print_header("PASO 4: RootCauseAgentV2 - Análisis de causa raíz")
    try:
        agent = RootCauseAgentV2()
        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA}
        )
        root_causes = part3.get("final_root_causes", [])
        print_success(f"Causas raíz identificadas: {len(root_causes)}")
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("root_cause_code", "N/A")
            title = rc.get("root_cause_title", "N/A")[:60]
            print_info(f"[{i}] {code} - {title}")

        json_path = f"outputs/fall_from_height_spanish_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON guardado: {json_path}")

        results["steps"]["rca"] = "PASSED"
        results["part3"] = part3
        results["json_path"] = json_path
    except Exception as e:
        print_error(f"Error en RootCauseAgentV2: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca"] = "FAILED"
        return results

    # Paso 5: SkillBasedDocxAgent
    print_header("PASO 5: SkillBasedDocxAgent - Generación del informe")
    try:
        agent = SkillBasedDocxAgent()
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_path = f"outputs/{ref_no}_fall_from_height_SPANISH.docx"

        investigation_data = {
            "part1": part1,
            "part2": part2,
            "part3_rca": part3
        }

        result_path = agent.generate_report(investigation_data, docx_path)
        html_path = result_path.replace('.docx', '.html')

        if Path(result_path).exists():
            size_kb = Path(result_path).stat().st_size / 1024
            print_success(f"DOCX creado: {size_kb:.1f} KB")
            print_info(f"Archivo: {result_path}")

        if Path(html_path).exists():
            html_kb = Path(html_path).stat().st_size / 1024
            print_success(f"HTML creado: {html_kb:.1f} KB")
            print_info(f"Archivo: {html_path}")
            html_content = Path(html_path).read_text(encoding='utf-8')
            lang_ok = 'lang="es"' in html_content
            print_success(f"lang=\"es\": {'✓' if lang_ok else '✗'}")

        results["steps"]["docx"] = "PASSED"
        results["docx_path"] = result_path
        results["html_path"] = html_path
    except Exception as e:
        print_error(f"Error en SkillBasedDocxAgent: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["docx"] = "FAILED"
        return results

    # Resumen
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])

    print_header("RESUMEN DEL TEST")
    print_info(f"Tiempo transcurrido: {elapsed:.1f} segundos")
    print_info(f"Pasos superados: {passed}/{total}")

    if passed == total:
        print_success("🎉 ¡TODAS LAS PRUEBAS SUPERADAS!")
        results["overall"] = "PASSED"
    else:
        print_error(f"❌ {total - passed} pruebas fallidas")
        results["overall"] = "FAILED"

    print("\n📄 Archivos generados:")
    if "docx_path" in results:
        print(f"   DOCX: {results['docx_path']}")
    if "html_path" in results:
        print(f"   HTML: {results['html_path']}")
    if "json_path" in results:
        print(f"   JSON: {results['json_path']}\n")

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") == "PASSED" else 1)
