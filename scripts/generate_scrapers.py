#!/usr/bin/env python
"""
Script para generar stubs de scrapers para las plataformas faltantes.
Cada scraper generado es funcional pero requiere completar los selectores CSS.
"""

import os
from pathlib import Path

# Directorio de scrapers
SCRAPERS_DIR = Path(__file__).parent.parent / "src" / "scrapers"

# Plataformas a generar (nombre, URL base, URL de búsqueda, notas)
PLATFORMS = [
    ("Freelancer", "https://www.freelancer.es", "https://www.freelancer.es/jobs",
     "Plataforma freelance internacional. Requiere autenticación para ver ofertas completas."),

    ("Workana", "https://www.workana.com", "https://www.workana.com/jobs",
     "Plataforma freelance enfocada en Latinoamérica y España."),

    ("Malt", "https://www.malt.es", "https://www.malt.es/s",
     "Plataforma para freelancers europeos. Requiere autenticación."),

    ("Fiverr", "https://www.fiverr.com", "https://www.fiverr.com/search/gigs",
     "Plataforma de servicios freelance. Modelo inverso (vendedores publican servicios)."),

    ("SimplyHired", "https://www.simplyhired.es", "https://www.simplyhired.es/search",
     "Agregador de ofertas de empleo."),

    ("ZipRecruiter", "https://www.ziprecruiter.com", "https://www.ziprecruiter.com/candidate/search",
     "Plataforma de empleo estadounidense con presencia internacional."),

    ("CareerBuilder", "https://www.careerbuilder.com", "https://www.careerbuilder.com/jobs",
     "Plataforma de empleo establecida. Tiene API disponible."),

    ("Randstad", "https://www.randstad.es", "https://www.randstad.es/candidatos/ofertas-empleo/",
     "Empresa de recursos humanos. Tiene ofertas propias."),

    ("iTalenters", "https://www.italenters.com", "https://www.italenters.com/ofertas-empleo",
     "Plataforma española para perfiles tecnológicos."),

    ("MichaelPage", "https://www.michaelpage.es", "https://www.michaelpage.es/ofertas-trabajo",
     "Empresa de headhunting. Ofertas de alta cualificación."),

    ("Tecnoempleo", "https://www.tecnoempleo.com", "https://www.tecnoempleo.com/ofertas-empleo",
     "Portal español especializado en tecnología."),

    ("Hays", "https://www.hays.es", "https://www.hays.es/jobsearch",
     "Empresa internacional de recursos humanos."),

    ("Infoempleo", "https://www.infoempleo.com", "https://www.infoempleo.com/trabajo",
     "Portal español de empleo generalista."),
]


SCRAPER_TEMPLATE = '''"""
Scraper para {platform_name}.

{notes}

TODO: Completar la implementación:
1. Verificar las URLs (BASE_URL y JOBS_URL)
2. Ajustar selectores CSS en _parse_job_card()
3. Ajustar parámetros de búsqueda en _search_keyword()
4. Probar con modo headless=false para ver la estructura HTML
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


class {class_name}Scraper(BaseScraper):
    """Scraper para {platform_name}."""

    BASE_URL = "{base_url}"
    JOBS_URL = "{jobs_url}"

    def __init__(self, config=None):
        """Inicializa el scraper de {platform_name}."""
        super().__init__(config)

        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "{platform_name} scraper requiere Selenium. "
                "Instala con: pip install selenium webdriver-manager"
            )

        self.driver = None

    def _get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return "{platform_name}"

    def _setup_driver(self):
        """Configura driver de Selenium para {platform_name}."""
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
        chrome_options.add_argument(f'user-agent={{ScrapingUtils.get_random_user_agent()}}')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--lang=es-ES')

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {{
                'source': \'\'\'
                    Object.defineProperty(navigator, 'webdriver', {{
                        get: () => undefined
                    }});
                \'\'\'
            }})

            driver.implicitly_wait(2)
            driver.set_page_load_timeout(self.config.get('scraping.page_load_timeout', 30))

            logger.info("✅ {platform_name} WebDriver configurado")
            return driver

        except Exception as e:
            logger.error(f"Error configurando WebDriver: {{str(e)}}")
            raise

    def scrape_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> List[JobOffer]:
        """Recopila ofertas de {platform_name}."""
        if keywords is None:
            keywords = self.config.get('search_terms.keywords', ['data scientist'])

        if location is None:
            location = "España"

        logger.info(f"Iniciando scraping de {{self.platform_name}}...")
        self.clear_jobs()

        try:
            self.driver = self._setup_driver()

            for keyword in keywords:
                try:
                    logger.info(f"Buscando: '{{keyword}}' en {{location}}")
                    jobs = self._search_keyword(keyword, location)
                    self.jobs.extend(jobs)

                    if self.max_jobs > 0 and len(self.jobs) >= self.max_jobs:
                        logger.info(f"Alcanzado límite de {{self.max_jobs}} ofertas")
                        break

                except Exception as e:
                    logger.error(f"Error buscando '{{keyword}}': {{str(e)}}")
                    continue

        finally:
            if self.driver:
                logger.debug("Cerrando {platform_name} WebDriver...")
                self.driver.quit()
                self.driver = None

        logger.info(f"Scraping completado. Total ofertas: {{len(self.jobs)}}")
        return self.jobs

    def _search_keyword(self, keyword: str, location: str) -> List[JobOffer]:
        """Busca ofertas para una palabra clave."""
        jobs = []
        page = 0
        max_pages = self.config.get('scraping.max_pages_per_session', 5)

        while page < max_pages:
            if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                break

            try:
                # TODO: Ajustar parámetros según la plataforma
                params = {{
                    'q': keyword,
                    'location': location,
                    'start': str(page * 10)
                }}

                url = ScrapingUtils.build_search_url(self.JOBS_URL, params)
                logger.debug(f"Navegando a: {{url}}")

                self.driver.get(url)

                # TODO: Ajustar selector del contenedor de ofertas
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
                    )
                except TimeoutException:
                    logger.warning("Timeout esperando resultados")
                    break

                # TODO: Ajustar selector de las tarjetas
                job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card")

                if not job_cards:
                    logger.debug("No se encontraron más ofertas")
                    break

                logger.debug(f"Encontradas {{len(job_cards)}} ofertas en página {{page + 1}}")

                for idx, card in enumerate(job_cards, 1):
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                            logger.info(f"✓ {{len(jobs)}}. {{job.title}} - {{job.company}}")

                        if self.max_jobs > 0 and len(jobs) >= self.max_jobs:
                            break

                    except Exception as e:
                        logger.warning(f"Error parseando oferta {{idx}}: {{str(e)}}")
                        continue

                page += 1
                self._sleep()

            except Exception as e:
                logger.error(f"Error en página {{page}}: {{str(e)}}")
                break

        return jobs

    def _parse_job_card(self, card) -> Optional[JobOffer]:
        """
        Extrae información de una tarjeta de oferta de {platform_name}.

        TODO: Completar los selectores CSS apropiados para esta plataforma.
        """
        try:
            # TODO: Ajustar selectores según la plataforma
            title = ""
            company = "Desconocido"
            location = ""
            job_url = ""
            description = ""

            # Título (TODO: ajustar selector)
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.job-title, h3.title, a.job-link")
                title = ScrapingUtils.clean_text(title_elem.text)
            except NoSuchElementException:
                logger.debug("No se pudo extraer título")
                return None

            # Empresa (TODO: ajustar selector)
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, ".company-name, .employer, [data-company]")
                company = ScrapingUtils.clean_text(company_elem.text)
            except NoSuchElementException:
                pass

            # Ubicación (TODO: ajustar selector)
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, ".job-location, .location, [data-location]")
                location = ScrapingUtils.clean_text(location_elem.text)
            except NoSuchElementException:
                pass

            # URL (TODO: ajustar selector)
            try:
                link_elem = card.find_element(By.TAG_NAME, "a")
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url
            except NoSuchElementException:
                pass

            # Descripción (TODO: ajustar selectores)
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

            # Fallback: usar texto completo
            if not description:
                try:
                    card_text = ScrapingUtils.clean_text(card.text)
                    card_text = card_text.replace(title, "").replace(company, "")
                    if len(card_text) > 50:
                        description = card_text
                except Exception:
                    pass

            full_text = f"{{title}} {{description}}".strip()
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
            logger.warning(f"Error parseando tarjeta de {platform_name}: {{str(e)}}")
            return None
'''


def generate_scraper(platform_name, base_url, jobs_url, notes):
    """Genera un archivo de scraper para una plataforma."""
    class_name = platform_name.replace(" ", "")
    filename = f"{platform_name.lower().replace(' ', '_')}_scraper.py"
    filepath = SCRAPERS_DIR / filename

    content = SCRAPER_TEMPLATE.format(
        platform_name=platform_name,
        class_name=class_name,
        base_url=base_url,
        jobs_url=jobs_url,
        notes=notes
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Generado: {filename}")
    return filename, class_name


def main():
    """Genera todos los scrapers faltantes."""
    print("Generando scrapers stub para plataformas faltantes...\n")

    generated = []
    for platform_name, base_url, jobs_url, notes in PLATFORMS:
        try:
            filename, class_name = generate_scraper(platform_name, base_url, jobs_url, notes)
            generated.append((filename, class_name, platform_name))
        except Exception as e:
            print(f"✗ Error generando {platform_name}: {e}")

    print(f"\n✅ Generados {len(generated)} scrapers")

    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Completar los selectores CSS en cada scraper (busca 'TODO')")
    print("2. Registrar los scrapers en src/scrapers/scraper_factory.py")
    print("3. Probar cada scraper con headless_mode=false")
    print("\nPara registrar en scraper_factory.py, añade:\n")

    for filename, class_name, platform_name in generated:
        print(f"from .{filename[:-3]} import {class_name}Scraper")

    print("\nY en el diccionario _SCRAPERS:\n")
    for filename, class_name, platform_name in generated:
        key = platform_name.lower().replace(" ", "")
        print(f"'{key}': {class_name}Scraper,")


if __name__ == '__main__':
    main()
