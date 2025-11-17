"""
Módulo de scrapers para diferentes plataformas de empleo.
"""

from .base_scraper import BaseScraper
from .scraper_factory import ScraperFactory

__all__ = ['BaseScraper', 'ScraperFactory']
