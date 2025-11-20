"""
PLANTILLA PARA CREAR NUEVOS SCRAPERS

Esta plantilla proporciona la estructura básica para implementar
un scraper para cualquier plataforma de empleo.

INSTRUCCIONES PARA USAR ESTA PLANTILLA:

1. Copiar este archivo y renombrarlo a: {plataforma}_scraper.py
2. Reemplazar "PLATFORM_NAME" con el nombre de la plataforma
3. Actualizar BASE_URL y JOBS_URL con las URLs correctas
4. Completar los selectores CSS en _parse_job_card()
5. Ajustar la lógica de paginación en _search_keyword()
6. Registrar el scraper en scraper_factory.py

TIPS:

- Usa herramientas de desarrollo del navegador (F12) para encontrar selectores CSS
- Prueba los selectores en la consola: document.querySelector('.selector')
- Usa delays generosos para evitar bloqueos
- Considera usar la API oficial si está disponible
- Lee la documentación de la plataforma sobre scraping/términos de servicio

EJEMPLO DE USO:

    from src.scrapers.{platform}_scraper import {Platform}Scraper

    scraper = {Platform}Scraper(config)
    jobs = scraper.scrape_jobs(keywords=['python developer'])
    print(f"Encontradas {len(jobs)} ofertas")
"""

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


class TemplateplatformScraper(BaseScraper):
    """
    Scraper para PLATFORM_NAME.

    TODO: Completar la implementación siguiendo los TODOs
    """

    # TODO: Actualizar con las URLs correctas de la plataforma
    BASE_URL = "https://www.example.com"
    JOBS_URL = "https://www.example.com/jobs"

    def __init__(self, config=None):
        """Inicializa el scraper."""
        super().__init__(config)

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Este scraper requiere Selenium. "
                "Instala con: pip install selenium webdriver-manager"
            )

        self.driver = None

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        # TODO: Cambiar "PLATFORM_NAME" por el nombre real
        return "PLATFORM_NAME"

    def _setup_driver(self):
        """Configura driver de Selenium."""
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        chrome_options = Options()

        if self.config.get('scraping.headless_mode', True):
            chrome_options.add_argument('--headless=new')

        # Opciones anti-detección
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

            logger.info(f"✅ {self._get_platform_name()} WebDriver configurado")
            return driver

        except Exception as e:
            logger.error(f"Error configurando WebDriver: {str(e)}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """Recopila ofertas de trabajo."""
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
                logger.debug(f"Cerrando {self.platform_name} WebDriver...")
                self.driver.quit()
                self.driver = None

        logger.info(f"Scraping completado. Total ofertas: {len(self.jobs)}")
        return self.jobs

    def _search_keyword(self, keyword: str, location: str) -> List[JobOffer]:
        """
        Busca ofertas para una palabra clave.

        TODO: Ajustar la lógica de paginación según la plataforma:
        - Algunas usan ?page=N
        - Otras usan ?start=N
        - Algunas usan infinite scroll
        """
        jobs = []
        page = 0
        max_pages = self.config.get('scraping.max_pages_per_session', 5)

        while page < max_pages:
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            try:
                # TODO: Ajustar los parámetros según la plataforma
                params = {
                    'q': keyword,  # O 'keywords', 'search', etc.
                    'location': location,  # O 'l', 'where', 'loc', etc.
                    'start': str(page * 10)  # O 'page', 'offset', etc.
                }

                url = ScrapingUtils.build_search_url(self.JOBS_URL, params)
                logger.debug(f"Navegando a: {url}")

                self.driver.get(url)

                # TODO: Ajustar el selector del contenedor de ofertas
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
                    )
                except TimeoutException:
                    logger.warning("Timeout esperando resultados")
                    break

                # TODO: Ajustar el selector de las tarjetas de ofertas
                # Ejemplos comunes:
                # - By.CLASS_NAME, "job-card"
                # - By.CSS_SELECTOR, "div[data-job-id]"
                # - By.CSS_SELECTOR, "article.job"
                job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card")

                if not job_cards:
                    logger.debug("No se encontraron más ofertas")
                    break

                logger.debug(f"Encontradas {len(job_cards)} ofertas en página {page + 1}")

                for idx, card in enumerate(job_cards, 1):
                    try:
                        logger.debug(f"📝 Parseando oferta {idx}/{len(job_cards)}...")
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
        """
        Extrae información de una tarjeta de oferta.

        TODO: Actualizar los selectores CSS según la plataforma.

        CÓMO ENCONTRAR SELECTORES:
        1. Abre la página de búsqueda en el navegador
        2. Presiona F12 (DevTools)
        3. Click derecho en un elemento -> Inspeccionar
        4. Copia el selector CSS o la clase
        5. Prueba en consola: document.querySelector('.tu-selector')
        """
        try:
            # TODO: Ajustar selector del título
            # Ejemplos comunes:
            # - By.CLASS_NAME, "job-title"
            # - By.CSS_SELECTOR, "h2.title"
            # - By.CSS_SELECTOR, "a[data-job-title]"
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.job-title")
                title = ScrapingUtils.clean_text(title_elem.text)
            except NoSuchElementException:
                logger.debug("No se pudo extraer título")
                return None

            # TODO: Ajustar selector de la empresa
            try:
                company_elem = card.find_element(By.CLASS_NAME, "company-name")
                company = ScrapingUtils.clean_text(company_elem.text)
            except NoSuchElementException:
                company = "Desconocido"

            # TODO: Ajustar selector de la ubicación
            try:
                location_elem = card.find_element(By.CLASS_NAME, "job-location")
                location = ScrapingUtils.clean_text(location_elem.text)
            except NoSuchElementException:
                location = ""

            # TODO: Ajustar selector de la URL
            job_url = ""
            try:
                link_elem = card.find_element(By.TAG_NAME, "a")
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url
            except NoSuchElementException:
                pass

            # TODO: Ajustar selector de la descripción
            description = ""
            description_selectors = [
                (By.CLASS_NAME, "job-description"),
                (By.CLASS_NAME, "job-snippet"),
                (By.CSS_SELECTOR, "div.description"),
            ]

            for selector_type, selector_value in description_selectors:
                try:
                    desc_elem = card.find_element(selector_type, selector_value)
                    desc_text = ScrapingUtils.clean_text(desc_elem.text)
                    if desc_text and len(desc_text) > 20:
                        description = desc_text
                        break
                except NoSuchElementException:
                    continue

            # Fallback: usar todo el texto de la tarjeta
            if not description:
                try:
                    card_text = ScrapingUtils.clean_text(card.text)
                    card_text = card_text.replace(title, "").replace(company, "")
                    if len(card_text) > 50:
                        description = card_text
                except Exception:
                    pass

            # Combinar título + descripción
            full_text = f"{title} {description}".strip()
            description = full_text if full_text else title

            # TODO: Ajustar selector del salario (si aplica)
            salary_info = {'salary_min': None, 'salary_max': None, 'salary_currency': 'EUR'}
            try:
                salary_elem = card.find_element(By.CLASS_NAME, "salary")
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

            # Crear oferta con lazy loading de tecnologías
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
            logger.warning(f"Error parseando tarjeta: {str(e)}")
            return None
