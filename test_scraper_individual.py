#!/usr/bin/env python3
"""
Script para probar scrapers individuales con configuración flexible.

Uso:
    python test_scraper_individual.py <platform> [opciones]

Ejemplos:
    # Probar MichaelPage con 5 ofertas en modo visual
    python test_scraper_individual.py michaelpage --headless=false --max-jobs=5

    # Probar Randstad con keywords específicas
    python test_scraper_individual.py randstad --keywords="python,data science" --location="Barcelona"

    # Probar Tecnoempleo con logging detallado
    python test_scraper_individual.py tecnoempleo --verbose
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from loguru import logger

# Configurar logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def parse_arguments():
    """Parse argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Probar scraper individual',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s michaelpage
  %(prog)s randstad --headless=false --max-jobs=10
  %(prog)s tecnoempleo --keywords="python,django" --location="Madrid"
  %(prog)s glassdoor --verbose --delay=20
        """
    )

    parser.add_argument(
        'platform',
        type=str,
        help='Nombre del scraper a probar (glassdoor, monster, randstad, etc.)'
    )

    parser.add_argument(
        '--headless',
        type=lambda x: x.lower() == 'true',
        default=True,
        help='Ejecutar navegador en modo headless (true/false). Default: true'
    )

    parser.add_argument(
        '--max-jobs',
        type=int,
        default=10,
        help='Número máximo de ofertas a extraer. Default: 10'
    )

    parser.add_argument(
        '--keywords',
        type=str,
        default='python,data science',
        help='Keywords separadas por comas. Default: "python,data science"'
    )

    parser.add_argument(
        '--location',
        type=str,
        default='Madrid, España',
        help='Ubicación para búsqueda. Default: "Madrid, España"'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=None,
        help='Delay personalizado entre requests en segundos. Default: configuración del scraper'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Habilitar logging detallado (DEBUG level)'
    )

    parser.add_argument(
        '--save',
        type=str,
        default=None,
        help='Guardar resultados en archivo CSV. Ejemplo: --save=results.csv'
    )

    return parser.parse_args()


def setup_logging(verbose=False):
    """Configura logging según nivel de verbosidad."""
    log_level = "DEBUG" if verbose else "INFO"

    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level
    )

    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)

    # Guardar log en archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"logs/test_{args.platform}_{timestamp}.log"

    logger.add(
        log_file,
        rotation="10 MB",
        level="DEBUG"
    )

    logger.info(f"📝 Log guardado en: {log_file}")


def test_scraper(platform, keywords, location, config_overrides=None):
    """
    Prueba un scraper individual.

    Args:
        platform: Nombre del scraper
        keywords: Lista de keywords
        location: Ubicación para búsqueda
        config_overrides: Configuraciones personalizadas

    Returns:
        Lista de ofertas encontradas
    """
    try:
        # Importar módulos necesarios
        from src.scrapers.scraper_factory import ScraperFactory
        from src.utils.config_loader import ConfigLoader

        logger.info(f"\n{'='*70}")
        logger.info(f"🧪 PROBANDO SCRAPER: {platform.upper()}")
        logger.info(f"{'='*70}\n")

        # Cargar configuración
        config = ConfigLoader()

        # Aplicar overrides de configuración
        if config_overrides:
            for key, value in config_overrides.items():
                logger.debug(f"Override config: {key} = {value}")
                config.config[key] = value

        logger.info(f"📋 Parámetros de búsqueda:")
        logger.info(f"   • Keywords: {keywords}")
        logger.info(f"   • Ubicación: {location}")
        logger.info(f"   • Máximo ofertas: {config.get('scraping.max_jobs_per_platform', 10)}")
        logger.info(f"   • Modo headless: {config.get('scraping.headless_mode', True)}")
        logger.info(f"   • Delay entre requests: {config.get('scraping.delay_between_requests', 2)}s")
        logger.info("")

        # Crear scraper
        logger.info(f"🔧 Creando scraper para {platform}...")
        scraper = ScraperFactory.create_scraper(platform, config)

        # Ejecutar scraping
        logger.info(f"🚀 Iniciando scraping...\n")
        start_time = datetime.now()

        jobs = scraper.scrape_jobs(
            keywords=keywords,
            location=location
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Mostrar resultados
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ SCRAPING COMPLETADO")
        logger.info(f"{'='*70}\n")

        logger.info(f"📊 Estadísticas:")
        logger.info(f"   • Ofertas encontradas: {len(jobs)}")
        logger.info(f"   • Tiempo total: {duration:.2f} segundos")
        logger.info(f"   • Tiempo promedio: {duration/len(jobs):.2f}s por oferta" if jobs else "   • N/A")
        logger.info("")

        if jobs:
            logger.info(f"📋 Muestra de ofertas encontradas:\n")

            for i, job in enumerate(jobs[:5], 1):
                logger.info(f"  {i}. {job.title}")
                logger.info(f"     🏢 {job.company}")
                logger.info(f"     📍 {job.location}")

                if hasattr(job, 'salary') and job.salary:
                    logger.info(f"     💰 {job.salary}")

                if job.technologies:
                    techs = ', '.join(job.technologies[:5])
                    if len(job.technologies) > 5:
                        techs += f" (+{len(job.technologies)-5} más)"
                    logger.info(f"     🛠️  {techs}")

                if job.url:
                    url_display = job.url[:60] + "..." if len(job.url) > 60 else job.url
                    logger.info(f"     🔗 {url_display}")

                logger.info("")

            if len(jobs) > 5:
                logger.info(f"  ... y {len(jobs)-5} ofertas más\n")

        return jobs

    except ImportError as e:
        logger.error(f"\n❌ ERROR DE IMPORTACIÓN")
        logger.error(f"No se pudieron importar los módulos necesarios.")
        logger.error(f"¿Ya integraste la rama estable con el merge?\n")
        logger.error(f"Comando: git merge claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6\n")
        logger.error(f"Detalle: {str(e)}\n")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ ERROR DURANTE SCRAPING")
        logger.error(f"Scraper: {platform}")
        logger.error(f"Error: {str(e)}\n")

        if args.verbose:
            import traceback
            logger.error("Traceback completo:")
            logger.error(traceback.format_exc())

        logger.info("\n💡 SUGERENCIAS:")
        logger.info("1. Verifica que el nombre del scraper sea correcto")
        logger.info("2. Prueba en modo no-headless para ver qué sucede:")
        logger.info(f"   python {sys.argv[0]} {platform} --headless=false")
        logger.info("3. Revisa el log detallado con --verbose")
        logger.info("4. Verifica los selectores CSS en el archivo del scraper\n")

        sys.exit(1)


def save_results(jobs, filename):
    """Guarda resultados en archivo CSV."""
    try:
        import pandas as pd

        logger.info(f"\n💾 Guardando resultados en {filename}...")

        # Convertir ofertas a diccionarios
        data = []
        for job in jobs:
            data.append({
                'título': job.title,
                'empresa': job.company,
                'ubicación': job.location,
                'salario': job.salary if hasattr(job, 'salary') and job.salary else 'No especificado',
                'tecnologías': ', '.join(job.technologies) if job.technologies else '',
                'plataforma': job.platform,
                'url': job.url,
                'fecha_scraping': job.scraped_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(job, 'scraped_date') and job.scraped_date else ''
            })

        # Crear DataFrame y guardar
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')

        logger.success(f"✅ Resultados guardados en {filename}")
        logger.info(f"   Puedes abrir el archivo con: excel {filename} o pandas.read_csv('{filename}')")

    except Exception as e:
        logger.error(f"❌ Error guardando resultados: {str(e)}")


def main():
    """Función principal."""
    global args
    args = parse_arguments()

    # Configurar logging
    setup_logging(verbose=args.verbose)

    # Preparar keywords
    keywords = [k.strip() for k in args.keywords.split(',')]

    # Preparar configuración personalizada
    config_overrides = {}

    if args.headless is not None:
        config_overrides['scraping.headless_mode'] = args.headless

    if args.max_jobs:
        config_overrides['scraping.max_jobs_per_platform'] = args.max_jobs

    if args.delay:
        config_overrides['scraping.delay_between_requests'] = args.delay

    # Ejecutar test
    jobs = test_scraper(
        platform=args.platform.lower(),
        keywords=keywords,
        location=args.location,
        config_overrides=config_overrides
    )

    # Guardar resultados si se especificó
    if args.save and jobs:
        save_results(jobs, args.save)

    # Resumen final
    logger.info(f"\n{'='*70}")
    logger.info("🎉 TEST COMPLETADO")
    logger.info(f"{'='*70}\n")

    if jobs:
        logger.success(f"✅ Scraper {args.platform} funcionó correctamente")
        logger.info(f"📊 Total: {len(jobs)} ofertas extraídas")
    else:
        logger.warning(f"⚠️  No se encontraron ofertas")
        logger.info("Esto puede ser normal si no hay ofertas que coincidan con los criterios")

    logger.info("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Scraping interrumpido por el usuario (Ctrl+C)")
        sys.exit(130)
