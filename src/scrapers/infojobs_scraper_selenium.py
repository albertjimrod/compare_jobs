"""
Scraper para InfoJobs usando Selenium.

InfoJobs es uno de los portales de empleo más populares en España.
Este scraper usa Selenium para evitar detección anti-scraping.
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


class InfojobsScraperSelenium(BaseScraper):
    """Scraper para InfoJobs usando Selenium."""

    BASE_URL = "https://www.infojobs.net"

    def __init__(self, config=None):
        """Inicializa el scraper de InfoJobs."""
        super().__init__(config)

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "InfoJobs scraper requiere Selenium. "
                "Instala con: pip install selenium webdriver-manager"
            )

        self.driver = None

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "InfoJobs"

    def _setup_driver(self):
        """Configura driver de Selenium para InfoJobs."""
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

            logger.info("✅ InfoJobs WebDriver configurado")
            return driver

        except Exception as e:
            logger.error(f"Error configurando WebDriver: {str(e)}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """Recopila ofertas de InfoJobs."""
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
                logger.debug("Cerrando InfoJobs WebDriver...")
                self.driver.quit()
                self.driver = None

        logger.info(f"Scraping completado. Total ofertas: {len(self.jobs)}")
        return self.jobs

    def _search_keyword(self, keyword: str, location: str) -> List[JobOffer]:
        """Busca ofertas para una palabra clave."""
        jobs = []
        page = 1
        max_pages = self.config.get('scraping.max_pages_per_session', 0)

        while True:
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            if max_pages > 0 and page > max_pages:
                logger.info(f"Alcanzado límite de {max_pages} páginas")
                break

            try:
                # Construir URL de búsqueda
                params = {
                    'keyword': keyword.replace(' ', '-'),
                    'page': str(page)
                }

                # InfoJobs usa URLs del tipo: /ofertas-trabajo/data-scientist.html?page=1
                search_url = f"{self.BASE_URL}/ofertas-trabajo/{keyword.replace(' ', '-')}.html"
                if page > 1:
                    search_url += f"?page={page}"

                logger.debug(f"Navegando a: {search_url}")

                self.driver.get(search_url)

                # Esperar a que la página cargue completamente (InfoJobs es MUY lenta)
                wait_time = 12 if page > 1 else 10
                logger.debug(f"Esperando {wait_time}s para carga de InfoJobs página {page}...")
                time.sleep(wait_time)

                # Scroll SUPER agresivo para cargar contenido dinámico (InfoJobs lazy loading)
                try:
                    for i in range(4):  # Repetir scroll 4 veces (InfoJobs es muy lenta)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                        time.sleep(1)
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    logger.debug("Scroll de InfoJobs completado")
                except Exception as e:
                    logger.debug(f"Error en scroll: {e}")

                # Buscar ofertas con múltiples selectores de InfoJobs
                job_cards = []
                selectors = [
                    "li.offercard",                    # Selector principal de InfoJobs
                    "article.offer-item",              # Artículos de ofertas
                    "li[class*='offer']",              # Li que contiene 'offer'
                    "div[class*='offer']",             # Div que contiene 'offer'
                    "article[class*='job']",           # Artículos de trabajos
                    "[data-offer-id]",                 # Elementos con ID de oferta
                    "li.js-offer",                     # Ofertas con clase js-offer
                ]

                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            job_cards = elements
                            logger.info(f"✓ Encontradas {len(job_cards)} ofertas con selector: {selector}")
                            break
                    except Exception:
                        continue

                if not job_cards:
                    logger.warning(f"No se encontraron ofertas en página {page}")
                    # Similar a Indeed - solo terminar si ya teníamos ofertas
                    if page > 1 and len(jobs) > 0:
                        logger.info("Fin de resultados alcanzado")
                        break
                    if page == 1:
                        break
                    page += 1
                    continue

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
        """Extrae información de una tarjeta de oferta de InfoJobs."""
        try:
            # Título
            title = ""
            title_selectors = [
                "h2.title",
                "h3.title",
                "a[class*='title']",
                ".tc_title"
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
                ".tc_company_name",
                "a[class*='company']",
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
                ".tc_locality",
                ".location",
                "span[class*='location']"
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
                ".tc_description",
                ".description",
                "div[class*='description']"
            ]

            for selector in desc_selectors:
                try:
                    desc_elem = card.find_element(By.CSS_SELECTOR, selector)
                    desc_text = ScrapingUtils.clean_text(desc_elem.text)
                    if desc_text and len(desc_text) > 20:
                        description = desc_text
                        break
                except NoSuchElementException:
                    continue

            # Fallback: usar texto completo
            if not description:
                try:
                    card_text = ScrapingUtils.clean_text(card.text)
                    card_text = card_text.replace(title, "").replace(company, "")
                    if len(card_text) > 50:
                        description = card_text
                except Exception:
                    pass

            full_text = f"{title} {description}".strip()
            description = full_text if full_text else title

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
                technologies=[],
                skills=[]
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando tarjeta de InfoJobs: {str(e)}")
            return None
