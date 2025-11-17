#!/usr/bin/env python
"""
Script para buscar ofertas de trabajo en las 19 plataformas disponibles.

Uso:
    python scripts/search_all_platforms.py
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.scrapers.scraper_factory import ScraperFactory
from src.services.data_storage import DataStorage
from src.services.data_analyzer import DataAnalyzer
from src.services.data_visualizer import DataVisualizer
from src.services.report_generator import ReportGenerator
from src.utils.config_loader import ConfigLoader
from loguru import logger


def main():
    """Ejecuta scraping en todas las plataformas disponibles."""

    logger.info("\n" + "="*80)
    logger.info("🌐 JOB SCRAPER - BÚSQUEDA EN 19 PLATAFORMAS")
    logger.info("="*80 + "\n")

    # Configuración
    config = ConfigLoader()

    # Lista de todas las plataformas
    # ✅ = Completamente funcional
    # ⚠️  = Requiere completar selectores CSS
    all_platforms = [
        'indeed',       # ✅ Completamente funcional
        'infojobs',     # ✅ Completamente funcional
        'linkedin',     # ✅ Funcional (ofertas públicas)
        'monster',      # ✅ Funcional
        'glassdoor',    # ⚠️  Requiere selectores
        'upwork',       # ⚠️  Requiere login
        'freelancer',   # ⚠️  Requiere selectores
        'workana',      # ⚠️  Requiere selectores
        'malt',         # ⚠️  Requiere selectores
        'fiverr',       # ⚠️  Requiere selectores
        'simplyhired',  # ⚠️  Requiere selectores
        'ziprecruiter', # ⚠️  Requiere selectores
        'careerbuilder',# ⚠️  Requiere selectores
        'randstad',     # ⚠️  Requiere selectores
        'italenters',   # ⚠️  Requiere selectores
        'michaelpage',  # ⚠️  Requiere selectores
        'tecnoempleo',  # ⚠️  Requiere selectores
        'hays',         # ⚠️  Requiere selectores
        'infoempleo',   # ⚠️  Requiere selectores
    ]

    # Plataformas recomendadas (las que funcionan mejor)
    recommended_platforms = [
        'indeed',
        'infojobs',
        'monster',
        # 'linkedin',  # Descomentar si quieres usar LinkedIn
    ]

    # OPCIÓN 1: Usar solo plataformas recomendadas (más rápido y confiable)
    platforms_to_use = recommended_platforms

    # OPCIÓN 2: Usar todas las plataformas (puede tardar más tiempo)
    # platforms_to_use = all_platforms

    logger.info(f"🎯 Plataformas seleccionadas: {len(platforms_to_use)}")
    logger.info(f"   {', '.join(platforms_to_use)}\n")

    # Palabras clave a buscar
    keywords = config.get('search_terms.keywords', ['data scientist', 'machine learning'])
    location = config.get('search_terms.locations', ['España'])[0]

    logger.info(f"🔍 Palabras clave: {', '.join(keywords)}")
    logger.info(f"📍 Ubicación: {location}\n")

    # Recopilar ofertas de todas las plataformas
    all_jobs = []
    successful_platforms = []
    failed_platforms = []

    for idx, platform_name in enumerate(platforms_to_use, 1):
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"[{idx}/{len(platforms_to_use)}] 🔍 Buscando en {platform_name.upper()}...")
            logger.info(f"{'='*80}")

            scraper = ScraperFactory.create_scraper(platform_name, config)

            if scraper:
                # Configurar límite de ofertas
                scraper.max_jobs = config.get('scraping.max_jobs_per_platform', 50)

                jobs = scraper.scrape_jobs(keywords=keywords, location=location)

                if jobs:
                    all_jobs.extend(jobs)
                    successful_platforms.append(platform_name)
                    logger.info(f"✅ {platform_name}: {len(jobs)} ofertas recopiladas")
                else:
                    logger.warning(f"⚠️  {platform_name}: 0 ofertas encontradas")
                    failed_platforms.append(f"{platform_name} (0 ofertas)")

            else:
                logger.warning(f"⚠️  {platform_name}: Scraper no disponible")
                failed_platforms.append(f"{platform_name} (no disponible)")

        except Exception as e:
            logger.error(f"❌ Error en {platform_name}: {e}")
            failed_platforms.append(f"{platform_name} (error)")
            continue

    # Resumen de scraping
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 RESUMEN DE SCRAPING")
    logger.info(f"{'='*80}")
    logger.info(f"✅ Plataformas exitosas: {len(successful_platforms)}")
    logger.info(f"   {', '.join(successful_platforms) if successful_platforms else 'Ninguna'}")
    logger.info(f"\n❌ Plataformas fallidas: {len(failed_platforms)}")
    if failed_platforms:
        for platform in failed_platforms:
            logger.info(f"   - {platform}")
    logger.info(f"\n📦 Total ofertas recopiladas: {len(all_jobs)}")
    logger.info(f"{'='*80}\n")

    if not all_jobs:
        logger.error("❌ No se recopilaron ofertas. Verifica:")
        logger.error("   1. Que Chrome esté instalado: python scripts/check_chrome.py")
        logger.error("   2. Que las dependencias estén instaladas")
        logger.error("   3. Los logs en data/job_scraper.log")
        return 1

    # Guardar datos
    logger.info("💾 Guardando datos...")
    storage = DataStorage(config)
    storage.save_jobs(all_jobs)
    logger.info(f"✅ Datos guardados en: {storage.data_dir}/raw/")

    # Analizar datos
    logger.info("\n📊 Analizando datos...")
    analyzer = DataAnalyzer(config)
    analysis = analyzer.analyze(all_jobs)

    # Mostrar resumen de tecnologías
    if 'technologies' in analysis and analysis['technologies']['total_mentions'] > 0:
        logger.info(f"\n🔧 TECNOLOGÍAS MÁS DEMANDADAS:")
        top_techs = analysis['technologies'].get('top_20', {})
        for idx, (tech, count) in enumerate(list(top_techs.items())[:10], 1):
            logger.info(f"   {idx}. {tech}: {count} menciones")
    else:
        logger.warning("\n⚠️  No se encontraron tecnologías en las ofertas")
        logger.warning("   Verifica que las descripciones se están extrayendo correctamente")

    # Generar visualizaciones
    logger.info("\n📈 Generando visualizaciones...")
    visualizer = DataVisualizer(config)
    try:
        visualizer.create_all_visualizations(all_jobs, analysis)
        logger.info(f"✅ Visualizaciones guardadas en: {storage.data_dir}/visualizations/")
    except Exception as e:
        logger.error(f"❌ Error generando visualizaciones: {e}")

    # Generar informe
    logger.info("\n📄 Generando informe HTML...")
    reporter = ReportGenerator(config)
    try:
        report_path = reporter.generate_report(all_jobs, analysis)
        logger.info(f"✅ Informe generado: {report_path}")
    except Exception as e:
        logger.error(f"❌ Error generando informe: {e}")
        report_path = None

    # Resumen final
    logger.info(f"\n{'='*80}")
    logger.info(f"✅ PROCESO COMPLETADO")
    logger.info(f"{'='*80}")
    logger.info(f"📦 Ofertas totales: {len(all_jobs)}")
    logger.info(f"🏢 Empresas únicas: {analysis.get('companies', {}).get('total_unique', 0)}")
    logger.info(f"📍 Ubicaciones: {analysis.get('locations', {}).get('total_unique', 0)}")
    logger.info(f"🔧 Tecnologías encontradas: {analysis.get('technologies', {}).get('total_unique', 0)}")

    if report_path:
        logger.info(f"\n📄 Ver informe completo en:")
        logger.info(f"   {report_path}")
        logger.info(f"\n💡 Abre en tu navegador:")
        logger.info(f"   firefox {report_path}")
        logger.info(f"   # o")
        logger.info(f"   xdg-open {report_path}")

    logger.info(f"\n{'='*80}")
    logger.info("🎉 ¡Scraping completado exitosamente!")
    logger.info(f"{'='*80}\n")

    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ Error fatal: {e}")
        sys.exit(1)
