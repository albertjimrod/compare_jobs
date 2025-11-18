#!/usr/bin/env python3
"""Script de debug para Indeed."""

if __name__ == "__main__":
    import sys
    import os

    # Añadir el directorio del proyecto al path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    from src.utils.config_loader import ConfigLoader
    from src.scrapers.indeed_scraper_selenium import IndeedScraperSelenium

    print("🔍 Iniciando test de Indeed con debug...")
    print("="*80)

    config = ConfigLoader()
    scraper = IndeedScraperSelenium(config)

    # Probar solo con 'data scientist'
    jobs = scraper.scrape_jobs(keywords=['data scientist'], location='España')

    print("="*80)
    print(f"✅ Total encontrado: {len(jobs)} ofertas")
    print("="*80)

    if jobs:
        print("\n📋 Primeras 5 ofertas:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"  {i}. {job.title} - {job.company}")
