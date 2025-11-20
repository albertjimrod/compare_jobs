"""
Scraper genérico que puede servir de plantilla para nuevas plataformas.
Este archivo contiene ejemplos comentados para facilitar la implementación de nuevos scrapers.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from loguru import logger

from .base_scraper import BaseScraper
from ..models.job_offer import JobOffer, WorkLocation
from ..utils.scraping_utils import ScrapingUtils


class GenericScraper(BaseScraper):
    """
    Scraper genérico que sirve como plantilla.

    Para crear un nuevo scraper:
    1. Copia este archivo y renómbralo (ej: linkedin_scraper.py)
    2. Cambia el nombre de la clase (ej: LinkedinScraper)
    3. Actualiza BASE_URL con la URL de la plataforma
    4. Implementa los métodos de parsing específicos
    5. Registra el scraper en scraper_factory.py
    """

    # URL base de la plataforma
    BASE_URL = "https://ejemplo.com"

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "NombrePlataforma"  # Cambiar por el nombre real

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """
        Recopila ofertas de trabajo de la plataforma.

        Args:
            keywords: Lista de palabras clave para buscar
            location: Ubicación para filtrar ofertas

        Returns:
            Lista de ofertas de trabajo encontradas
        """
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        logger.info(f"Iniciando scraping de {self.platform_name}...")
        self.clear_jobs()

        for keyword in keywords:
            try:
                logger.info(f"Buscando: '{keyword}'")
                jobs = self._search_keyword(keyword, location or "")
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
        page = 1

        while True:
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            try:
                # 1. Construir URL de búsqueda
                url = self._build_search_url(keyword, location, page)
                logger.debug(f"Consultando página {page}: {url}")

                # 2. Hacer request con headers
                headers = ScrapingUtils.get_headers()
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()

                # 3. Parsear HTML
                soup = BeautifulSoup(response.content, 'lxml')

                # 4. Encontrar elementos de ofertas
                # Cambiar selector según la estructura del sitio
                job_elements = soup.find_all('div', class_='job-card')

                if not job_elements:
                    logger.debug("No se encontraron más ofertas")
                    break

                logger.debug(f"Encontrados {len(job_elements)} elementos en página {page}")

                # 5. Parsear cada oferta
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

                # 6. Siguiente página
                page += 1
                self._sleep()

            except Exception as e:
                logger.error(f"Error en página {page}: {str(e)}")
                break

        return jobs

    def _build_search_url(self, keyword: str, location: str, page: int) -> str:
        """
        Construye la URL de búsqueda.

        Args:
            keyword: Palabra clave
            location: Ubicación
            page: Número de página

        Returns:
            URL completa
        """
        # Ejemplo de construcción de URL
        # Adaptar según la plataforma
        params = {
            'q': keyword,
            'l': location,
            'page': str(page)
        }

        return ScrapingUtils.build_search_url(
            f"{self.BASE_URL}/jobs",
            params,
            page
        )

    def _parse_job_element(self, elem) -> Optional[JobOffer]:
        """
        Extrae información de un elemento de oferta.

        Args:
            elem: Elemento BeautifulSoup

        Returns:
            Objeto JobOffer o None si falla
        """
        try:
            # 1. Extraer título
            # Cambiar selector según estructura del sitio
            title_elem = elem.find('h2', class_='job-title')
            if not title_elem:
                return None
            title = ScrapingUtils.clean_text(title_elem.get_text())

            # 2. Extraer empresa
            company_elem = elem.find('span', class_='company-name')
            company = ScrapingUtils.clean_text(
                company_elem.get_text() if company_elem else "Desconocido"
            )

            # 3. Extraer URL
            link_elem = elem.find('a', class_='job-link')
            job_url = ""
            if link_elem and link_elem.get('href'):
                job_url = link_elem['href']
                if not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url

            # 4. Extraer ubicación
            location_elem = elem.find('span', class_='location')
            location = ScrapingUtils.clean_text(
                location_elem.get_text() if location_elem else ""
            )

            # 5. Extraer descripción
            desc_elem = elem.find('div', class_='description')
            description = ScrapingUtils.clean_text(
                desc_elem.get_text() if desc_elem else ""
            )

            # 6. Extraer salario (si está disponible)
            salary_elem = elem.find('span', class_='salary')
            salary_info = {'salary_min': None, 'salary_max': None, 'salary_currency': 'EUR'}
            if salary_elem:
                salary_text = salary_elem.get_text()
                salary_info = ScrapingUtils.extract_salary(salary_text)

            # 7. Determinar tipo de ubicación
            work_location = WorkLocation.UNKNOWN
            if location:
                location_lower = location.lower()
                if 'remot' in location_lower:
                    work_location = WorkLocation.REMOTE
                elif 'híbrid' in location_lower or 'hybrid' in location_lower:
                    work_location = WorkLocation.HYBRID
                else:
                    work_location = WorkLocation.ONSITE

            # 8. Crear y retornar oferta
            job_offer = self._create_job_offer(
                title=title,
                company=company,
                url=job_url,
                description=description,
                location=location,
                work_location_type=work_location,
                **salary_info
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando elemento: {str(e)}")
            return None


# Ejemplo de uso:
# 1. Copia este archivo
# 2. Renombra la clase
# 3. Actualiza los selectores CSS según la estructura del sitio
# 4. Registra en ScraperFactory:
#
# from .tu_scraper import TuScraper
# ScraperFactory._SCRAPERS['tuplataforma'] = TuScraper
