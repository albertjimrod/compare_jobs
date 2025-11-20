#!/usr/bin/env python3
"""
Script completo para scrapear Indeed con las 3 keywords optimizadas
y generar informes completos (HTML, CSV, JSON, visualizaciones).
"""

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    # Añadir el directorio del proyecto al path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from src.utils.config_loader import ConfigLoader
    from src.scrapers.indeed_scraper_selenium import IndeedScraperSelenium
    from src.services.data_analyzer import DataAnalyzer
    from src.services.data_visualizer import DataVisualizer
    from src.services.data_storage import DataStorage
    from src.services.report_generator import ReportGenerator
    from loguru import logger

    print("=" * 80)
    print("🚀 INDEED JOB SCRAPER - VERSIÓN COMPLETA")
    print("=" * 80)
    print()

    # Cargar configuración
    config = ConfigLoader()

    # Obtener keywords del config
    keywords = config.get('search_terms.keywords', [])
    location = config.get('search_terms.locations', ['España'])[0]

    print(f"📋 Keywords configuradas: {keywords}")
    print(f"📍 Ubicación: {location}")
    print()

    # Inicializar scraper
    logger.info("Inicializando scraper de Indeed...")
    scraper = IndeedScraperSelenium(config)

    # Scrapear ofertas con todas las keywords
    logger.info(f"Iniciando scraping con {len(keywords)} keywords...")
    all_jobs = scraper.scrape_jobs(keywords=keywords, location=location)

    print()
    print("=" * 80)
    print(f"✅ SCRAPING COMPLETADO")
    print(f"📦 Total ofertas recopiladas: {len(all_jobs)}")
    print("=" * 80)
    print()

    if not all_jobs:
        print("❌ No se encontraron ofertas. Verifica tu conexión o los selectores.")
        sys.exit(1)

    # Inicializar servicios
    storage = DataStorage(config)
    analyzer = DataAnalyzer(config)
    visualizer = DataVisualizer(config)
    reporter = ReportGenerator(config)

    # Guardar datos crudos
    logger.info("\n💾 Guardando datos...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        csv_path = storage.save_to_csv(all_jobs, f"jobs_{timestamp}.csv")
        logger.info(f"✅ CSV guardado: {csv_path}")
    except Exception as e:
        logger.error(f"❌ Error guardando CSV: {e}")

    try:
        json_path = storage.save_to_json(all_jobs, f"jobs_{timestamp}.json")
        logger.info(f"✅ JSON guardado: {json_path}")
    except Exception as e:
        logger.error(f"❌ Error guardando JSON: {e}")

    # Analizar datos
    logger.info("\n🔍 Analizando datos...")
    analysis = analyzer.analyze(all_jobs)

    print()
    print("📊 ANÁLISIS DE RESULTADOS")
    print("-" * 80)
    print(f"🔧 Tecnologías encontradas: {len(analysis.get('technologies', {}).get('counts', {}))}")
    print(f"🏢 Empresas únicas: {len(analysis.get('companies', {}).get('counts', {}))}")
    print(f"📍 Ubicaciones únicas: {len(analysis.get('locations', {}).get('counts', {}))}")

    # Mostrar top 10 tecnologías
    if analysis.get('technologies', {}).get('counts'):
        print("\n🔝 Top 10 Tecnologías:")
        top_tech = list(analysis['technologies']['counts'].items())[:10]
        for i, (tech, count) in enumerate(top_tech, 1):
            print(f"   {i}. {tech}: {count} menciones")

    # Generar visualizaciones
    logger.info("\n📈 Generando visualizaciones...")
    chart_paths = {}
    try:
        chart_paths = visualizer.create_all_visualizations(analysis, all_jobs)
        logger.info(f"✅ Visualizaciones guardadas en: {storage.data_dir}/visualizations/")
    except Exception as e:
        logger.error(f"❌ Error generando visualizaciones: {e}")

    # Generar insights
    insights = []
    if analysis.get('technologies', {}).get('counts'):
        top_tech = list(analysis['technologies']['counts'].items())[0] if analysis['technologies']['counts'] else None
        if top_tech:
            insights.append(f"La tecnología más demandada es {top_tech[0]} con {top_tech[1]} menciones")

    if len(all_jobs) > 0:
        insights.append(f"Se encontraron {len(all_jobs)} ofertas de trabajo en Indeed")

    if analysis.get('companies', {}).get('counts'):
        top_company = list(analysis['companies']['counts'].items())[0]
        insights.append(f"La empresa con más ofertas es {top_company[0]} ({top_company[1]} ofertas)")

    # Generar informe HTML
    logger.info("\n📄 Generando informe HTML...")
    try:
        report_path = reporter.generate_html_report(analysis, insights, chart_paths, all_jobs)
        logger.info(f"✅ Informe generado: {report_path}")
    except Exception as e:
        logger.error(f"❌ Error generando informe: {e}")
        report_path = None

    # Resumen final
    print()
    print("=" * 80)
    print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print()
    print("📁 Archivos generados:")
    print(f"   • CSV: data/raw/jobs_{timestamp}.csv")
    print(f"   • JSON: data/raw/jobs_{timestamp}.json")
    if report_path:
        print(f"   • Informe: {report_path}")
    print(f"   • Visualizaciones: data/visualizations/")
    print()
    print("=" * 80)
