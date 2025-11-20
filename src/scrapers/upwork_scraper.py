"""
Scraper para Upwork.

IMPORTANTE: Upwork es una plataforma de freelance.
- Requiere autenticación para ver ofertas completas
- Tiene API oficial: https://developers.upwork.com/
- Protección anti-scraping fuerte

Recomendación: Usar la API oficial con credenciales OAuth.
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
from ..models.job_offer import JobOffer, WorkLocation, ContractType
from ..utils.scraping_utils import ScrapingUtils


class UpworkScraper(BaseScraper):
    """Scraper para Upwork (freelance platform)."""

    BASE_URL = "https://www.upwork.com"
    JOBS_URL = "https://www.upwork.com/nx/search/jobs"

    def __init__(self, config=None):
        """Inicializa el scraper de Upwork."""
        super().__init__(config)

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Upwork scraper requiere Selenium. "
                "Instala con: pip install selenium webdriver-manager"
            )

        self.driver = None

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "Upwork"

    def _setup_driver(self):
        """Configura driver de Selenium para Upwork."""
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

            logger.info("✅ Upwork WebDriver configurado")
            return driver

        except Exception as e:
            logger.error(f"Error configurando WebDriver: {str(e)}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """Recopila ofertas de Upwork."""
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        logger.info(f"Iniciando scraping de {self.platform_name}...")
        logger.warning(
            "⚠️  Upwork requiere autenticación para acceso completo. "
            "Considera usar la API oficial: https://developers.upwork.com/"
        )

        self.clear_jobs()

        try:
            self.driver = self._setup_driver()

            for keyword in keywords:
                try:
                    logger.info(f"Buscando: '{keyword}'")
                    jobs = self._search_keyword(keyword)
                    self.jobs.extend(jobs)

                    if self.max_jobs > 0 and len(self.jobs) >= self.max_jobs:
                        logger.info(f"Alcanzado límite de {self.max_jobs} ofertas")
                        break

                except Exception as e:
                    logger.error(f"Error buscando '{keyword}': {str(e)}")
                    continue

        finally:
            if self.driver:
                logger.debug("Cerrando Upwork WebDriver...")
                self.driver.quit()
                self.driver = None

        logger.info(f"Scraping completado. Total ofertas: {len(self.jobs)}")
        return self.jobs

    def _search_keyword(self, keyword: str) -> List[JobOffer]:
        """Busca ofertas para una palabra clave."""
        jobs = []
        max_pages = self.config.get('scraping.max_pages_per_session', 3)

        try:
            # Construir URL de búsqueda
            params = {
                'q': keyword,
                'sort': 'recency'
            }

            url = ScrapingUtils.build_search_url(self.JOBS_URL, params)
            logger.debug(f"Navegando a: {url}")

            self.driver.get(url)

            # Esperar a que carguen los resultados
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-test='job-tile']"))
                )
            except TimeoutException:
                logger.warning("Timeout esperando resultados")
                return jobs

            # Scroll para cargar más ofertas (Upwork usa infinite scroll)
            for _ in range(max_pages):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Encontrar tarjetas de ofertas
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "article[data-test='job-tile']")

            if not job_cards:
                logger.debug("No se encontraron ofertas")
                return jobs

            logger.debug(f"Encontradas {len(job_cards)} ofertas")

            for idx, card in enumerate(job_cards, 1):
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                        logger.info(f"✓ {len(jobs)}. {job.title}")

                    if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                        break

                except Exception as e:
                    logger.warning(f"Error parseando oferta {idx}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")

        return jobs

    def _parse_job_card(self, card) -> Optional[JobOffer]:
        """Extrae información de una tarjeta de oferta de Upwork."""
        try:
            # Título
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2[class*='job-title']")
                title = ScrapingUtils.clean_text(title_elem.text)
            except NoSuchElementException:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "h3")
                    title = ScrapingUtils.clean_text(title_elem.text)
                except NoSuchElementException:
                    return None

            # En Upwork, el "company" es el cliente (generalmente anónimo hasta contratar)
            company = "Cliente de Upwork"

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
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, "[data-test='job-description']")
                description = ScrapingUtils.clean_text(desc_elem.text)
            except NoSuchElementException:
                pass

            # Combinar título + descripción
            full_text = f"{title} {description}".strip()
            description = full_text if full_text else title

            # Budget/Presupuesto
            salary_info = {'salary_min': None, 'salary_max': None, 'salary_currency': 'USD'}
            try:
                budget_elem = card.find_element(By.CSS_SELECTOR, "[data-test='budget']")
                budget_text = budget_elem.text
                salary_info = ScrapingUtils.extract_salary(budget_text)
            except NoSuchElementException:
                pass

            # Skills/Tecnologías (Upwork las muestra como tags)
            tech_list = []
            try:
                skill_elems = card.find_elements(By.CSS_SELECTOR, "[data-test='token']")
                tech_list = [ScrapingUtils.clean_text(elem.text) for elem in skill_elems[:10]]
            except NoSuchElementException:
                pass

            # Crear oferta (Upwork es siempre remote/freelance)
            job_offer = self._create_job_offer(
                title=title,
                company=company,
                url=job_url,
                description=description,
                location="Remote",
                work_location_type=WorkLocation.REMOTE,
                contract_type=ContractType.FREELANCE,
                technologies=tech_list if tech_list else [],  # Upwork proporciona skills directamente
                skills=[]
            )

            return job_offer

        except Exception as e:
            logger.warning(f"Error parseando tarjeta de Upwork: {str(e)}")
            return None
