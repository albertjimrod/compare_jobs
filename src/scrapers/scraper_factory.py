"""
Factory para crear scrapers según la plataforma.
"""

from typing import Optional, Dict, Type
from loguru import logger

from .base_scraper import BaseScraper
from .indeed_scraper import IndeedScraper
from .infojobs_scraper import InfojobsScraper
from ..utils.config_loader import ConfigLoader


class ScraperFactory:
    """Factory para crear instancias de scrapers."""

    # Mapeo de plataformas a clases de scrapers
    _SCRAPERS: Dict[str, Type[BaseScraper]] = {
        'indeed': IndeedScraper,
        'infojobs': InfojobsScraper,
        # Más scrapers se pueden agregar aquí
    }

    @staticmethod
    def create_scraper(
        platform: str,
        config: Optional[ConfigLoader] = None
    ) -> Optional[BaseScraper]:
        """
        Crea un scraper para la plataforma especificada.

        Args:
            platform: Nombre de la plataforma (ej: 'indeed', 'infojobs')
            config: Configuración del sistema

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
        return scraper_class(config)

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
