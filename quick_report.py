#!/usr/bin/env python3
"""Genera informe rápido de ofertas ya scrapeadas"""
import csv
from collections import Counter
from datetime import datetime

# Cargar ofertas del scraper
from src.scrapers.scraper_factory import ScraperFactory
from src.utils.config_loader import ConfigLoader

print("📊 Generando informe de Indeed...\n")

config = ConfigLoader()
scraper = ScraperFactory.create_scraper('indeed', config)
jobs = scraper.get_jobs()

if not jobs:
    print("⚠️  No hay ofertas en memoria")
    print("Ejecuta primero: python test_scraper_individual.py indeed --max-jobs=100")
    exit(1)

print(f"✅ {len(jobs)} ofertas encontradas\n")

# CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_file = f"indeed_{timestamp}.csv"

with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['titulo', 'empresa', 'ubicacion', 'tecnologias', 'num_techs', 'url'])
    for job in jobs:
        techs = ', '.join(job.technologies) if job.technologies else ''
        num_techs = len(job.technologies) if job.technologies else 0
        writer.writerow([job.title, job.company, job.location, techs, num_techs, job.url])

print(f"💾 CSV guardado: {csv_file}\n")

# Estadísticas
all_techs = []
for job in jobs:
    if job.technologies:
        all_techs.extend(job.technologies)

tech_counter = Counter(all_techs)
companies = Counter([job.company for job in jobs if job.company])
locations = Counter([job.location for job in jobs if job.location])

with_tech = sum(1 for job in jobs if job.technologies)

print("="*80)
print("📊 ESTADÍSTICAS")
print("="*80)
print(f"\n📋 Resumen:")
print(f"   • Total ofertas: {len(jobs)}")
print(f"   • Empresas únicas: {len(companies)}")
print(f"   • Ubicaciones únicas: {len(locations)}")
print(f"   • Tecnologías únicas: {len(tech_counter)}")
print(f"   • Ofertas con tecnologías: {with_tech} ({round(with_tech/len(jobs)*100, 1)}%)")

print(f"\n🔝 Top 20 Tecnologías:")
for i, (tech, count) in enumerate(tech_counter.most_common(20), 1):
    print(f"   {i:2d}. {tech:<25} → {count:>3} menciones")

print(f"\n🏢 Top 10 Empresas:")
for i, (comp, count) in enumerate(companies.most_common(10), 1):
    print(f"   {i:2d}. {comp:<40} → {count:>3} ofertas")

print(f"\n📍 Top 10 Ubicaciones:")
for i, (loc, count) in enumerate(locations.most_common(10), 1):
    print(f"   {i:2d}. {loc:<40} → {count:>3} ofertas")

# Informe texto
txt_file = f"indeed_{timestamp}_informe.txt"
with open(txt_file, 'w', encoding='utf-8') as f:
    f.write(f"INFORME INDEED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*80 + "\n\n")
    f.write(f"Total ofertas: {len(jobs)}\n")
    f.write(f"Empresas: {len(companies)} | Ubicaciones: {len(locations)} | Tecnologías: {len(tech_counter)}\n\n")
    f.write("TOP 20 TECNOLOGÍAS:\n" + "-"*80 + "\n")
    for i, (tech, count) in enumerate(tech_counter.most_common(20), 1):
        f.write(f"{i:2d}. {tech:<30} → {count:>4} menciones\n")
    f.write("\nTOP 10 EMPRESAS:\n" + "-"*80 + "\n")
    for i, (comp, count) in enumerate(companies.most_common(10), 1):
        f.write(f"{i:2d}. {comp:<50} → {count:>3} ofertas\n")
    f.write("\nMUESTRA (20 primeras ofertas):\n" + "-"*80 + "\n")
    for i, job in enumerate(jobs[:20], 1):
        f.write(f"\n{i}. {job.title}\n")
        f.write(f"   {job.company} | {job.location}\n")
        if job.technologies:
            f.write(f"   Techs: {', '.join(job.technologies[:6])}\n")

print(f"\n📄 Informe guardado: {txt_file}")
print(f"\n✅ Archivos generados:")
print(f"   • {csv_file}")
print(f"   • {txt_file}")
