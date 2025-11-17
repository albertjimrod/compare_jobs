#!/usr/bin/env python
"""
Script de inicio rápido para Job Scraper.
Ejemplo simple de uso del sistema.
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas."""
    missing = []

    try:
        import pandas
    except ImportError:
        missing.append('pandas')

    try:
        import requests
    except ImportError:
        missing.append('requests')

    try:
        import bs4
    except ImportError:
        missing.append('beautifulsoup4')

    try:
        import loguru
    except ImportError:
        missing.append('loguru')

    try:
        import yaml
    except ImportError:
        missing.append('pyyaml')

    if missing:
        print("\n" + "="*60)
        print("❌ ERROR: FALTAN DEPENDENCIAS")
        print("="*60)
        print("\nNo se pueden importar los siguientes módulos:")
        for pkg in missing:
            print(f"  - {pkg}")

        print("\n📦 Para instalar las dependencias, ejecuta uno de estos comandos:")
        print("\nOpción 1 - Con Conda (recomendado):")
        print("  conda env create -f environment.yml")
        print("  conda activate job-scraper-env")

        print("\nOpción 2 - Con pip:")
        print("  pip install -r requirements.txt")

        print("\nOpción 3 - Instalación rápida de lo mínimo:")
        print(f"  pip install {' '.join(missing)}")

        print("\n" + "="*60)
        print("Después de instalar, vuelve a ejecutar este script.")
        print("="*60 + "\n")
        sys.exit(1)


# Verificar dependencias antes de importar
check_dependencies()

from src.scrapers.scraper_factory import ScraperFactory
from src.services.data_storage import DataStorage
from src.services.data_analyzer import DataAnalyzer
from src.services.data_visualizer import DataVisualizer
from src.services.report_generator import ReportGenerator
from src.utils.config_loader import ConfigLoader
from loguru import logger


def main():
    """Ejemplo de uso básico del Job Scraper."""

    logger.info("=== JOB SCRAPER - EJEMPLO DE USO ===\n")

    # Advertencia sobre Indeed
    print("\n" + "="*70)
    print("⚠️  ADVERTENCIA: PROTECCIÓN ANTI-SCRAPING")
    print("="*70)
    print("\nIndeed tiene protección anti-scraping MUY AGRESIVA.")
    print("Es muy probable que este ejemplo falle con error 403 Forbidden.")
    print("\n📖 Para soluciones y alternativas, lee:")
    print("   → ANTI_SCRAPING_SOLUTIONS.md")
    print("\n💡 Opciones recomendadas:")
    print("   1. Usar API oficial de Indeed (https://developer.indeed.com/)")
    print("   2. Probar con plataformas menos restrictivas")
    print("   3. Implementar Selenium para navegación real")
    print("\nℹ️  Este ejemplo continúa con Indeed para demostración...")
    print("="*70 + "\n")

    # 1. Cargar configuración
    logger.info("1. Cargando configuración...")
    config = ConfigLoader()

    # 2. Crear scraper (en este ejemplo, solo Indeed)
    logger.info("2. Creando scraper de Indeed...")
    scraper = ScraperFactory.create_scraper('indeed', config)

    if not scraper:
        logger.error("No se pudo crear el scraper")
        return

    # 3. Scrapear ofertas (limitado a 10 para el ejemplo)
    logger.info("3. Buscando ofertas de 'data scientist'...")
    jobs = scraper.scrape_jobs(
        keywords=['data scientist'],
        location='España'
    )

    logger.info(f"Encontradas {len(jobs)} ofertas\n")

    if not jobs:
        logger.warning("No se encontraron ofertas")
        print("\n" + "="*70)
        print("❌ NO SE PUDIERON OBTENER OFERTAS")
        print("="*70)
        print("\nProbablemente Indeed bloqueó la petición (error 403).")
        print("\n🔧 Soluciones:")
        print("\n1. USAR OTRAS PLATAFORMAS (menos restrictivas):")
        print("   python -m src.main --platforms infojobs tecnoempleo")
        print("\n2. USAR API OFICIAL DE INDEED:")
        print("   - Registrarse en: https://developer.indeed.com/")
        print("   - Obtener API key")
        print("   - Implementar cliente API (ver docs)")
        print("\n3. USAR DATOS DE EJEMPLO (para probar el análisis):")
        print("   python -m src.main --skip-scraping --load-from data/ejemplo.csv")
        print("\n4. LEER DOCUMENTACIÓN COMPLETA:")
        print("   cat ANTI_SCRAPING_SOLUTIONS.md")
        print("\n" + "="*70 + "\n")
        return

    # Mostrar algunas ofertas
    logger.info("=== PRIMERAS 5 OFERTAS ===")
    for i, job in enumerate(jobs[:5], 1):
        logger.info(f"\n{i}. {job.title}")
        logger.info(f"   Empresa: {job.company}")
        logger.info(f"   Ubicación: {job.location}")
        logger.info(f"   URL: {job.url}")
        if job.technologies:
            logger.info(f"   Tecnologías: {', '.join(job.technologies[:5])}")

    # 4. Guardar datos
    logger.info("\n4. Guardando datos...")
    storage = DataStorage(config)
    saved_files = storage.save_jobs(jobs, prefix="ejemplo")

    logger.info("Archivos guardados:")
    for format_type, path in saved_files.items():
        logger.info(f"  - {format_type}: {path}")

    # 5. Analizar datos
    logger.info("\n5. Analizando datos...")
    analyzer = DataAnalyzer(config)
    analysis = analyzer.analyze(jobs)

    # Mostrar insights
    insights = analyzer.get_insights(analysis)
    logger.info("\n=== INSIGHTS ===")
    for insight in insights:
        logger.info(f"  {insight}")

    # 6. Generar visualizaciones
    logger.info("\n6. Generando visualizaciones...")
    visualizer = DataVisualizer(config)
    chart_paths = visualizer.create_all_visualizations(analysis, jobs)

    logger.info(f"Generados {len(chart_paths)} gráficos en:")
    for chart_name, path in chart_paths.items():
        logger.info(f"  - {chart_name}: {path}")

    # 7. Generar informe
    logger.info("\n7. Generando informe HTML...")
    reporter = ReportGenerator(config)
    report_path = reporter.generate_html_report(analysis, insights, chart_paths)

    logger.info(f"\n✅ ¡Proceso completado!")
    logger.info(f"📄 Informe disponible en: {report_path}")
    logger.info(f"\nAbre el informe en tu navegador para ver los resultados completos.")


if __name__ == '__main__':
    main()
