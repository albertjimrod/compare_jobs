"""
Scraper para InfoJobs.
NOTA: InfoJobs tiene una API oficial que es preferible usar si se dispone de credenciales.
Este scraper es una implementación básica para demostración.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from loguru import logger

from .base_scraper import BaseScraper
from ..models.job_offer import JobOffer, ContractType, WorkLocation
from ..utils.scraping_utils import ScrapingUtils


class InfojobsScraper(BaseScraper):
    """Scraper para la plataforma InfoJobs."""

    BASE_URL = "https://www.infojobs.net"

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "InfoJobs"

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """
        Recopila ofertas de trabajo de InfoJobs.

        Args:
            keywords: Lista de palabras clave para buscar
            location: Ubicación para filtrar ofertas

        Returns:
            Lista de ofertas de trabajo encontradas
        """
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        if location is None:
            location = ""

        logger.info(f"Iniciando scraping de {self.platform_name}...")
        logger.warning(
            f"{self.platform_name} tiene protección anti-scraping. "
            "Se recomienda usar su API oficial."
        )
        self.clear_jobs()

        for keyword in keywords:
            try:
                logger.info(f"Buscando: '{keyword}'")
                jobs = self._search_keyword(keyword, location)
                self.jobs.extend(jobs)

                if self.max_jobs > 0 and len(self.jobs) >= self.max_jobs:
                    logger.info(f"Alcanzado límite de {self.max_jobs} ofertas")
                    break

            except Exception as e:
                logger.error(f"Error buscando '{keyword}': {str(e)}")
                continue

        logger.info(f"Scraping completado. Total ofertas: {len(self.jobs)}")
        return self.jobs

    def _search_keyword(self, keyword: str, location: str) -> List[JobOffer]:
        """
        Busca ofertas para una palabra clave específica.

        Args:
            keyword: Palabra clave de búsqueda
            location: Ubicación

        Returns:
            Lista de ofertas encontradas
        """
        jobs = []

        try:
            # Construir URL de búsqueda
            # Nota: Esta es una URL simplificada. InfoJobs puede cambiar su estructura.
            search_url = f"{self.BASE_URL}/empleo/{keyword.replace(' ', '-')}"

            logger.debug(f"Consultando: {search_url}")

            # Hacer request con headers apropiados
            headers = ScrapingUtils.get_headers()
            response = requests.get(search_url, headers=headers, timeout=self.timeout)

            # InfoJobs puede retornar 403 o requerir cookies
            if response.status_code == 403:
                logger.warning(
                    f"{self.platform_name} bloqueó el request. "
                    "Considera usar Selenium o la API oficial."
                )
                return jobs

            response.raise_for_status()

            # Parsear HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Intentar encontrar ofertas
            # NOTA: Los selectores pueden cambiar. Esto es solo un ejemplo.
            job_elements = soup.find_all('div', class_='offer-element')

            if not job_elements:
                # Intentar selectores alternativos
                job_elements = soup.find_all('article', class_='job')

            if not job_elements:
                logger.warning(
                    f"No se pudieron encontrar ofertas en {self.platform_name}. "
                    "Es posible que la estructura del sitio haya cambiado."
                )
                return jobs

            logger.debug(f"Encontrados {len(job_elements)} elementos de trabajo")

            for elem in job_elements:
                try:
                    job = self._parse_job_element(elem)
                    if job:
                        jobs.append(job)

                    if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                        break

                except Exception as e:
                    logger.warning(f"Error parseando elemento: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")

        return jobs

    def _parse_job_element(self, elem) -> Optional[JobOffer]:
        """
        Extrae información de un elemento de oferta.

        Args:
            elem: Elemento BeautifulSoup

        Returns:
            Objeto JobOffer o None si falla
        """
        try:
            # Título
            title_elem = elem.find('a', class_='title')
            if not title_elem:
                title_elem = elem.find('h2') or elem.find('h3')

            if not title_elem:
                return None

            title = ScrapingUtils.clean_text(title_elem.get_text())

            # URL
            job_url = ""
            if title_elem.get('href'):
                job_url = title_elem['href']
                if not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url

            # Empresa
            company_elem = elem.find('a', class_='company-name')
            if not company_elem:
                company_elem = elem.find('span', class_='company')

            company = ScrapingUtils.clean_text(
                company_elem.get_text() if company_elem else "Desconocido"
            )

            # Ubicación
            location_elem = elem.find('span', class_='location')
            location = ScrapingUtils.clean_text(
                location_elem.get_text() if location_elem else ""
            )

            # Descripción
            desc_elem = elem.find('div', class_='description')
            description = ScrapingUtils.clean_text(
                desc_elem.get_text() if desc_elem else ""
            )

            # Crear oferta
            job_offer = self._create_job_offer(
                title=title,
                company=company,
                url=job_url,
                description=description,
                location=location,
                work_location_type=WorkLocation.UNKNOWN,
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando elemento de trabajo: {str(e)}")
            return None
