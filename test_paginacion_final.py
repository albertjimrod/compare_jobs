#!/usr/bin/env python3
"""
Test final del scraper con undetected-chromedriver y paginación.
Prueba con 1 keyword para verificar que encuentra 100+ ofertas.
"""

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from src.utils.config_loader import ConfigLoader
    from src.scrapers.indeed_scraper_selenium import IndeedScraperSelenium

    diag_file = "test_paginacion_final.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    log("TEST FINAL: UNDETECTED-CHROMEDRIVER + PAGINACIÓN")
    log("=" * 60)
    log("")

    config = ConfigLoader()
    scraper = IndeedScraperSelenium(config)

    log("Keyword: data scientist")
    log("Location: España")
    log("Método: Paginación con undetected-chromedriver")
    log("Máx páginas: 5 (para test rápido)")
    log("")
    log("Iniciando scraping...")
    log("-" * 60)

    # Limitar a 5 páginas para test rápido
    scraper.max_jobs = 75  # 5 páginas × 15 ofertas = ~75

    jobs = scraper.scrape_jobs(keywords=['data scientist'], location='España')

    log("=" * 60)
    log(f"RESULTADO: {len(jobs)} ofertas encontradas")
    log("=" * 60)

    if jobs:
        log("\nPRIMERAS 10 OFERTAS:")
        for i, job in enumerate(jobs[:10], 1):
            log(f"  {i}. {job.title} - {job.company}")

        log(f"\nÚLTIMAS 5 OFERTAS:")
        for i, job in enumerate(jobs[-5:], len(jobs)-4):
            log(f"  {i}. {job.title} - {job.company}")

        # Contar ofertas únicas
        unique_urls = set(j.url for j in jobs if j.url)
        log(f"\nOFERTAS ÚNICAS (por URL): {len(unique_urls)}")

        duplicates = len(jobs) - len(unique_urls)
        if duplicates > 0:
            log(f"⚠️  DUPLICADOS DETECTADOS: {duplicates}")

        # Verificar que son de diferentes páginas
        if len(jobs) > 20:
            log(f"\n✅ ÉXITO: Más de 20 ofertas = paginación funciona!")
        else:
            log(f"\n⚠️  Solo {len(jobs)} ofertas. Esperábamos 50+")

    else:
        log("❌ NO SE ENCONTRARON OFERTAS")

    log("")
    log("=" * 60)
    log("CONCLUSIÓN:")

    if len(jobs) >= 50:
        log("✅ PERFECTO: Paginación funciona correctamente")
        log(f"   {len(jobs)} ofertas encontradas de múltiples páginas")
        log("   Ahora puedes ejecutar con 3 keywords para 200+ ofertas")
    elif len(jobs) >= 20:
        log("⚠️  PARCIAL: Paginación funciona pero hay limitaciones")
        log(f"   {len(jobs)} ofertas (esperábamos 50+)")
        log("   Puede necesitar más delay entre páginas")
    else:
        log("❌ FALLO: Paginación no funciona como esperado")
        log(f"   Solo {len(jobs)} ofertas encontradas")

    log("")
    log(f"Timestamp: {datetime.now()}")

    # Guardar
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Resultado guardado en: {diag_file}")
