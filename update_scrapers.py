#!/usr/bin/env python3
"""
Script para actualizar scrapers con selectores CSS robustos automáticamente.

Actualiza los scrapers con múltiples selectores fallback genéricos.
"""

import re
from pathlib import Path

# Selectores robustos para tarjetas de ofertas
JOB_CARDS_SELECTORS = """                # Esperar carga con múltiples selectores posibles
                selectors_to_try = [
                    (By.CSS_SELECTOR, "article.job"),
                    (By.CSS_SELECTOR, "div.job-item"),
                    (By.CSS_SELECTOR, ".job-card"),
                    (By.CSS_SELECTOR, "[data-job-id]"),
                    (By.CSS_SELECTOR, "div[class*='job']"),
                    (By.CSS_SELECTOR, "li.search-result"),
                    (By.CSS_SELECTOR, "div.result"),
                ]

                job_cards = []
                for by_type, selector in selectors_to_try:
                    try:
                        WebDriverWait(self.driver, 8).until(
                            EC.presence_of_element_located((by_type, selector))
                        )
                        job_cards = self.driver.find_elements(by_type, selector)
                        if len(job_cards) > 2:  # Al menos 3 ofertas
                            logger.debug(f"✓ Usando selector: {selector} ({len(job_cards)} ofertas)")
                            break
                        else:
                            job_cards = []  # Falso positivo, seguir buscando
                    except TimeoutException:
                        continue

                if not job_cards:
                    logger.warning("No se encontraron ofertas con ningún selector")
                    break"""

# Selectores robustos para campos de la tarjeta
PARSE_JOB_CARD_SELECTORS = """            # Título - múltiples selectores
            title_selectors = [
                "h2.job-title", "h3.title", "h2", "h3", "a.job-link",
                ".job-title", "[data-job-title]", "h2 a", "h3 a"
            ]
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = ScrapingUtils.clean_text(title_elem.text)
                    if title and len(title) > 3:
                        break
                except NoSuchElementException:
                    continue

            if not title:
                logger.debug("No se pudo extraer título")
                return None

            # Empresa - múltiples selectores
            company_selectors = [
                ".company-name", ".employer", "[data-company]", ".company",
                "span.company", "div.company", "[class*='company']"
            ]
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    company_text = ScrapingUtils.clean_text(company_elem.text)
                    if company_text and len(company_text) > 1:
                        company = company_text
                        break
                except NoSuchElementException:
                    continue

            # Ubicación - múltiples selectores
            location_selectors = [
                ".job-location", ".location", "[data-location]", ".city",
                "span.location", "div.location", "[class*='location']"
            ]
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location_text = ScrapingUtils.clean_text(location_elem.text)
                    if location_text and len(location_text) > 1:
                        location = location_text
                        break
                except NoSuchElementException:
                    continue

            # URL
            try:
                link_elem = card.find_element(By.TAG_NAME, "a")
                job_url = link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = self.BASE_URL + job_url
            except NoSuchElementException:
                pass"""

SCRAPERS_TO_UPDATE = [
    'randstad_scraper.py',
    'hays_scraper.py',
    'tecnoempleo_scraper.py',
    'monster_scraper.py',
    'infoempleo_scraper.py',
    'simplyhired_scraper.py',
    'ziprecruiter_scraper.py',
    'glassdoor_scraper.py',
]


def update_scraper(file_path):
    """Actualiza un scraper con selectores robustos."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Patrón para encontrar el bloque de búsqueda de tarjetas
    pattern_cards = r'(# TODO: Ajustar selector del contenedor de ofertas.*?job_cards = self\.driver\.find_elements\(By\.CLASS_NAME, "job-card"\))'

    if re.search(pattern_cards, content, re.DOTALL):
        content = re.sub(pattern_cards, JOB_CARDS_SELECTORS, content, flags=re.DOTALL)
        print(f"   ✓ Actualizado selector de tarjetas")
    else:
        print(f"   ⚠️  No se encontró patrón de tarjetas")

    # Patrón para encontrar el bloque de parsing de campos
    pattern_parse = r'(# Título \(TODO: ajustar selector\).*?except NoSuchElementException:\s+pass)'

    if re.search(pattern_parse, content, re.DOTALL):
        content = re.sub(pattern_parse, PARSE_JOB_CARD_SELECTORS, content, flags=re.DOTALL)
        print(f"   ✓ Actualizado parsing de campos")
    else:
        print(f"   ⚠️  No se encontró patrón de parsing")

    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return content


def main():
    base_dir = Path('src/scrapers')

    print("="*70)
    print("🔧 ACTUALIZANDO SCRAPERS CON SELECTORES ROBUSTOS")
    print("="*70)
    print()

    updated = []
    errors = []

    for scraper_file in SCRAPERS_TO_UPDATE:
        file_path = base_dir / scraper_file
        scraper_name = scraper_file.replace('_scraper.py', '')

        print(f"📝 {scraper_name.upper()}...")

        if not file_path.exists():
            print(f"   ❌ Archivo no encontrado: {file_path}")
            errors.append(scraper_name)
            continue

        try:
            update_scraper(file_path)
            updated.append(scraper_name)
            print(f"   ✅ Completado\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            errors.append(scraper_name)

    # Resumen
    print("="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Actualizados: {len(updated)}")
    for name in updated:
        print(f"   • {name}")

    if errors:
        print(f"\n❌ Con errores: {len(errors)}")
        for name in errors:
            print(f"   • {name}")

    print("\n🧪 Ahora puedes probar los scrapers:")
    print("   python test_scraper_individual.py randstad --max-jobs=5 --headless=false")


if __name__ == "__main__":
    main()
