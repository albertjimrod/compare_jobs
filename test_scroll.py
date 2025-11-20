#!/usr/bin/env python3
"""
Diagnóstico de scroll infinito - Verifica por qué no carga más ofertas.
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

    diag_file = "test_scroll.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    log("TEST DE SCROLL INFINITO - INDEED")
    log("=" * 60)

    # Configurar driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Cargar página
        url = "https://es.indeed.com/jobs?q=data+scientist&l=España"
        log(f"\nCargando: {url}")
        driver.get(url)
        time.sleep(8)

        log(f"Título: {driver.title}")
        log("")

        # Selector que sabemos que funciona
        selector = "div[class*='job_']"

        # Intentar scroll infinito
        log("Iniciando scroll infinito...")
        log("-" * 60)

        previous_count = 0
        no_change_count = 0
        max_scrolls = 15

        for scroll_num in range(1, max_scrolls + 1):
            # Obtener altura antes
            height_before = driver.execute_script("return document.body.scrollHeight")

            # Scroll hasta el final
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Scroll intermedio
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(1)

            # Scroll final otra vez
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Obtener altura después
            height_after = driver.execute_script("return document.body.scrollHeight")

            # Contar elementos
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            current_count = len(elements)

            # Log detallado
            height_changed = "✅ CAMBIÓ" if height_after > height_before else "❌ NO cambió"
            count_changed = f"+{current_count - previous_count}" if current_count > previous_count else "sin cambios"

            log(f"Scroll {scroll_num}:")
            log(f"  Altura: {height_before} → {height_after} ({height_changed})")
            log(f"  Elementos: {previous_count} → {current_count} ({count_changed})")

            # Verificar si hay cambios
            if current_count == previous_count:
                no_change_count += 1
                log(f"  ⚠️  Sin nuevos elementos ({no_change_count}/3)")

                if no_change_count >= 3:
                    log("\n✓ Deteniendo: 3 scrolls sin cambios")
                    break
            else:
                no_change_count = 0

            previous_count = current_count
            log("")

        # Resumen final
        log("=" * 60)
        log(f"RESUMEN:")
        log(f"  Total scrolls realizados: {scroll_num}")
        log(f"  Elementos finales: {current_count}")
        log(f"  Altura final página: {height_after}px")

        # Intentar parsear algunas ofertas
        log("\n" + "=" * 60)
        log("PARSEANDO PRIMERAS 5 OFERTAS:")
        log("=" * 60)

        for i, elem in enumerate(elements[:5], 1):
            try:
                title = elem.find_element(By.CSS_SELECTOR, "h2.jobTitle").text
                company = elem.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                log(f"{i}. {title} - {company}")
            except Exception as e:
                log(f"{i}. Error: {e}")

        # Test: ¿Hay un botón "Cargar más"?
        log("\n" + "=" * 60)
        log("BUSCANDO BOTÓN 'CARGAR MÁS':")
        log("=" * 60)

        load_more_selectors = [
            "button[aria-label*='más']",
            "button[aria-label*='more']",
            "a[aria-label*='más']",
            "button:contains('Ver más')",
            "[data-testid*='load-more']",
        ]

        found_button = False
        for sel in load_more_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, sel)
                if buttons:
                    log(f"✅ Encontrado: {sel} ({len(buttons)} botones)")
                    found_button = True

                    # Intentar hacer click
                    log("   Intentando hacer click...")
                    buttons[0].click()
                    time.sleep(5)

                    new_count = len(driver.find_elements(By.CSS_SELECTOR, selector))
                    log(f"   Después del click: {new_count} elementos")
                    break
            except:
                pass

        if not found_button:
            log("❌ No se encontró botón 'Cargar más'")

    finally:
        driver.quit()

    log("\n" + "=" * 60)
    log(f"Timestamp: {datetime.now()}")

    # Guardar
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Resultado guardado en: {diag_file}")
