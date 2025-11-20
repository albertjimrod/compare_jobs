#!/usr/bin/env python3
"""Script simplificado - NO requiere dependencias externas"""

import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from collections import Counter


def generate_report(platform='indeed', output_dir='data/processed'):
    print("="*80)
    print(f"📊 GENERANDO INFORME DE {platform.upper()}")
    print("="*80)
    print()

    try:
        from src.scrapers.scraper_factory import ScraperFactory
        from src.utils.config_loader import ConfigLoader

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        print(f"📥 Cargando ofertas de {platform}...")
        config = ConfigLoader()
        scraper = ScraperFactory.create_scraper(platform, config)
        jobs = scraper.get_jobs()

        if not jobs:
            print("⚠️  No hay ofertas disponibles")
            return

        print(f"✅ {len(jobs)} ofertas encontradas\n")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{platform}_{timestamp}"

        # CSV
        print("💾 Exportando a CSV...")
        csv_path = f"{output_dir}/{base_filename}.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['titulo', 'empresa', 'ubicacion', 'descripcion', 'tecnologias', 'num_tecnologias', 'url', 'plataforma'])
            for job in jobs:
                desc = (job.description[:200] + '...') if job.description and len(job.description) > 200 else (job.description or '')
                techs = ', '.join(job.technologies) if job.technologies else ''
                writer.writerow([job.title, job.company, job.location, desc, techs, len(job.technologies) if job.technologies else 0, job.url, job.platform])
        print(f"✅ CSV: {csv_path}\n")

        # Estadísticas
        print("📊 Generando estadísticas...")
        all_techs = []
        for job in jobs:
            if job.technologies:
                all_techs.extend(job.technologies)
        
        tech_counter = Counter(all_techs)
        companies = Counter([job.company for job in jobs if job.company])
        locations = Counter([job.location for job in jobs if job.location])
        
        with_tech = sum(1 for job in jobs if job.technologies)
        
        stats = {
            'total_ofertas': len(jobs),
            'top_tecnologias': [{'tecnologia': t, 'menciones': c} for t, c in tech_counter.most_common(20)],
            'top_empresas': [{'empresa': e, 'ofertas': c} for e, c in companies.most_common(10)],
            'top_ubicaciones': [{'ubicacion': l, 'ofertas': c} for l, c in locations.most_common(10)],
            'ofertas_con_tecnologias': with_tech,
            'porcentaje_con_tecnologias': round((with_tech / len(jobs)) * 100, 1)
        }

        # Informe texto
        txt_path = f"{output_dir}/{base_filename}_informe.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\nINFORME DE SCRAPING - {platform.upper()}\n{'='*80}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total ofertas: {len(jobs)}\n{'='*80}\n\n")
            
            f.write(f"RESUMEN EJECUTIVO\n{'-'*80}\n")
            f.write(f"• Total ofertas: {len(jobs)}\n")
            f.write(f"• Empresas únicas: {len(companies)}\n")
            f.write(f"• Ubicaciones únicas: {len(locations)}\n")
            f.write(f"• Tecnologías únicas: {len(tech_counter)}\n")
            f.write(f"• Ofertas con tecnologías: {with_tech} ({stats['porcentaje_con_tecnologias']}%)\n\n")
            
            f.write(f"TOP 20 TECNOLOGÍAS\n{'-'*80}\n")
            for i, item in enumerate(stats['top_tecnologias'], 1):
                f.write(f"{i:2d}. {item['tecnologia']:<30} → {item['menciones']:>4} menciones\n")
            
            f.write(f"\nTOP 10 EMPRESAS\n{'-'*80}\n")
            for i, item in enumerate(stats['top_empresas'], 1):
                f.write(f"{i:2d}. {item['empresa']:<50} → {item['ofertas']:>3} ofertas\n")
            
            f.write(f"\nTOP 10 UBICACIONES\n{'-'*80}\n")
            for i, item in enumerate(stats['top_ubicaciones'], 1):
                f.write(f"{i:2d}. {item['ubicacion']:<50} → {item['ofertas']:>3} ofertas\n")
            
            f.write(f"\nMUESTRA DE OFERTAS (20 primeras)\n{'-'*80}\n")
            for i, job in enumerate(jobs[:20], 1):
                f.write(f"\n{i}. {job.title}\n   Empresa: {job.company}\n   Ubicación: {job.location}\n")
                if job.technologies:
                    f.write(f"   Tecnologías: {', '.join(job.technologies[:8])}\n")
                f.write(f"   URL: {job.url}\n")
        
        print(f"✅ Informe: {txt_path}\n")

        # JSON
        json_path = f"{output_dir}/{base_filename}_stats.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"✅ Stats JSON: {json_path}\n")

        # Resumen pantalla
        print("="*80)
        print("📊 RESUMEN")
        print("="*80)
        print(f"\n📋 Total ofertas: {len(jobs)}")
        print(f"🏢 Empresas únicas: {len(companies)}")
        print(f"📍 Ubicaciones únicas: {len(locations)}")
        print(f"🛠️  Tecnologías únicas: {len(tech_counter)}\n")
        print("🔝 Top 10 Tecnologías:")
        for i, item in enumerate(stats['top_tecnologias'][:10], 1):
            print(f"   {i:2d}. {item['tecnologia']:<25} → {item['menciones']:>3} menciones")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    platform = sys.argv[1] if len(sys.argv) > 1 else 'indeed'
    generate_report(platform)
