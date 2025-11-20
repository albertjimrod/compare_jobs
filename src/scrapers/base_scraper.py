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

    def _sleep(self, extra_delay: float = 0):
        """
        Espera un tiempo aleatorio entre requests con jitter para evitar detección.

        Args:
            extra_delay: Delay adicional en segundos (útil después de errores)
        """
        # Delay base + variación aleatoria (20-50%) + extra delay
        base_delay = self.delay + extra_delay
        jitter = base_delay * random.uniform(0.2, 0.5)
        sleep_time = base_delay + jitter

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

    def remove_duplicates(self):
        """
        Elimina ofertas duplicadas basándose en URL o título+empresa.
        Mantiene la primera ocurrencia.
        """
        seen_urls = set()
        seen_titles = set()
        unique_jobs = []
        duplicates_count = 0

        for job in self.jobs:
            # Crear identificador único basado en URL
            job_id = job.url if job.url else f"{job.title}_{job.company}"

            if job_id not in seen_urls and job_id not in seen_titles:
                seen_urls.add(job_id)
                seen_titles.add(job_id)
                unique_jobs.append(job)
            else:
                duplicates_count += 1

        if duplicates_count > 0:
            logger.info(f"🗑️  Eliminados {duplicates_count} duplicados. Ofertas únicas: {len(unique_jobs)}")

        self.jobs = unique_jobs

    def _extract_technologies(self, text: str) -> List[str]:
        """
        Extrae tecnologías mencionadas en el texto usando regex para palabras completas.
        Mejora la detección usando word boundaries para evitar falsos positivos.

        Args:
            text: Texto donde buscar tecnologías

        Returns:
            Lista de tecnologías encontradas
        """
        if not text:
            return []

        import re

        technologies = []

        # Obtener tecnologías de la configuración
        tech_config = self.config.get('analysis.technologies', {})

        for category, tech_list in tech_config.items():
            for tech in tech_list:
                # Crear patrón regex para buscar palabra completa (case-insensitive)
                # \b = word boundary para evitar coincidencias parciales
                # Por ejemplo, buscar "SQL" no coincidirá con "NoSQL"
                pattern = r'\b' + re.escape(tech) + r'\b'

                if re.search(pattern, text, re.IGNORECASE):
                    technologies.append(tech)

        return list(set(technologies))  # Eliminar duplicados

    def _extract_skills(self, text: str) -> List[str]:
        """
        Extrae habilidades mencionadas en el texto usando regex.
        Mejora la detección usando word boundaries.

        Args:
            text: Texto donde buscar habilidades

        Returns:
            Lista de habilidades encontradas
        """
        if not text:
            return []

        import re

        skills = []

        # Obtener habilidades de la configuración
        skill_list = self.config.get('analysis.skills', [])

        for skill in skill_list:
            # Buscar palabra completa (case-insensitive)
            # Permite guiones en habilidades como "Machine Learning"
            pattern = r'\b' + re.escape(skill) + r'\b'

            if re.search(pattern, text, re.IGNORECASE):
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
