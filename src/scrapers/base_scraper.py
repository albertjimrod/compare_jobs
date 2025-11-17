"""
Clase base abstracta para scrapers de ofertas de trabajo.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
import time
import random
from loguru import logger

from ..models.job_offer import JobOffer
from ..utils.config_loader import ConfigLoader


class BaseScraper(ABC):
    """Clase base para todos los scrapers de plataformas de empleo."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Inicializa el scraper.

        Args:
            config: Configuración del sistema
        """
        self.config = config or ConfigLoader()
        self.platform_name = self._get_platform_name()
        self.jobs: List[JobOffer] = []

        # Configuración de scraping
        self.delay = self.config.get('scraping.delay_between_requests', 2)
        self.max_retries = self.config.get('scraping.max_retries', 3)
        self.timeout = self.config.get('scraping.page_load_timeout', 30)
        self.max_jobs = self.config.get('scraping.max_jobs_per_platform', 100)

        logger.info(f"Inicializado scraper para {self.platform_name}")

    @abstractmethod
    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        pass

    @abstractmethod
    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """
        Método principal para recopilar ofertas de trabajo.

        Args:
            keywords: Lista de palabras clave para buscar
            location: Ubicación para filtrar ofertas

        Returns:
            Lista de ofertas de trabajo encontradas
        """
        pass

    def _sleep(self):
        """Espera un tiempo aleatorio entre requests."""
        sleep_time = self.delay + random.uniform(0, 1)
        logger.debug(f"Esperando {sleep_time:.2f} segundos...")
        time.sleep(sleep_time)

    def _retry_on_failure(self, func, *args, **kwargs):
        """
        Ejecuta una función con reintentos en caso de fallo.

        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre

        Returns:
            Resultado de la función

        Raises:
            Exception: Si todos los reintentos fallan
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Intento {attempt + 1}/{self.max_retries} falló: {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponencial
                    logger.info(f"Esperando {wait_time} segundos antes de reintentar...")
                    time.sleep(wait_time)

        logger.error(f"Todos los reintentos fallaron para {self.platform_name}")
        raise last_exception

    def get_jobs(self) -> List[JobOffer]:
        """Retorna las ofertas recopiladas."""
        return self.jobs

    def get_jobs_count(self) -> int:
        """Retorna el número de ofertas recopiladas."""
        return len(self.jobs)

    def clear_jobs(self):
        """Limpia la lista de ofertas."""
        self.jobs = []
        logger.debug(f"Lista de ofertas limpiada para {self.platform_name}")

    def _extract_technologies(self, text: str) -> List[str]:
        """
        Extrae tecnologías mencionadas en el texto.

        Args:
            text: Texto donde buscar tecnologías

        Returns:
            Lista de tecnologías encontradas
        """
        if not text:
            return []

        text_lower = text.lower()
        technologies = []

        # Obtener tecnologías de la configuración
        tech_config = self.config.get('analysis.technologies', {})

        for category, tech_list in tech_config.items():
            for tech in tech_list:
                if tech.lower() in text_lower:
                    technologies.append(tech)

        return list(set(technologies))  # Eliminar duplicados

    def _extract_skills(self, text: str) -> List[str]:
        """
        Extrae habilidades mencionadas en el texto.

        Args:
            text: Texto donde buscar habilidades

        Returns:
            Lista de habilidades encontradas
        """
        if not text:
            return []

        text_lower = text.lower()
        skills = []

        # Obtener habilidades de la configuración
        skill_list = self.config.get('analysis.skills', [])

        for skill in skill_list:
            if skill.lower() in text_lower:
                skills.append(skill)

        return list(set(skills))  # Eliminar duplicados

    def _create_job_offer(self, **kwargs) -> JobOffer:
        """
        Crea una oferta de trabajo con el nombre de plataforma.

        Args:
            **kwargs: Argumentos para crear JobOffer

        Returns:
            Objeto JobOffer
        """
        # Asegurar que la plataforma esté establecida
        kwargs['platform'] = self.platform_name

        # Establecer fecha de scraping
        kwargs['scraped_date'] = datetime.now()

        # Extraer tecnologías y habilidades si hay descripción
        description = kwargs.get('description', '')
        if description:
            if 'technologies' not in kwargs or not kwargs['technologies']:
                kwargs['technologies'] = self._extract_technologies(description)
            if 'skills' not in kwargs or not kwargs['skills']:
                kwargs['skills'] = self._extract_skills(description)

        return JobOffer(**kwargs)

    def __repr__(self) -> str:
        """Representación en string del scraper."""
        return f"{self.__class__.__name__}(platform='{self.platform_name}', jobs={self.get_jobs_count()})"
