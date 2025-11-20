#!/usr/bin/env python3
"""
Test con navegador VISIBLE (no headless) para evitar detección Cloudflare.
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

    diag_file = "test_no_headless.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    log("TEST SIN HEADLESS - INDEED")
    log("=" * 60)
    log("NOTA: Se abrirá una ventana de Chrome visible")
    log("")

    # Configurar driver SIN headless
    chrome_options = Options()
    # NO añadir --headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Test 1: Página sin start
        log("TEST 1: Cargando página sin parámetro 'start'")
        url1 = "https://es.indeed.com/jobs?q=data+scientist&l=España"
        driver.get(url1)
        time.sleep(8)

        title1 = driver.title
        log(f"  URL: {url1}")
        log(f"  Título: {title1}")

        if "momento" in title1.lower():
            log("  ❌ BLOQUEADO por Cloudflare")
        else:
            elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
            log(f"  ✅ OK - {len(elements)} ofertas")

        # Test 2: Página con start=10 (después de delay)
        log("\nTEST 2: Navegando a página 2 (start=10)")
        log("  Esperando 10 segundos antes de cargar...")
        time.sleep(10)

        url2 = "https://es.indeed.com/jobs?q=data+scientist&l=España&start=10"
        driver.get(url2)
        time.sleep(8)

        title2 = driver.title
        log(f"  URL: {url2}")
        log(f"  Título: {title2}")

        if "momento" in title2.lower():
            log("  ❌ BLOQUEADO por Cloudflare")
        else:
            elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
            log(f"  ✅ OK - {len(elements)} ofertas")

            if len(elements) > 0:
                log("\n  🎉 ÉXITO: Modo no-headless evita Cloudflare!")

        # Test 3: Intentar más páginas
        if "momento" not in title2.lower():
            log("\nTEST 3: Probando página 3 (start=20)")
            time.sleep(10)

            url3 = "https://es.indeed.com/jobs?q=data+scientist&l=España&start=20"
            driver.get(url3)
            time.sleep(8)

            title3 = driver.title
            log(f"  URL: {url3}")
            log(f"  Título: {title3}")

            if "momento" in title3.lower():
                log("  ❌ BLOQUEADO")
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
                log(f"  ✅ OK - {len(elements)} ofertas")

        log("\n" + "=" * 60)
        log("CONCLUSIÓN:")

        if "momento" in title2.lower():
            log("❌ Modo NO-headless NO evita Cloudflare")
            log("   Posibles soluciones:")
            log("   1. Usar delays más largos (30-60s entre páginas)")
            log("   2. Aceptar solo ~15 ofertas por keyword")
            log("   3. Usar undetected-chromedriver")
        else:
            log("✅ Modo NO-headless FUNCIONA!")
            log("   Puedes scrapear múltiples páginas sin bloqueo")

    finally:
        log("\nCerrando navegador en 5 segundos...")
        time.sleep(5)
        driver.quit()

    log(f"\nTimestamp: {datetime.now()}")

    # Guardar
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Resultado guardado en: {diag_file}")
