#!/usr/bin/env python3
"""Script de debug para Indeed - Genera resumen diagnóstico."""

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    # Añadir el directorio del proyecto al path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from src.utils.config_loader import ConfigLoader
    from src.scrapers.indeed_scraper_selenium import IndeedScraperSelenium

    print("🔍 Iniciando test de Indeed con debug...")
    print("="*80)

    # Crear archivo de diagnóstico
    diag_file = "diagnostico_indeed.txt"
    output = []

    def log(msg):
        print(msg)
        output.append(msg)

    config = ConfigLoader()
    scraper = IndeedScraperSelenium(config)

    # Probar solo con 'data scientist' (1 keyword para diagnóstico rápido)
    log("KEYWORD: data scientist")
    log("LOCATION: España")
    log("")

    jobs = scraper.scrape_jobs(keywords=['data scientist'], location='España')

    log("="*60)
    log(f"RESULTADO: {len(jobs)} ofertas encontradas")
    log("="*60)

    if jobs:
        log("\nPRIMERAS 5 OFERTAS:")
        for i, job in enumerate(jobs[:5], 1):
            log(f"  {i}. {job.title} - {job.company}")

        # Contar ofertas únicas por URL
        unique_urls = set(j.url for j in jobs if j.url)
        log(f"\nOFERTAS ÚNICAS (por URL): {len(unique_urls)}")

        # Verificar duplicados
        duplicates = len(jobs) - len(unique_urls)
        if duplicates > 0:
            log(f"⚠️  DUPLICADOS DETECTADOS: {duplicates}")
    else:
        log("❌ NO SE ENCONTRARON OFERTAS")

    log("")
    log("="*60)
    log(f"Timestamp: {datetime.now()}")

    # Guardar diagnóstico
    with open(diag_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n📄 Diagnóstico guardado en: {diag_file}")
    print("   Muéstrame el contenido de este archivo para analizar el problema.")
