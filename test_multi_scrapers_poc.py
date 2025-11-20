"""
Prueba de Concepto (PoC) - Verificación de Scrapers Multi-Fuente
================================================================

Este script prueba los 10 scrapers solicitados extrayendo un pequeño
conjunto de datos de cada fuente para verificar que funcionan correctamente.

Scrapers a probar:
1. Glassdoor
2. Monster
3. InfoEmpleo
4. Workana
5. SimplyHired
6. ZipRecruiter
7. Randstad
8. MichaelPage
9. Tecnoempleo
10. Hays
"""

import sys
import os
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
logger.add(
    f"logs/poc_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    rotation="10 MB",
    level="DEBUG"
)


class MultiScraperPoC:
    """Prueba de concepto para scrapers multi-fuente."""

    def __init__(self):
        """Inicializa la PoC."""
        self.scrapers_to_test = [
            'glassdoor',
            'monster',
            'infoempleo',
            'workana',
            'simplyhired',
            'ziprecruiter',
            'randstad',
            'michaelpage',
            'tecnoempleo',
            'hays'
        ]
        self.results = {}
        self.test_keywords = ['python', 'data science']
        self.test_location = 'Madrid, España'
        self.max_jobs_per_scraper = 10  # Solo 10 para PoC

    def test_scraper(self, scraper_name: str) -> dict:
        """
        Prueba un scraper individual.

        Args:
            scraper_name: Nombre del scraper a probar

        Returns:
            Diccionario con resultados del test
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 PROBANDO: {scraper_name.upper()}")
        logger.info(f"{'='*60}")

        result = {
            'scraper': scraper_name,
            'success': False,
            'jobs_found': 0,
            'error': None,
            'execution_time': 0,
            'sample_jobs': []
        }

        try:
            # Importar dinámicamente el scraper
            # NOTA: Esto funcionará cuando tengas la rama estable mergeada
            from src.scrapers.scraper_factory import ScraperFactory
            from src.utils.config_loader import ConfigLoader

            config = ConfigLoader()

            # Reducir número máximo de ofertas para PoC
            config.config['scraping']['max_jobs_per_platform'] = self.max_jobs_per_scraper

            start_time = datetime.now()

            # Crear scraper usando factory
            scraper = ScraperFactory.create_scraper(scraper_name, config)

            logger.info(f"📡 Buscando ofertas: keywords={self.test_keywords}, location={self.test_location}")

            # Ejecutar scraping
            jobs = scraper.scrape_jobs(
                keywords=self.test_keywords,
                location=self.test_location
            )

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # Guardar resultados
            result['success'] = True
            result['jobs_found'] = len(jobs)
            result['execution_time'] = execution_time

            # Guardar muestra de 3 ofertas
            for job in jobs[:3]:
                result['sample_jobs'].append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'url': job.url[:80] + '...' if len(job.url) > 80 else job.url
                })

            logger.success(f"✅ {scraper_name}: {len(jobs)} ofertas encontradas en {execution_time:.2f}s")

            # Mostrar muestra de ofertas
            if jobs:
                logger.info(f"\n📋 Muestra de ofertas de {scraper_name}:")
                for i, job in enumerate(jobs[:3], 1):
                    logger.info(f"  {i}. {job.title} @ {job.company}")
                    logger.info(f"     📍 {job.location}")
                    if job.technologies:
                        logger.info(f"     🛠️  {', '.join(job.technologies[:5])}")

        except ImportError as e:
            error_msg = f"No se pudo importar el scraper. ¿Ya mergeaste la rama estable? Error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result['error'] = error_msg

        except Exception as e:
            error_msg = f"Error ejecutando scraper: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result['error'] = error_msg

        return result

    def run_all_tests(self):
        """Ejecuta tests en todos los scrapers."""
        logger.info("🚀 INICIANDO PRUEBA DE CONCEPTO - MULTI-SCRAPERS")
        logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        total_jobs = 0
        successful_scrapers = 0
        failed_scrapers = 0

        for scraper_name in self.scrapers_to_test:
            result = self.test_scraper(scraper_name)
            self.results[scraper_name] = result

            if result['success']:
                successful_scrapers += 1
                total_jobs += result['jobs_found']
            else:
                failed_scrapers += 1

        # Mostrar resumen final
        self._print_summary(successful_scrapers, failed_scrapers, total_jobs)

        return self.results

    def _print_summary(self, successful: int, failed: int, total_jobs: int):
        """Imprime resumen de resultados."""
        logger.info(f"\n{'='*80}")
        logger.info("📊 RESUMEN DE PRUEBA DE CONCEPTO")
        logger.info(f"{'='*80}\n")

        logger.info(f"📈 Estadísticas Generales:")
        logger.info(f"   • Scrapers probados: {len(self.scrapers_to_test)}")
        logger.info(f"   • ✅ Exitosos: {successful}")
        logger.info(f"   • ❌ Fallidos: {failed}")
        logger.info(f"   • 📋 Total ofertas encontradas: {total_jobs}")
        logger.info(f"   • 📊 Promedio por scraper: {total_jobs/successful if successful > 0 else 0:.1f}\n")

        logger.info("🔍 Detalle por Scraper:")
        logger.info(f"{'─'*80}")
        logger.info(f"{'Scraper':<20} {'Estado':<10} {'Ofertas':<10} {'Tiempo (s)':<12} {'Error'}")
        logger.info(f"{'─'*80}")

        for scraper_name, result in self.results.items():
            status = "✅ OK" if result['success'] else "❌ FAIL"
            jobs = result['jobs_found']
            time = f"{result['execution_time']:.1f}" if result['success'] else "N/A"
            error = result['error'][:30] + "..." if result['error'] else ""

            logger.info(f"{scraper_name:<20} {status:<10} {jobs:<10} {time:<12} {error}")

        logger.info(f"{'─'*80}\n")

        # Recomendaciones
        if failed > 0:
            logger.warning("⚠️  RECOMENDACIONES:")
            for scraper_name, result in self.results.items():
                if not result['success']:
                    logger.warning(f"   • {scraper_name}: {result['error']}")

        logger.info("\n💡 Próximos Pasos:")
        if "No se pudo importar el scraper" in str(self.results.values()):
            logger.info("   1. Mergea la rama estable con: git merge claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6")
            logger.info("   2. Instala dependencias: pip install -r requirements.txt")
            logger.info("   3. Vuelve a ejecutar este script")
        else:
            logger.info("   1. Revisar scrapers fallidos y ajustar selectores si es necesario")
            logger.info("   2. Ejecutar script completo: python scripts/search_all_platforms.py")
            logger.info("   3. Analizar resultados: python scripts/analyze_results.py")


def main():
    """Función principal."""
    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)

    # Ejecutar PoC
    poc = MultiScraperPoC()
    results = poc.run_all_tests()

    # Retornar código de salida apropiado
    failed_count = sum(1 for r in results.values() if not r['success'])
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
