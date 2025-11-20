#!/usr/bin/env python3
"""
Diagnóstico detallado de Indeed - Captura errores y estado del scraper.
"""

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from src.utils.config_loader import ConfigLoader
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    diag_file = "diagnostico_detallado.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    log("DIAGNÓSTICO DETALLADO DE INDEED")
    log("=" * 60)
    log("")

    # Test 1: Selenium disponible
    log("TEST 1: Verificando Selenium...")
    try:
        from selenium import webdriver
        log("✅ Selenium instalado")
    except ImportError as e:
        log(f"❌ Selenium NO disponible: {e}")
        with open(diag_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        sys.exit(1)

    # Test 2: Crear driver
    log("\nTEST 2: Inicializando Chrome WebDriver...")
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log("✅ WebDriver inicializado correctamente")
    except Exception as e:
        log(f"❌ Error inicializando WebDriver: {e}")
        with open(diag_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        sys.exit(1)

    # Test 3: Cargar página
    log("\nTEST 3: Cargando página de Indeed...")
    url = "https://es.indeed.com/jobs?q=data+scientist&l=España&start=0"
    log(f"URL: {url}")

    try:
        driver.get(url)
        time.sleep(6)

        page_title = driver.title
        log(f"✅ Página cargada: '{page_title}'")

        # Verificar bloqueo
        if "momento" in page_title.lower() or "wait" in page_title.lower():
            log("⚠️  DETECTADO BLOQUEO CLOUDFLARE")
        else:
            log("✅ No hay bloqueo detectado")

    except Exception as e:
        log(f"❌ Error cargando página: {e}")
        driver.quit()
        with open(diag_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        sys.exit(1)

    # Test 4: Buscar ofertas con diferentes selectores
    log("\nTEST 4: Buscando ofertas con selectores CSS...")
    selectors = [
        "div.job_seen_beacon",
        "div[data-jk]",
        "td.resultContent",
        "div.cardOutline",
        "div.slider_item",
        "div[class*='job_']",
    ]

    best_selector = None
    max_found = 0

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            count = len(elements)
            log(f"  {selector}: {count} elementos")
            if count > max_found:
                max_found = count
                best_selector = selector
        except Exception as e:
            log(f"  {selector}: ERROR - {e}")

    log("")
    if max_found > 0:
        log(f"✅ MEJOR SELECTOR: {best_selector} ({max_found} ofertas)")
    else:
        log("❌ NO SE ENCONTRARON OFERTAS CON NINGÚN SELECTOR")

    # Test 5: Extraer datos de la primera oferta
    if max_found > 0:
        log("\nTEST 5: Extrayendo datos de primera oferta...")
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, best_selector)
            first_card = cards[0]

            # Intentar extraer título
            try:
                title_elem = first_card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                title = title_elem.text
                log(f"  Título: {title}")
            except:
                log("  ❌ No se pudo extraer título")

            # Intentar extraer empresa
            try:
                company_elem = first_card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
                company = company_elem.text
                log(f"  Empresa: {company}")
            except:
                log("  ❌ No se pudo extraer empresa")

            log("✅ Extracción de datos funciona")

        except Exception as e:
            log(f"❌ Error extrayendo datos: {e}")

    # Test 6: Verificar segunda página
    log("\nTEST 6: Verificando paginación (página 2)...")
    try:
        url_page2 = "https://es.indeed.com/jobs?q=data+scientist&l=España&start=10"
        driver.get(url_page2)
        time.sleep(5)

        elements = driver.find_elements(By.CSS_SELECTOR, best_selector if best_selector else "div.job_seen_beacon")
        count = len(elements)
        log(f"✅ Página 2: {count} ofertas encontradas")

        if count == 0:
            log("⚠️  Página 2 vacía - puede ser fin de resultados")

    except Exception as e:
        log(f"❌ Error en página 2: {e}")

    # Cerrar driver
    driver.quit()

    log("")
    log("=" * 60)
    log(f"Timestamp: {datetime.now()}")
    log("")
    log("RESUMEN:")
    if max_found > 0:
        log(f"✅ Scraper puede encontrar ofertas ({max_found} en página 1)")
        log(f"✅ Mejor selector: {best_selector}")
    else:
        log("❌ Scraper NO puede encontrar ofertas")
        log("   Posibles causas:")
        log("   - Indeed cambió su estructura HTML")
        log("   - Bloqueo de Cloudflare activo")
        log("   - Selectores desactualizados")

    # Guardar diagnóstico
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Diagnóstico guardado en: {diag_file}")
