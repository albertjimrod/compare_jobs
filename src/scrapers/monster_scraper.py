"""
Scraper para Monster.

Monster es una plataforma de empleo internacional con presencia en España.
Tiene protección anti-scraping moderada.
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


class MonsterScraper(BaseScraper):
    """Scraper para Monster usando Selenium."""

    BASE_URL = "https://www.monster.es"
    JOBS_URL = "https://www.monster.es/empleos/buscar"

    def __init__(self, config=None):
        """Inicializa el scraper de Monster."""
        super().__init__(config)

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Monster scraper requiere Selenium. "
                "Instala con: pip install selenium webdriver-manager"
            )

        self.driver = None

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "Monster"

    def _setup_driver(self):
        """Configura driver de Selenium para Monster."""
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

            logger.info("✅ Monster WebDriver configurado")
            return driver

        except Exception as e:
            logger.error(f"Error configurando WebDriver: {str(e)}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """Recopila ofertas de Monster."""
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        if location is None:
            location = "España"

        logger.info(f"Iniciando scraping de {self.platform_name}...")

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
                logger.debug("Cerrando Monster WebDriver...")
                self.driver.quit()
                self.driver = None

        logger.info(f"Scraping completado. Total ofertas: {len(self.jobs)}")
        return self.jobs

    def _search_keyword(self, keyword: str, location: str) -> List[JobOffer]:
        """Busca ofertas para una palabra clave."""
        jobs = []
        page = 1
        max_pages = self.config.get('scraping.max_pages_per_session', 5)

        while page <= max_pages:
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            try:
                # Construir URL de búsqueda
                params = {
                    'q': keyword,
                    'where': location,
                    'page': str(page)
                }

                url = ScrapingUtils.build_search_url(self.JOBS_URL, params)
                logger.debug(f"Navegando a: {url}")

                self.driver.get(url)

                # Esperar a que carguen los resultados
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='JobCard']"))
                    )
                except TimeoutException:
                    logger.warning("Timeout esperando resultados")
                    break

                # Encontrar tarjetas de ofertas - Monster usa varios selectores posibles
                job_cards = []
                selectors = [
                    "div[class*='JobCard']",
                    "article[class*='job']",
                    "div.card-content"
                ]

                for selector in selectors:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break

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
        """Extrae información de una tarjeta de oferta de Monster."""
        try:
            # Título - probar varios selectores
            title = ""
            title_selectors = [
                "h2[class*='title']",
                "h3[class*='title']",
                "a[class*='title']",
                ".job-title"
            ]

            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = ScrapingUtils.clean_text(title_elem.text)
                    if title:
                        break
                except NoSuchElementException:
                    continue

            if not title:
                return None

            # Empresa
            company = "Desconocido"
            company_selectors = [
                "[class*='company']",
                "[data-test-id='svx-jobcard-company-name']",
                ".company-name"
            ]

            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    company = ScrapingUtils.clean_text(company_elem.text)
                    if company:
                        break
                except NoSuchElementException:
                    continue

            # Ubicación
            location = ""
            location_selectors = [
                "[class*='location']",
                "[data-test-id='job-location']",
                ".job-location"
            ]

            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = ScrapingUtils.clean_text(location_elem.text)
                    if location:
                        break
                except NoSuchElementException:
                    continue

            # URL
            job_url = ""
            try:
                link_elem = card.find_element(By.TAG_NAME, "a")
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url
            except NoSuchElementException:
                pass

            # Descripción
            description = ""
            desc_selectors = [
                "[class*='description']",
                "[class*='summary']",
                ".job-description"
            ]

            for selector in desc_selectors:
                try:
                    desc_elem = card.find_element(By.CSS_SELECTOR, selector)
                    description = ScrapingUtils.clean_text(desc_elem.text)
                    if description and len(description) > 20:
                        break
                except NoSuchElementException:
                    continue

            # Combinar título + descripción
            full_text = f"{title} {description}".strip()
            description = full_text if full_text else title

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
                skills=[]  # Lazy loading
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando tarjeta de Monster: {str(e)}")
            return None
