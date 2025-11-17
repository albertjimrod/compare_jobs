"""
Scraper para Indeed usando Selenium.

Este scraper utiliza Selenium WebDriver para simular un navegador real,
lo que permite evitar la mayoría de las protecciones anti-scraping.

Ventajas sobre el scraper basado en requests:
- Ejecuta JavaScript como un navegador real
- Maneja cookies y sesiones automáticamente
- Más difícil de detectar como bot
- Puede interactuar con elementos dinámicos

Requisitos:
- selenium
- webdriver-manager (para gestionar drivers automáticamente)
"""

import time
import random
from typing import List, Optional
from loguru import logger

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning(
        "Selenium no está disponible. Instala con: pip install selenium webdriver-manager"
    )

from .base_scraper import BaseScraper
from ..models.job_offer import JobOffer, ContractType, WorkLocation
from ..utils.scraping_utils import ScrapingUtils


class IndeedScraperSelenium(BaseScraper):
    """Scraper para Indeed usando Selenium WebDriver."""

    BASE_URL = "https://es.indeed.com"

    def __init__(self, config=None):
        """Inicializa el scraper de Indeed con Selenium."""
        super().__init__(config)
        self.driver = None

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium no está instalado. Ejecuta: pip install selenium webdriver-manager"
            )

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "Indeed (Selenium)"

    def _setup_driver(self):
        """Configura y retorna un driver de Selenium con opciones anti-detección."""
        logger.info("Configurando Selenium WebDriver...")

        chrome_options = Options()

        # Modo headless (sin interfaz gráfica) si está configurado
        if self.config.get('scraping.headless_mode', True):
            chrome_options.add_argument('--headless=new')
            logger.debug("Modo headless activado")
        else:
            logger.debug("Modo headless desactivado - se abrirá ventana del navegador")

        # Opciones para evadir detección
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Opciones de rendimiento
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        # User agent realista
        user_agent = ScrapingUtils.get_random_user_agent()
        chrome_options.add_argument(f'user-agent={user_agent}')

        # Tamaño de ventana
        chrome_options.add_argument('--window-size=1920,1080')

        # Idioma
        chrome_options.add_argument('--lang=es-ES')

        try:
            # Usar webdriver-manager para gestionar el driver automáticamente
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Script para ocultar propiedades de webdriver
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })

            # Timeouts
            driver.implicitly_wait(self.config.get('scraping.page_load_timeout', 30))
            driver.set_page_load_timeout(self.config.get('scraping.page_load_timeout', 30))

            logger.info("✅ Selenium WebDriver configurado correctamente")
            return driver

        except Exception as e:
            logger.error(f"Error configurando Selenium WebDriver: {str(e)}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """
        Recopila ofertas de trabajo de Indeed usando Selenium.

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

        try:
            # Configurar driver
            self.driver = self._setup_driver()

            # Scrapear para cada keyword
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
            # Siempre cerrar el driver
            if self.driver:
                logger.debug("Cerrando Selenium WebDriver...")
                self.driver.quit()
                self.driver = None

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

                logger.debug(f"Navegando a: {url}")

                # Navegar a la página
                self.driver.get(url)

                # Esperar a que carguen los resultados
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
                    )
                except TimeoutException:
                    logger.warning("Timeout esperando resultados de búsqueda")
                    break

                # Scroll aleatorio para parecer más humano
                self._random_scroll()

                # Encontrar ofertas en la página
                job_cards = self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

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
        Extrae información de una tarjeta de oferta usando Selenium.

        Args:
            card: WebElement de Selenium de la tarjeta

        Returns:
            Objeto JobOffer o None si falla
        """
        try:
            # Título
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                title = ScrapingUtils.clean_text(title_elem.text)
            except NoSuchElementException:
                return None

            # Empresa
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
                company = ScrapingUtils.clean_text(company_elem.text)
            except NoSuchElementException:
                company = "Desconocido"

            # Ubicación
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']")
                location = ScrapingUtils.clean_text(location_elem.text)
            except NoSuchElementException:
                location = ""

            # URL
            job_url = ""
            job_id = None
            try:
                link_elem = title_elem.find_element(By.TAG_NAME, "a")
                job_url = link_elem.get_attribute('href')
                # Extraer ID del trabajo
                if job_url and 'jk=' in job_url:
                    job_id = job_url.split('jk=')[1].split('&')[0]
            except NoSuchElementException:
                pass

            # Descripción (snippet)
            try:
                desc_elem = card.find_element(By.CLASS_NAME, "job-snippet")
                description = ScrapingUtils.clean_text(desc_elem.text)
            except NoSuchElementException:
                description = ""

            # Salario (si está disponible)
            salary_info = {'salary_min': None, 'salary_max': None, 'salary_currency': 'EUR'}
            try:
                salary_elem = card.find_element(By.CLASS_NAME, "salary-snippet")
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

    def _random_scroll(self):
        """Realiza scroll aleatorio en la página para parecer más humano."""
        try:
            # Scroll aleatorio
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 0.8))

            # A veces scroll hacia arriba
            if random.random() < 0.3:
                scroll_up = random.randint(100, 300)
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_up});")
                time.sleep(random.uniform(0.2, 0.5))

        except Exception as e:
            logger.debug(f"Error en scroll aleatorio: {str(e)}")
