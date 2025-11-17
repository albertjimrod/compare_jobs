"""
Scraper para Glassdoor.

IMPORTANTE: Glassdoor tiene protección anti-scraping agresiva.
Recomendaciones:
1. Usar Glassdoor API (https://www.glassdoor.com/developer/index.htm)
2. Selenium con delays largos
3. Considerar partner program para acceso empresarial

Este scraper es una implementación básica educativa.
"""

import time
from typing import List, Optional
from loguru import logger

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from .base_scraper import BaseScraper
from ..models.job_offer import JobOffer, WorkLocation
from ..utils.scraping_utils import ScrapingUtils


class GlassdoorScraper(BaseScraper):
    """Scraper para Glassdoor usando Selenium."""

    BASE_URL = "https://www.glassdoor.es"
    JOBS_URL = "https://www.glassdoor.es/Job/jobs.htm"

    def __init__(self, config=None):
        """Inicializa el scraper de Glassdoor."""
        super().__init__(config)

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Glassdoor scraper requiere Selenium. "
                "Instala con: pip install selenium webdriver-manager"
            )

        self.driver = None

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "Glassdoor"

    def _setup_driver(self):
        """Configura driver de Selenium para Glassdoor."""
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        chrome_options = Options()

        if self.config.get('scraping.headless_mode', True):
            chrome_options.add_argument('--headless=new')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={ScrapingUtils.get_random_user_agent()}')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--lang=es-ES')

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })

            driver.implicitly_wait(2)
            driver.set_page_load_timeout(self.config.get('scraping.page_load_timeout', 30))

            logger.info("✅ Glassdoor WebDriver configurado")
            return driver

        except Exception as e:
            logger.error(f"Error configurando WebDriver: {str(e)}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """Recopila ofertas de Glassdoor."""
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        if location is None:
            location = "España"

        logger.info(f"Iniciando scraping de {self.platform_name}...")
        logger.warning(
            "⚠️  Glassdoor tiene protección anti-scraping. "
            "Considera usar la API oficial o aumentar delays."
        )

        self.clear_jobs()

        try:
            self.driver = self._setup_driver()

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

        finally:
            if self.driver:
                logger.debug("Cerrando Glassdoor WebDriver...")
                self.driver.quit()
                self.driver = None

        logger.info(f"Scraping completado. Total ofertas: {len(self.jobs)}")
        return self.jobs

    def _search_keyword(self, keyword: str, location: str) -> List[JobOffer]:
        """Busca ofertas para una palabra clave."""
        jobs = []
        page = 1
        max_pages = self.config.get('scraping.max_pages_per_session', 3)

        while page <= max_pages:
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            try:
                # Construir URL de búsqueda
                params = {
                    'sc.keyword': keyword,
                    'locT': 'N',
                    'locId': '115',  # España
                    'jobType': '',
                    'fromAge': '-1',
                    'minSalary': '0',
                    'includeNoSalaryJobs': 'true',
                    'radius': '100',
                    'cityId': '-1',
                    'minRating': '0.0',
                    'industryId': '-1',
                    'sgocId': '-1',
                    'seniorityType': '',
                    'companyId': '-1',
                    'employerSizes': '0',
                    'applicationType': '0',
                    'remoteWorkType': '0',
                    'page': str(page)
                }

                url = ScrapingUtils.build_search_url(self.JOBS_URL, params)
                logger.debug(f"Navegando a: {url}")

                self.driver.get(url)

                # Esperar a que carguen los resultados
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-test='jobListing']"))
                    )
                except TimeoutException:
                    logger.warning("Timeout esperando resultados")
                    break

                # Encontrar tarjetas de ofertas
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "li[data-test='jobListing']")

                if not job_cards:
                    logger.debug("No se encontraron más ofertas")
                    break

                logger.debug(f"Encontradas {len(job_cards)} ofertas en página {page}")

                for idx, card in enumerate(job_cards, 1):
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                            logger.info(f"✓ {len(jobs)}. {job.title} - {job.company}")

                        if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                            break

                    except Exception as e:
                        logger.warning(f"Error parseando oferta {idx}: {str(e)}")
                        continue

                page += 1
                self._sleep()

            except Exception as e:
                logger.error(f"Error en página {page}: {str(e)}")
                break

        return jobs

    def _parse_job_card(self, card) -> Optional[JobOffer]:
        """Extrae información de una tarjeta de oferta de Glassdoor."""
        try:
            # Título
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "a[data-test='job-link']")
                title = ScrapingUtils.clean_text(title_elem.text)
            except NoSuchElementException:
                return None

            # Empresa
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "[data-test='employer-name']")
                company = ScrapingUtils.clean_text(company_elem.text)
            except NoSuchElementException:
                company = "Desconocido"

            # Ubicación
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, "[data-test='emp-location']")
                location = ScrapingUtils.clean_text(location_elem.text)
            except NoSuchElementException:
                location = ""

            # URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a[data-test='job-link']")
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url
            except NoSuchElementException:
                pass

            # Descripción
            description = ""
            try:
                desc_elem = card.find_element(By.CLASS_NAME, "jobDescriptionContent")
                description = ScrapingUtils.clean_text(desc_elem.text)
            except NoSuchElementException:
                pass

            # Combinar título + descripción
            full_text = f"{title} {description}".strip()
            description = full_text if full_text else title

            # Salario
            salary_info = {'salary_min': None, 'salary_max': None, 'salary_currency': 'EUR'}
            try:
                salary_elem = card.find_element(By.CSS_SELECTOR, "[data-test='detailSalary']")
                salary_text = salary_elem.text
                salary_info = ScrapingUtils.extract_salary(salary_text)
            except NoSuchElementException:
                pass

            # Determinar tipo de ubicación
            work_location = WorkLocation.UNKNOWN
            location_lower = location.lower()
            if 'remot' in location_lower or 'teletrabajo' in location_lower:
                work_location = WorkLocation.REMOTE
            elif location:
                work_location = WorkLocation.ONSITE

            # Crear oferta con lazy loading
            job_offer = self._create_job_offer(
                title=title,
                company=company,
                url=job_url,
                description=description,
                location=location,
                work_location_type=work_location,
                technologies=[],  # Lazy loading
                skills=[],  # Lazy loading
                **salary_info
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando tarjeta de Glassdoor: {str(e)}")
            return None
