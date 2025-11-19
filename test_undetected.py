#!/usr/bin/env python3
"""
Test con undetected-chromedriver para evitar Cloudflare.
Esta librería está diseñada para evitar detección de bots.
"""

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime
    import time

    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
    except ImportError:
        print("❌ undetected-chromedriver no está instalado")
        print("   Ejecuta: pip install undetected-chromedriver")
        sys.exit(1)

    diag_file = "test_undetected.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    log("TEST CON UNDETECTED-CHROMEDRIVER")
    log("=" * 60)
    log("Esta librería evita detección de Cloudflare/captcha")
    log("")

    # Configurar undetected-chromedriver
    options = uc.ChromeOptions()
    # options.add_argument('--headless')  # Comentado: mejor visible para Cloudflare

    log("Inicializando undetected-chromedriver...")
    driver = uc.Chrome(options=options, version_main=None)

    try:
        # Test 1: Página principal sin start
        log("\nTEST 1: Página principal (sin 'start')")
        url1 = "https://es.indeed.com/jobs?q=data+scientist&l=España"
        driver.get(url1)
        time.sleep(8)

        title1 = driver.title
        log(f"  URL: {url1}")
        log(f"  Título: {title1}")

        if "momento" in title1.lower():
            log("  ❌ BLOQUEADO - Verificando si hay botón de Cloudflare...")

            # Buscar botón de verificación
            cloudflare_selectors = [
                "input[type='checkbox']",
                "iframe[src*='cloudflare']",
                "div#challenge-form",
                "[id*='cf-']",
            ]

            for selector in cloudflare_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        log(f"  ⚠️  Encontrado elemento Cloudflare: {selector}")
                except:
                    pass
        else:
            elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
            log(f"  ✅ OK - {len(elements)} ofertas encontradas")

        # Test 2: Página con start=10 (paginación)
        log("\nTEST 2: Página 2 con paginación (start=10)")
        log("  Esperando 15 segundos...")
        time.sleep(15)

        url2 = "https://es.indeed.com/jobs?q=data+scientist&l=España&start=10"
        driver.get(url2)
        time.sleep(8)

        title2 = driver.title
        log(f"  URL: {url2}")
        log(f"  Título: {title2}")

        if "momento" in title2.lower():
            log("  ❌ BLOQUEADO por Cloudflare")
            log("  Esperando 30 segundos adicionales...")
            time.sleep(30)

            # Intentar refrescar
            log("  Refrescando página...")
            driver.refresh()
            time.sleep(10)

            new_title = driver.title
            log(f"  Nuevo título: {new_title}")

            if "momento" not in new_title.lower():
                log("  ✅ Desbloqueado después de esperar!")
        else:
            elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='job_']")
            log(f"  ✅ OK - {len(elements)} ofertas encontradas")

            if len(elements) > 0:
                # Extraer primera oferta
                try:
                    first = elements[0]
                    title = first.find_element(By.CSS_SELECTOR, "h2.jobTitle").text
                    company = first.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                    log(f"  📋 Primera oferta: {title} - {company}")
                except:
                    pass

        # Test 3: Página 3 (start=20)
        if "momento" not in title2.lower():
            log("\nTEST 3: Página 3 (start=20)")
            log("  Esperando 15 segundos...")
            time.sleep(15)

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

        # Conclusión
        log("\n" + "=" * 60)
        log("CONCLUSIÓN:")

        if "momento" not in title2.lower():
            log("✅ ÉXITO: undetected-chromedriver evita Cloudflare!")
            log("   Se puede usar paginación para obtener 100+ ofertas")
        elif "momento" not in title1.lower():
            log("⚠️  PARCIAL: Funciona para página 1, pero Cloudflare detecta paginación")
            log("   Solución: Usar múltiples keywords en lugar de paginación")
        else:
            log("❌ FALLO: Cloudflare sigue bloqueando")
            log("   Necesita intervención manual o delays muy largos")

    finally:
        log("\nCerrando navegador en 5 segundos...")
        time.sleep(5)
        driver.quit()

    log(f"\nTimestamp: {datetime.now()}")

    # Guardar
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Resultado guardado en: {diag_file}")
