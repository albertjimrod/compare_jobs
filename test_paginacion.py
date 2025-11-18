#!/usr/bin/env python3
"""
Test de paginación - Verifica diferentes métodos de navegar páginas en Indeed.
"""

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    diag_file = "test_paginacion.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    log("TEST DE PAGINACIÓN - INDEED ESPAÑA")
    log("=" * 60)

    # Configurar driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Test diferentes URLs de paginación
    urls_to_test = [
        ("Página 1 (sin start)", "https://es.indeed.com/jobs?q=data+scientist&l=España"),
        ("Página 1 (start=0)", "https://es.indeed.com/jobs?q=data+scientist&l=España&start=0"),
        ("Página 2 (start=10)", "https://es.indeed.com/jobs?q=data+scientist&l=España&start=10"),
        ("Página 3 (start=20)", "https://es.indeed.com/jobs?q=data+scientist&l=España&start=20"),
        ("Página 10 (start=90)", "https://es.indeed.com/jobs?q=data+scientist&l=España&start=90"),
    ]

    for name, url in urls_to_test:
        log(f"\n{name}")
        log(f"URL: {url}")

        try:
            driver.get(url)
            time.sleep(6)  # Esperar carga

            # Verificar título
            title = driver.title
            log(f"  Título: {title}")

            # Verificar bloqueo
            if "momento" in title.lower():
                log("  ⚠️  BLOQUEADO por Cloudflare")
                continue

            # Contar ofertas con mejor selector
            selector = "div[class*='job_']"
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                count = len(elements)
                log(f"  ✅ Ofertas encontradas: {count}")

                # Extraer primera oferta si existe
                if count > 0:
                    try:
                        first = elements[0]
                        title_elem = first.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                        job_title = title_elem.text[:50]
                        log(f"  📋 Primera oferta: {job_title}...")
                    except:
                        pass

            except Exception as e:
                log(f"  ❌ Error: {e}")

            # Delay entre requests
            time.sleep(3)

        except Exception as e:
            log(f"  ❌ Error cargando: {e}")

    # Test: Click en botón "Siguiente"
    log("\n" + "=" * 60)
    log("TEST: Navegar con botón 'Siguiente'")
    log("=" * 60)

    try:
        driver.get("https://es.indeed.com/jobs?q=data+scientist&l=España")
        time.sleep(6)

        # Contar ofertas en página 1
        elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
        page1_count = len(elements)
        log(f"\nPágina 1: {page1_count} ofertas")

        # Intentar encontrar botón "Siguiente"
        next_selectors = [
            "a[aria-label*='siguiente']",
            "a[aria-label*='Next']",
            "a[data-testid='pagination-page-next']",
            "nav[role='navigation'] a:last-child",
        ]

        next_button = None
        for selector in next_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    next_button = buttons[0]
                    log(f"✅ Botón 'Siguiente' encontrado: {selector}")
                    break
            except:
                continue

        if next_button:
            # Click en siguiente
            log("Haciendo click en 'Siguiente'...")
            next_button.click()
            time.sleep(6)

            # Contar ofertas en página 2
            elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
            page2_count = len(elements)
            log(f"Página 2 (después de click): {page2_count} ofertas")

            if page2_count > 0:
                log("✅ PAGINACIÓN FUNCIONA con botón 'Siguiente'")
            else:
                log("❌ Click en 'Siguiente' no cargó ofertas")
        else:
            log("❌ No se encontró botón 'Siguiente'")

    except Exception as e:
        log(f"❌ Error en test de botón: {e}")

    driver.quit()

    log("\n" + "=" * 60)
    log(f"Timestamp: {datetime.now()}")

    # Guardar
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Resultado guardado en: {diag_file}")
