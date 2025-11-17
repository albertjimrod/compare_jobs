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

# Importar nuevos scrapers (solo si Selenium está disponible)
if SELENIUM_AVAILABLE:
    try:
        from .linkedin_scraper import LinkedInScraper
        from .glassdoor_scraper import GlassdoorScraper
        from .monster_scraper import MonsterScraper
        from .upwork_scraper import UpworkScraper
        from .freelancer_scraper import FreelancerScraper
        from .workana_scraper import WorkanaScraper
        from .malt_scraper import MaltScraper
        from .fiverr_scraper import FiverrScraper
        from .simplyhired_scraper import SimplyHiredScraper
        from .ziprecruiter_scraper import ZipRecruiterScraper
        from .careerbuilder_scraper import CareerBuilderScraper
        from .randstad_scraper import RandstadScraper
        from .italenters_scraper import iTalentersScraper
        from .michaelpage_scraper import MichaelPageScraper
        from .tecnoempleo_scraper import TecnoempleoScraper
        from .hays_scraper import HaysScraper
        from .infoempleo_scraper import InfoempleoScraper
    except ImportError as e:
        logger.debug(f"Algunos scrapers no pudieron importarse: {e}")

from ..utils.config_loader import ConfigLoader


class ScraperFactory:
    """Factory para crear instancias de scrapers."""

    # Mapeo de plataformas a clases de scrapers
    # Se usa Selenium por defecto si está disponible
    _SCRAPERS: Dict[str, Type[BaseScraper]] = {
        # Indeed (con Selenium y fallback)
        'indeed': IndeedScraperSelenium if SELENIUM_AVAILABLE else IndeedScraper,
        'indeed-requests': IndeedScraper,  # Versión requests (menos confiable)
        'indeed-selenium': IndeedScraperSelenium if SELENIUM_AVAILABLE else None,

        # InfoJobs (existente)
        'infojobs': InfojobsScraper,

        # Plataformas principales (requieren Selenium)
        'linkedin': LinkedInScraper if SELENIUM_AVAILABLE else None,
        'glassdoor': GlassdoorScraper if SELENIUM_AVAILABLE else None,
        'monster': MonsterScraper if SELENIUM_AVAILABLE else None,

        # Plataformas freelance
        'upwork': UpworkScraper if SELENIUM_AVAILABLE else None,
        'freelancer': FreelancerScraper if SELENIUM_AVAILABLE else None,
        'workana': WorkanaScraper if SELENIUM_AVAILABLE else None,
        'malt': MaltScraper if SELENIUM_AVAILABLE else None,
        'fiverr': FiverrScraper if SELENIUM_AVAILABLE else None,

        # Agregadores y portales de empleo
        'simplyhired': SimplyHiredScraper if SELENIUM_AVAILABLE else None,
        'ziprecruiter': ZipRecruiterScraper if SELENIUM_AVAILABLE else None,
        'careerbuilder': CareerBuilderScraper if SELENIUM_AVAILABLE else None,

        # Empresas de recursos humanos
        'randstad': RandstadScraper if SELENIUM_AVAILABLE else None,
        'michaelpage': MichaelPageScraper if SELENIUM_AVAILABLE else None,
        'hays': HaysScraper if SELENIUM_AVAILABLE else None,

        # Portales españoles especializados
        'italenters': iTalentersScraper if SELENIUM_AVAILABLE else None,
        'tecnoempleo': TecnoempleoScraper if SELENIUM_AVAILABLE else None,
        'infoempleo': InfoempleoScraper if SELENIUM_AVAILABLE else None,
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
