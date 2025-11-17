"""
Punto de entrada principal del Job Scraper.
Orquesta el proceso completo de scraping, análisis y generación de informes.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Verificar dependencias críticas antes de continuar
try:
    from loguru import logger
except ImportError:
    print("\n" + "="*60)
    print("❌ ERROR: Falta instalar 'loguru'")
    print("="*60)
    print("\nEjecuta uno de estos comandos para instalar dependencias:")
    print("  conda env create -f environment.yml  # Con Conda")
    print("  pip install -r requirements.txt      # Con pip")
    print("="*60 + "\n")
    sys.exit(1)

try:
    from .models.job_offer import JobOffer
    from .scrapers.scraper_factory import ScraperFactory
    from .services.data_storage import DataStorage
    from .services.data_analyzer import DataAnalyzer
    from .services.data_visualizer import DataVisualizer
    from .services.report_generator import ReportGenerator
    from .utils.config_loader import ConfigLoader
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.error("\nAsegúrate de haber instalado todas las dependencias:")
    logger.error("  conda env create -f environment.yml  # Con Conda")
    logger.error("  pip install -r requirements.txt      # Con pip")
    sys.exit(1)


def setup_logging(config: ConfigLoader):
    """
    Configura el sistema de logging.

    Args:
        config: Configuración del sistema
    """
    log_config = config.get_logging_config()

    # Remover configuración por defecto
    logger.remove()

    # Configurar formato
    log_format = log_config.get(
        'log_format',
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )

    # Agregar handler para consola
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_config.get('level', 'INFO'),
        colorize=True
    )

    # Agregar handler para archivo si está configurado
    if log_config.get('log_to_file', True):
        log_file = log_config.get('log_file', './data/job_scraper.log')
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_format,
            level=log_config.get('level', 'INFO'),
            rotation="10 MB",
            retention="7 days"
        )


def run_scraping(
    config: ConfigLoader,
    platforms: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    location: Optional[str] = None
) -> List[JobOffer]:
    """
    Ejecuta el proceso de scraping.

    Args:
        config: Configuración del sistema
        platforms: Lista de plataformas a scrapear (None = todas habilitadas)
        keywords: Palabras clave de búsqueda (None = usar config)
        location: Ubicación (None = usar config)

    Returns:
        Lista de ofertas recopiladas
    """
    logger.info("=== INICIANDO PROCESO DE SCRAPING ===")

    all_jobs = []

    # Crear scrapers
    if platforms:
        scrapers = {
            platform: ScraperFactory.create_scraper(platform, config)
            for platform in platforms
        }
        # Filtrar None (scrapers no disponibles)
        scrapers = {k: v for k, v in scrapers.items() if v is not None}
    else:
        scrapers = ScraperFactory.create_all_enabled_scrapers(config)

    if not scrapers:
        logger.error("No hay scrapers disponibles")
        return all_jobs

    logger.info(f"Scrapers activos: {list(scrapers.keys())}")

    # Obtener keywords y location de config si no se especifican
    if keywords is None:
        keywords = config.get('search_terms.keywords', ['data scientist'])
    if location is None:
        locations = config.get('search_terms.locations', ['España'])
        location = locations[0] if locations else None

    # Ejecutar scraping para cada plataforma
    for platform_name, scraper in scrapers.items():
        try:
            logger.info(f"\n--- Scraping {platform_name} ---")
            jobs = scraper.scrape_jobs(keywords=keywords, location=location)
            all_jobs.extend(jobs)
            logger.info(f"Recopiladas {len(jobs)} ofertas de {platform_name}")
        except Exception as e:
            logger.error(f"Error en scraper de {platform_name}: {str(e)}")
            continue

    logger.info(f"\n=== SCRAPING COMPLETADO: {len(all_jobs)} ofertas totales ===\n")
    return all_jobs


def run_analysis(jobs: List[JobOffer], config: ConfigLoader) -> dict:
    """
    Ejecuta el análisis de datos.

    Args:
        jobs: Lista de ofertas
        config: Configuración del sistema

    Returns:
        Diccionario con resultados del análisis
    """
    logger.info("=== INICIANDO ANÁLISIS DE DATOS ===")

    analyzer = DataAnalyzer(config)
    analysis = analyzer.analyze(jobs)

    logger.info("=== ANÁLISIS COMPLETADO ===\n")
    return analysis


def run_visualization(
    analysis: dict,
    jobs: List[JobOffer],
    config: ConfigLoader
) -> dict:
    """
    Genera visualizaciones.

    Args:
        analysis: Resultados del análisis
        jobs: Lista de ofertas
        config: Configuración del sistema

    Returns:
        Diccionario con rutas de gráficos generados
    """
    logger.info("=== GENERANDO VISUALIZACIONES ===")

    visualizer = DataVisualizer(config)
    chart_paths = visualizer.create_all_visualizations(analysis, jobs)

    logger.info(f"Generados {len(chart_paths)} gráficos")
    logger.info("=== VISUALIZACIONES COMPLETADAS ===\n")
    return chart_paths


def run_reporting(
    analysis: dict,
    chart_paths: dict,
    config: ConfigLoader,
    jobs: list = None
) -> Path:
    """
    Genera informe final.

    Args:
        analysis: Resultados del análisis
        chart_paths: Rutas de gráficos
        config: Configuración del sistema
        jobs: Lista de ofertas de trabajo

    Returns:
        Ruta del informe generado
    """
    logger.info("=== GENERANDO INFORME ===")

    reporter = ReportGenerator(config)
    analyzer = DataAnalyzer(config)

    # Generar insights
    insights = analyzer.get_insights(analysis)

    # Generar informe HTML
    report_path = reporter.generate_html_report(analysis, insights, chart_paths, jobs)

    # Generar también Markdown si está configurado
    if config.get('reports.format') == 'markdown':
        reporter.generate_markdown_report(analysis, insights)

    logger.info(f"Informe generado: {report_path}")
    logger.info("=== INFORME COMPLETADO ===\n")
    return report_path


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Job Scraper - Recopilador y analizador de ofertas de trabajo'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Ruta al archivo de configuración YAML'
    )

    parser.add_argument(
        '--platforms',
        nargs='+',
        help='Plataformas a scrapear (ej: indeed infojobs)'
    )

    parser.add_argument(
        '--keywords',
        nargs='+',
        help='Palabras clave de búsqueda'
    )

    parser.add_argument(
        '--location',
        type=str,
        help='Ubicación para filtrar ofertas'
    )

    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Saltar scraping y usar datos existentes'
    )

    parser.add_argument(
        '--load-from',
        type=str,
        help='Cargar datos desde archivo CSV o JSON'
    )

    parser.add_argument(
        '--no-report',
        action='store_true',
        help='No generar informe'
    )

    parser.add_argument(
        '--no-visualizations',
        action='store_true',
        help='No generar visualizaciones'
    )

    args = parser.parse_args()

    try:
        # Cargar configuración
        config = ConfigLoader(args.config) if args.config else ConfigLoader()
        setup_logging(config)

        logger.info("╔═══════════════════════════════════════════════════════╗")
        logger.info("║         JOB SCRAPER - CIENCIA DE DATOS              ║")
        logger.info("╚═══════════════════════════════════════════════════════╝\n")

        # Inicializar almacenamiento
        storage = DataStorage(config)

        # Obtener ofertas
        jobs = []

        if args.load_from:
            # Cargar desde archivo
            logger.info(f"Cargando datos desde {args.load_from}")
            file_path = Path(args.load_from)
            if file_path.suffix == '.csv':
                jobs = storage.load_jobs_from_csv(file_path)
            elif file_path.suffix == '.json':
                jobs = storage.load_jobs_from_json(file_path)
            else:
                logger.error("Formato de archivo no soportado (usa .csv o .json)")
                return

        elif not args.skip_scraping:
            # Ejecutar scraping
            jobs = run_scraping(
                config,
                platforms=args.platforms,
                keywords=args.keywords,
                location=args.location
            )

            # Guardar datos
            if jobs:
                logger.info("Guardando datos recopilados...")
                saved_files = storage.save_jobs(jobs)
                for format_type, path in saved_files.items():
                    logger.info(f"  - {format_type.upper()}: {path}")
            else:
                logger.warning("No se recopilaron ofertas")
                return

        else:
            # Cargar desde base de datos
            logger.info("Cargando datos desde base de datos...")
            jobs = storage.get_all_jobs_from_db()

        if not jobs:
            logger.error("No hay datos para analizar")
            return

        # Análisis
        analysis = run_analysis(jobs, config)

        # Visualizaciones
        chart_paths = {}
        if not args.no_visualizations:
            chart_paths = run_visualization(analysis, jobs, config)

        # Informe
        if not args.no_report:
            report_path = run_reporting(analysis, chart_paths, config, jobs)
            logger.info(f"\n✅ Proceso completado exitosamente")
            logger.info(f"📄 Informe disponible en: {report_path}")
        else:
            logger.info(f"\n✅ Proceso completado exitosamente")

        # Mostrar insights en consola
        logger.info("\n" + "="*60)
        logger.info("INSIGHTS PRINCIPALES:")
        logger.info("="*60)
        analyzer = DataAnalyzer(config)
        insights = analyzer.get_insights(analysis)
        for insight in insights:
            logger.info(f"  {insight}")
        logger.info("="*60 + "\n")

    except KeyboardInterrupt:
        logger.warning("\n\nProceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
