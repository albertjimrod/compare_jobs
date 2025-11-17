"""
Scraper para Indeed.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from loguru import logger

from .base_scraper import BaseScraper
from ..models.job_offer import JobOffer, ContractType, WorkLocation
from ..utils.scraping_utils import ScrapingUtils


class IndeedScraper(BaseScraper):
    """Scraper para la plataforma Indeed."""

    BASE_URL = "https://es.indeed.com"

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "Indeed"

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """
        Recopila ofertas de trabajo de Indeed.

        Args:
            keywords: Lista de palabras clave para buscar
            location: Ubicación para filtrar ofertas

        Returns:
            Lista de ofertas de trabajo encontradas
        """
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        if location is None:
            location = "España"

        logger.info(f"Iniciando scraping de {self.platform_name}...")
        self.clear_jobs()

        for keyword in keywords:
            try:
                logger.info(f"Buscando: '{keyword}' en {location}")
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
        page = 0
        max_pages = self.config.get('scraping.max_pages_per_session', 5)

        while True:
            # Límite de ofertas
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            # Límite de páginas por sesión (anti-ban)
            if page >= max_pages:
                logger.info(
                    f"Alcanzado límite de {max_pages} páginas por sesión (anti-ban)"
                )
                break

            try:
                # Construir URL de búsqueda
                params = {
                    'q': keyword,
                    'l': location,
                    'start': str(page * 10)
                }

                url = ScrapingUtils.build_search_url(
                    f"{self.BASE_URL}/jobs",
                    params
                )

                logger.debug(f"Consultando: {url}")

                # Hacer request con manejo de rate limiting
                headers = ScrapingUtils.get_headers()
                response = requests.get(url, headers=headers, timeout=self.timeout)

                # Detectar rate limiting (429 Too Many Requests)
                if response.status_code == 429:
                    rate_limit_delay = self.config.get('scraping.rate_limit_delay', 60)
                    logger.warning(
                        f"Rate limit detectado (429). Esperando {rate_limit_delay} segundos..."
                    )
                    self._sleep(extra_delay=rate_limit_delay)
                    continue

                response.raise_for_status()

                # Parsear HTML
                soup = BeautifulSoup(response.content, 'lxml')

                # Encontrar ofertas en la página
                job_cards = soup.find_all('div', class_='job_seen_beacon')

                if not job_cards:
                    logger.debug("No se encontraron más ofertas")
                    break

                logger.debug(f"Encontradas {len(job_cards)} ofertas en página {page + 1}")

                for card in job_cards:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)

                        if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                            break

                    except Exception as e:
                        logger.warning(f"Error parseando oferta: {str(e)}")
                        continue

                # Siguiente página
                page += 1
                self._sleep()

            except Exception as e:
                logger.error(f"Error en página {page}: {str(e)}")
                break

        return jobs

    def _parse_job_card(self, card) -> Optional[JobOffer]:
        """
        Extrae información de una tarjeta de oferta.

        Args:
            card: Elemento BeautifulSoup de la tarjeta

        Returns:
            Objeto JobOffer o None si falla
        """
        try:
            # Título
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                return None
            title = ScrapingUtils.clean_text(title_elem.get_text())

            # Empresa
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = ScrapingUtils.clean_text(
                company_elem.get_text() if company_elem else "Desconocido"
            )

            # Ubicación
            location_elem = card.find('div', {'data-testid': 'text-location'})
            location = ScrapingUtils.clean_text(
                location_elem.get_text() if location_elem else ""
            )

            # URL
            link_elem = title_elem.find('a')
            job_url = ""
            job_id = None
            if link_elem and link_elem.get('href'):
                job_url = self.BASE_URL + link_elem['href']
                # Extraer ID del trabajo
                if 'jk=' in job_url:
                    job_id = job_url.split('jk=')[1].split('&')[0]

            # Descripción (snippet)
            desc_elem = card.find('div', class_='job-snippet')
            description = ScrapingUtils.clean_text(
                desc_elem.get_text() if desc_elem else ""
            )

            # Salario (si está disponible)
            salary_elem = card.find('div', class_='salary-snippet')
            salary_info = {'salary_min': None, 'salary_max': None, 'salary_currency': 'EUR'}
            if salary_elem:
                salary_text = salary_elem.get_text()
                salary_info = ScrapingUtils.extract_salary(salary_text)

            # Determinar tipo de ubicación
            work_location = WorkLocation.UNKNOWN
            location_lower = location.lower()
            if 'remot' in location_lower or 'teletrabajo' in location_lower:
                work_location = WorkLocation.REMOTE
            elif location:
                work_location = WorkLocation.ONSITE

            # Crear oferta
            job_offer = self._create_job_offer(
                title=title,
                company=company,
                url=job_url,
                description=description,
                location=location,
                work_location_type=work_location,
                job_id=job_id,
                **salary_info
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando tarjeta de trabajo: {str(e)}")
            return None
