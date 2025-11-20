#!/usr/bin/env python3
"""
Herramienta Interactiva para Completar Selectores CSS de Scrapers

Este script:
1. Abre el sitio web en modo visual
2. Te permite inspeccionar la página
3. Ingresas los selectores CSS que encuentres
4. Prueba los selectores en tiempo real
5. Actualiza automáticamente el archivo del scraper

Uso:
   python selector_helper.py michaelpage
   python selector_helper.py randstad
"""

import sys
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import undetected_chromedriver as uc
except ImportError:
    print("❌ Requiere selenium. Instala con:")
    print("   pip install selenium webdriver-manager undetected-chromedriver")
    sys.exit(1)


SCRAPER_CONFIGS = {
    'michaelpage': {
        'name': 'Michael Page',
        'url': 'https://www.michaelpage.es/ofertas-trabajo?searchterm=python&location=madrid',
        'file': 'src/scrapers/michaelpage_scraper.py'
    },
    'randstad': {
        'name': 'Randstad',
        'url': 'https://www.randstad.es/candidatos/ofertas-empleo/?query=python&location=madrid',
        'file': 'src/scrapers/randstad_scraper.py'
    },
    'hays': {
        'name': 'Hays',
        'url': 'https://www.hays.es/trabajos-ofertas-empleo?q=python&location=Madrid',
        'file': 'src/scrapers/hays_scraper.py'
    },
    'tecnoempleo': {
        'name': 'Tecnoempleo',
        'url': 'https://www.tecnoempleo.com/buscar-empleo.php?te=python&pr=Madrid',
        'file': 'src/scrapers/tecnoempleo_scraper.py'
    },
    'monster': {
        'name': 'Monster',
        'url': 'https://www.monster.es/trabajo/?q=python&where=Madrid',
        'file': 'src/scrapers/monster_scraper.py'
    },
    'infoempleo': {
        'name': 'InfoEmpleo',
        'url': 'https://www.infoempleo.com/trabajo/python/madrid/',
        'file': 'src/scrapers/infoempleo_scraper.py'
    },
    'simplyhired': {
        'name': 'SimplyHired',
        'url': 'https://www.simplyhired.es/search?q=python&l=Madrid',
        'file': 'src/scrapers/simplyhired_scraper.py'
    },
    'ziprecruiter': {
        'name': 'ZipRecruiter',
        'url': 'https://www.ziprecruiter.com/jobs-search?search=python&location=Madrid',
        'file': 'src/scrapers/ziprecruiter_scraper.py'
    },
    'glassdoor': {
        'name': 'Glassdoor',
        'url': 'https://www.glassdoor.es/Job/python-jobs-SRCH_KO0,6.htm',
        'file': 'src/scrapers/glassdoor_scraper.py'
    }
}


def setup_driver():
    """Configura driver visual para inspección."""
    print("🔧 Configurando navegador...")

    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')

    driver = uc.Chrome(options=options)
    return driver


def test_selector(driver, selector_type, selector_value):
    """Prueba un selector y retorna elementos encontrados."""
    try:
        if selector_type == 'css':
            elements = driver.find_elements(By.CSS_SELECTOR, selector_value)
        elif selector_type == 'class':
            elements = driver.find_elements(By.CLASS_NAME, selector_value)
        elif selector_type == 'id':
            elements = driver.find_elements(By.ID, selector_value)
        else:
            elements = driver.find_elements(By.CSS_SELECTOR, selector_value)

        return elements
    except Exception as e:
        print(f"   ❌ Error probando selector: {e}")
        return []


def interactive_selector_finder(platform):
    """Modo interactivo para encontrar selectores."""

    if platform not in SCRAPER_CONFIGS:
        print(f"❌ Plataforma '{platform}' no encontrada")
        print(f"Disponibles: {', '.join(SCRAPER_CONFIGS.keys())}")
        return

    config = SCRAPER_CONFIGS[platform]

    print("\n" + "="*70)
    print(f"🔍 SELECTOR HELPER - {config['name']}")
    print("="*70)
    print(f"\n📍 Abriendo: {config['url']}")
    print("\n⚠️  IMPORTANTE:")
    print("   1. Se abrirá el navegador en MODO VISUAL")
    print("   2. Usa F12 para abrir DevTools")
    print("   3. Click derecho > Inspeccionar elemento")
    print("   4. Busca el selector CSS en el HTML")
    print("\n💡 TIPS:")
    print("   - Clases: .nombre-clase o div.nombre-clase")
    print("   - IDs: #mi-id")
    print("   - Atributos: [data-test='value']")
    print("   - Combinados: div.card > h2.title")
    print("\n")

    driver = setup_driver()

    try:
        driver.get(config['url'])
        print("✅ Página cargada")
        time.sleep(3)

        selectors = {}

        # 1. Selector de tarjetas
        print("\n" + "-"*70)
        print("📋 PASO 1: Selector de TARJETAS de ofertas")
        print("-"*70)
        print("Busca el elemento HTML que contiene CADA oferta individual.")
        print("Ejemplos comunes: .job-card, .offer-item, article.job, .vacancy")
        print("\nPresiona ENTER para continuar...")
        input()

        while True:
            selector = input("\n🔎 Selector de tarjetas (ej: .job-card): ").strip()
            if not selector:
                continue

            elements = test_selector(driver, 'css', selector)
            count = len(elements)

            print(f"\n   ✓ Encontrados {count} elementos")

            if count > 0:
                print(f"\n   📄 Texto del primer elemento (primeros 200 caracteres):")
                print(f"   {elements[0].text[:200]}...")

                confirm = input(f"\n   ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    selectors['job_card'] = selector
                    break
            else:
                print("   ⚠️  No se encontraron elementos. Intenta otro selector.")

        # 2. Selector de título
        print("\n" + "-"*70)
        print("📋 PASO 2: Selector de TÍTULO dentro de la tarjeta")
        print("-"*70)
        print("Busca el elemento del TÍTULO del puesto de trabajo.")
        print("Ejemplos: h2.job-title, .title, h3.vacancy-title")
        print("\nPresiona ENTER para continuar...")
        input()

        while True:
            selector = input("\n🔎 Selector de título (ej: h2.title): ").strip()
            if not selector:
                continue

            # Probar dentro de la primera tarjeta
            first_card = test_selector(driver, 'css', selectors['job_card'])[0]
            try:
                title_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                title_text = title_elem.text

                print(f"\n   ✓ Título encontrado: {title_text}")

                confirm = input(f"\n   ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    selectors['title'] = selector
                    break
            except:
                print("   ❌ No se encontró título con ese selector")

        # 3. Selector de empresa
        print("\n" + "-"*70)
        print("📋 PASO 3: Selector de EMPRESA")
        print("-"*70)
        print("Busca el elemento del nombre de la EMPRESA.")
        print("Ejemplos: .company-name, span.employer, [data-company]")
        print("\nPresiona ENTER para continuar...")
        input()

        while True:
            selector = input("\n🔎 Selector de empresa (ej: .company): ").strip()
            if not selector:
                continue

            try:
                company_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                company_text = company_elem.text

                print(f"\n   ✓ Empresa encontrada: {company_text}")

                confirm = input(f"\n   ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    selectors['company'] = selector
                    break
            except:
                print("   ❌ No se encontró empresa con ese selector")

        # 4. Selector de ubicación
        print("\n" + "-"*70)
        print("📋 PASO 4: Selector de UBICACIÓN")
        print("-"*70)
        print("Busca el elemento de la UBICACIÓN/LOCALIZACIÓN.")
        print("Ejemplos: .location, span.city, [data-location]")
        print("\nPresiona ENTER para continuar...")
        input()

        while True:
            selector = input("\n🔎 Selector de ubicación (ej: .location): ").strip()
            if not selector:
                continue

            try:
                location_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                location_text = location_elem.text

                print(f"\n   ✓ Ubicación encontrada: {location_text}")

                confirm = input(f"\n   ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    selectors['location'] = selector
                    break
            except:
                print("   ❌ No se encontró ubicación con ese selector")

        # 5. Selector de URL
        print("\n" + "-"*70)
        print("📋 PASO 5: Selector de ENLACE (URL)")
        print("-"*70)
        print("Busca el elemento <a> que tiene el enlace a la oferta.")
        print("Ejemplos: a.job-link, h2 > a, .title a")
        print("\nPresiona ENTER para continuar...")
        input()

        while True:
            selector = input("\n🔎 Selector de enlace (ej: a.job-link): ").strip()
            if not selector:
                continue

            try:
                link_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                link_url = link_elem.get_attribute('href')

                print(f"\n   ✓ URL encontrada: {link_url[:80]}...")

                confirm = input(f"\n   ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    selectors['link'] = selector
                    break
            except:
                print("   ❌ No se encontró enlace con ese selector")

        # Resumen
        print("\n" + "="*70)
        print("✅ SELECTORES COMPLETADOS")
        print("="*70)
        for key, value in selectors.items():
            print(f"  • {key:15s}: {value}")

        # Guardar
        print("\n💾 Guardando selectores en el archivo del scraper...")
        update_scraper_file(config['file'], selectors)
        print("✅ Scraper actualizado exitosamente")

        print(f"\n🧪 Ahora puedes probar el scraper:")
        print(f"   python test_scraper_individual.py {platform} --max-jobs=5 --headless=false")

    finally:
        print("\n⏳ Cerrando navegador en 10 segundos...")
        time.sleep(10)
        driver.quit()


def update_scraper_file(file_path, selectors):
    """Actualiza el archivo del scraper con los selectores encontrados."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Reemplazar selectores
    replacements = {
        # Selector de tarjetas
        'WebDriverWait(self.driver, 10).until(\n                        EC.presence_of_element_located((By.CLASS_NAME, "job-card"))':
        f'WebDriverWait(self.driver, 10).until(\n                        EC.presence_of_element_located((By.CSS_SELECTOR, "{selectors["job_card"]}"))',

        'job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card")':
        f'job_cards = self.driver.find_elements(By.CSS_SELECTOR, "{selectors["job_card"]}")',

        # Selector de título
        'title_elem = card.find_element(By.CSS_SELECTOR, "h2.job-title, h3.title, a.job-link")':
        f'title_elem = card.find_element(By.CSS_SELECTOR, "{selectors["title"]}")',

        # Selector de empresa
        'company_elem = card.find_element(By.CSS_SELECTOR, ".company-name, .employer, [data-company]")':
        f'company_elem = card.find_element(By.CSS_SELECTOR, "{selectors["company"]}")',

        # Selector de ubicación
        'location_elem = card.find_element(By.CSS_SELECTOR, ".job-location, .location, [data-location]")':
        f'location_elem = card.find_element(By.CSS_SELECTOR, "{selectors["location"]}")',

        # Selector de enlace
        'link_elem = card.find_element(By.TAG_NAME, "a")':
        f'link_elem = card.find_element(By.CSS_SELECTOR, "{selectors["link"]}")'
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    if len(sys.argv) < 2:
        print("Uso: python selector_helper.py <platform>")
        print("\nPlataformas disponibles:")
        for key, val in SCRAPER_CONFIGS.items():
            print(f"  • {key:15s} - {val['name']}")
        print("\nEjemplo:")
        print("  python selector_helper.py michaelpage")
        sys.exit(1)

    platform = sys.argv[1].lower()
    interactive_selector_finder(platform)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")
        sys.exit(130)
