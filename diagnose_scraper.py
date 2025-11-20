#!/usr/bin/env python3
"""
Script de diagnóstico para ver qué está pasando con un scraper.
"""

import sys
import time
from src.scrapers.scraper_factory import ScraperFactory
from src.utils.config_loader import ConfigLoader

config = ConfigLoader()

# Forzar modo visual y verbose
config.config['scraping.headless_mode'] = False
config.config['scraping.max_jobs_per_platform'] = 5

print("="*70)
print("🔍 DIAGNÓSTICO DE SCRAPER - MICHAELPAGE")
print("="*70)
print()

try:
    scraper = ScraperFactory.create_scraper('michaelpage', config)

    print(f"✓ Scraper creado: {scraper.platform_name}")
    print(f"✓ Base URL: {scraper.BASE_URL}")
    print(f"✓ Jobs URL: {scraper.JOBS_URL}")
    print(f"✓ Max jobs: {scraper.max_jobs}")
    print()

    print("Iniciando scraping...")
    print("MIRA EL NAVEGADOR - ¿Se abre? ¿Carga la página?")
    print()

    jobs = scraper.scrape_jobs(
        keywords=['python'],
        location='Madrid, España'
    )

    print()
    print("="*70)
    print(f"RESULTADO: {len(jobs)} ofertas encontradas")
    print("="*70)

    if len(jobs) == 0:
        print()
        print("⚠️  NO SE ENCONTRARON OFERTAS")
        print()
        print("Posibles causas:")
        print("1. La URL de búsqueda no es correcta")
        print("2. Los selectores CSS no coinciden con la página")
        print("3. La página requiere interacción adicional (cookies, login, etc.)")
        print("4. La página está vacía o no tiene ofertas con ese criterio")
        print()
        print("💡 SOLUCIÓN:")
        print("Usa el navegador que se abrió para:")
        print("- Ver si aparecen ofertas en la página")
        print("- Presiona F12 > Inspector")
        print("- Encuentra el elemento de una oferta")
        print("- Copia su selector CSS")
        print("- Actualiza el scraper con ese selector")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
