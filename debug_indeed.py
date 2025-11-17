#!/usr/bin/env python3
"""Script de debug para investigar paginación de Indeed."""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Configura el driver de Selenium."""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(2)
    return driver

def test_pagination():
    """Prueba la paginación de Indeed."""
    driver = setup_driver()

    try:
        # Probar diferentes URLs de paginación
        urls = [
            "https://es.indeed.com/jobs?q=data+scientist&l=España&start=0",
            "https://es.indeed.com/jobs?q=data+scientist&l=España&start=10",
            "https://es.indeed.com/jobs?q=data+scientist&l=España&start=20",
        ]

        for page_num, url in enumerate(urls, 1):
            print(f"\n{'='*80}")
            print(f"PÁGINA {page_num}: {url}")
            print('='*80)

            driver.get(url)
            time.sleep(8)

            # Scroll agresivo
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)

            print("\nProbando selectores...")
            selectors = [
                "div.job_seen_beacon",
                "div[data-jk]",
                "td.resultContent",
                "div.cardOutline",
                "div.slider_item",
                "div[class*='job_']",
                "div[class*='result']",
            ]

            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"  {selector:30} → {len(elements):3} elementos")
                    if elements and len(elements) > 0:
                        print(f"    ✓ SELECTOR FUNCIONA!")
                        # Mostrar contenido del primer elemento
                        try:
                            first_text = elements[0].text[:100]
                            print(f"    Primer elemento: {first_text}...")
                        except:
                            pass
                        break
                except Exception as e:
                    print(f"  {selector:30} → ERROR: {str(e)[:50]}")

            # Verificar si hay mensaje de "no hay resultados"
            try:
                no_results = driver.find_elements(By.CSS_SELECTOR, "div[class*='bad_query']")
                if no_results:
                    print(f"\n  ⚠️ MENSAJE 'NO RESULTS' ENCONTRADO")
            except:
                pass

            # Guardar screenshot para debug
            screenshot_path = f"/home/user/compare_jobs/debug_page{page_num}.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n  📸 Screenshot guardado: {screenshot_path}")

            time.sleep(2)

    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 DEBUG: Investigando paginación de Indeed")
    print("="*80)
    test_pagination()
    print("\n✅ Debug completado")
