"""
Factory para crear scrapers según la plataforma.
"""

from typing import Optional, Dict, Type
from loguru import logger

from .base_scraper import BaseScraper
from .indeed_scraper import IndeedScraper
from .infojobs_scraper import InfojobsScraper

# Importar scraper de Selenium si está disponible
try:
    from .indeed_scraper_selenium import IndeedScraperSelenium
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.debug("Selenium scraper no disponible")

from ..utils.config_loader import ConfigLoader


class ScraperFactory:
    """Factory para crear instancias de scrapers."""

    # Mapeo de plataformas a clases de scrapers
    # Se usa Selenium por defecto si está disponible
    _SCRAPERS: Dict[str, Type[BaseScraper]] = {
        'indeed': IndeedScraperSelenium if SELENIUM_AVAILABLE else IndeedScraper,
        'indeed-requests': IndeedScraper,  # Versión requests (menos confiable)
        'indeed-selenium': IndeedScraperSelenium if SELENIUM_AVAILABLE else None,
        'infojobs': InfojobsScraper,
        # Más scrapers se pueden agregar aquí
    }

    @staticmethod
    def create_scraper(
        platform: str,
        config: Optional[ConfigLoader] = None,
        allow_fallback: bool = True
    ) -> Optional[BaseScraper]:
        """
        Crea un scraper para la plataforma especificada.

        Args:
            platform: Nombre de la plataforma (ej: 'indeed', 'infojobs')
            config: Configuración del sistema
            allow_fallback: Si True, usa scraper de requests si Selenium falla

        Returns:
            Instancia del scraper o None si no existe
        """
        platform_lower = platform.lower()

        if platform_lower not in ScraperFactory._SCRAPERS:
            logger.warning(
                f"No hay scraper disponible para '{platform}'. "
                f"Plataformas disponibles: {list(ScraperFactory._SCRAPERS.keys())}"
            )
            return None

        scraper_class = ScraperFactory._SCRAPERS[platform_lower]

        # Verificar si el scraper está disponible (puede ser None si Selenium no está instalado)
        if scraper_class is None:
            logger.error(
                f"Scraper '{platform}' requiere dependencias adicionales. "
                "Instala Selenium con: pip install selenium webdriver-manager"
            )
            return None

        # Intentar crear el scraper
        try:
            scraper = scraper_class(config)
            return scraper

        except (ImportError, RuntimeError) as e:
            error_msg = str(e)

            # Si es Indeed con Selenium y falla, intentar fallback a requests
            if platform_lower == 'indeed' and allow_fallback and SELENIUM_AVAILABLE:
                if 'Chrome' in error_msg or 'cannot find' in error_msg:
                    logger.warning(
                        "⚠️  Selenium no puede ejecutarse (Chrome no instalado). "
                        "Usando scraper de requests como fallback..."
                    )
                    logger.info(
                        "💡 Nota: El scraper de requests tiene menor tasa de éxito (~10% vs ~70%).\n"
                        "   Para mejor rendimiento, instala Chrome y vuelve a intentar."
                    )
                    # Usar scraper de requests como fallback
                    return IndeedScraper(config)

            # Si no hay fallback posible, re-lanzar el error
            logger.error(f"No se pudo crear scraper para '{platform}': {error_msg}")
            raise

    @staticmethod
    def get_available_platforms() -> list:
        """
        Retorna lista de plataformas con scrapers disponibles.

        Returns:
            Lista de nombres de plataformas
        """
        return list(ScraperFactory._SCRAPERS.keys())

    @staticmethod
    def create_all_enabled_scrapers(
        config: Optional[ConfigLoader] = None
    ) -> Dict[str, BaseScraper]:
        """
        Crea scrapers para todas las plataformas habilitadas en la configuración.

        Args:
            config: Configuración del sistema

        Returns:
            Diccionario con scrapers creados {platform_name: scraper}
        """
        if config is None:
            config = ConfigLoader()

        enabled_platforms = config.get_enabled_platforms()
        scrapers = {}

        for platform_name in enabled_platforms.keys():
            scraper = ScraperFactory.create_scraper(platform_name, config)
            if scraper:
                scrapers[platform_name] = scraper
            else:
                logger.info(
                    f"Scraper para '{platform_name}' no está implementado aún, "
                    "pero está habilitado en configuración"
                )

        logger.info(f"Creados {len(scrapers)} scrapers")
        return scrapers

    @staticmethod
    def register_scraper(platform: str, scraper_class: Type[BaseScraper]):
        """
        Registra un nuevo scraper en el factory.

        Args:
            platform: Nombre de la plataforma
            scraper_class: Clase del scraper
        """
        platform_lower = platform.lower()
        ScraperFactory._SCRAPERS[platform_lower] = scraper_class
        logger.info(f"Scraper registrado para '{platform}'")
