#!/usr/bin/env python3
"""
Script para generar informe completo de ofertas scrapeadas.

Genera:
- CSV con todas las ofertas
- Estadísticas detalladas
- Top tecnologías
- Análisis por ubicación
- Informe en texto
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import Counter
import json

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Pandas no disponible. Instala con: pip install pandas")

from loguru import logger

# Configurar logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def generate_report(platform='indeed', output_dir='data/processed'):
    """
    Genera informe completo de un scraper.

    Args:
        platform: Nombre del scraper
        output_dir: Directorio donde guardar los archivos
    """
    logger.info("="*80)
    logger.info(f"📊 GENERANDO INFORME DE {platform.upper()}")
    logger.info("="*80)
    logger.info("")

    try:
        # Importar módulos
        from src.scrapers.scraper_factory import ScraperFactory
        from src.utils.config_loader import ConfigLoader

        # Crear directorio de salida
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Cargar scraper
        logger.info(f"📥 Cargando ofertas de {platform}...")
        config = ConfigLoader()
        scraper = ScraperFactory.create_scraper(platform, config)
        jobs = scraper.get_jobs()

        if not jobs:
            logger.warning("⚠️  No hay ofertas disponibles para generar informe")
            logger.info("Ejecuta primero el scraper para obtener datos")
            return

        logger.success(f"✅ {len(jobs)} ofertas encontradas")
        logger.info("")

        # Generar timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{platform}_{timestamp}"

        # 1. Exportar a CSV
        if PANDAS_AVAILABLE:
            logger.info("💾 Exportando a CSV...")
            csv_path = export_to_csv(jobs, output_dir, base_filename)
            logger.success(f"✅ CSV guardado: {csv_path}")
            logger.info("")

        # 2. Generar estadísticas
        logger.info("📊 Generando estadísticas...")
        stats = generate_statistics(jobs)

        # 3. Guardar informe de texto
        logger.info("📝 Creando informe de texto...")
        txt_path = f"{output_dir}/{base_filename}_informe.txt"
        save_text_report(jobs, stats, txt_path, platform)
        logger.success(f"✅ Informe guardado: {txt_path}")
        logger.info("")

        # 4. Guardar JSON con stats
        logger.info("💾 Guardando estadísticas JSON...")
        json_path = f"{output_dir}/{base_filename}_stats.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
        logger.success(f"✅ Estadísticas JSON: {json_path}")
        logger.info("")

        # 5. Mostrar resumen en pantalla
        print_summary(stats, platform)

        logger.info("")
        logger.info("="*80)
        logger.success("🎉 INFORME COMPLETADO")
        logger.info("="*80)
        logger.info("")
        logger.info("📂 Archivos generados:")
        if PANDAS_AVAILABLE:
            logger.info(f"   • CSV: {csv_path}")
        logger.info(f"   • Informe: {txt_path}")
        logger.info(f"   • Stats JSON: {json_path}")
        logger.info("")

        return {
            'csv': csv_path if PANDAS_AVAILABLE else None,
            'report': txt_path,
            'stats': json_path,
            'jobs_count': len(jobs)
        }

    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        logger.error("Asegúrate de haber hecho el merge de la rama estable")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error generando informe: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


def export_to_csv(jobs, output_dir, base_filename):
    """Exporta ofertas a CSV."""
    data = []
    for job in jobs:
        data.append({
            'titulo': job.title,
            'empresa': job.company,
            'ubicacion': job.location,
            'descripcion': job.description[:200] + '...' if job.description and len(job.description) > 200 else job.description or '',
            'tecnologias': ', '.join(job.technologies) if job.technologies else '',
            'num_tecnologias': len(job.technologies) if job.technologies else 0,
            'skills': ', '.join(job.skills) if hasattr(job, 'skills') and job.skills else '',
            'url': job.url,
            'plataforma': job.platform,
            'fecha_scraping': job.scraped_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(job, 'scraped_date') and job.scraped_date else ''
        })

    df = pd.DataFrame(data)
    csv_path = f"{output_dir}/{base_filename}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    return csv_path


def generate_statistics(jobs):
    """Genera estadísticas de las ofertas."""
    stats = {
        'total_ofertas': len(jobs),
        'fecha_generacion': datetime.now().isoformat(),
    }

    # Tecnologías
    all_techs = []
    for job in jobs:
        if job.technologies:
            all_techs.extend(job.technologies)

    tech_counter = Counter(all_techs)
    stats['top_tecnologias'] = [
        {'tecnologia': tech, 'menciones': count}
        for tech, count in tech_counter.most_common(20)
    ]
    stats['total_tecnologias_unicas'] = len(tech_counter)

    # Empresas
    companies = [job.company for job in jobs if job.company]
    company_counter = Counter(companies)
    stats['top_empresas'] = [
        {'empresa': comp, 'ofertas': count}
        for comp, count in company_counter.most_common(10)
    ]
    stats['total_empresas_unicas'] = len(company_counter)

    # Ubicaciones
    locations = [job.location for job in jobs if job.location]
    location_counter = Counter(locations)
    stats['top_ubicaciones'] = [
        {'ubicacion': loc, 'ofertas': count}
        for loc, count in location_counter.most_common(10)
    ]
    stats['total_ubicaciones_unicas'] = len(location_counter)

    # Ofertas con/sin tecnologías
    with_tech = sum(1 for job in jobs if job.technologies)
    stats['ofertas_con_tecnologias'] = with_tech
    stats['ofertas_sin_tecnologias'] = len(jobs) - with_tech
    stats['porcentaje_con_tecnologias'] = round((with_tech / len(jobs)) * 100, 1) if jobs else 0

    # Promedio de tecnologías por oferta
    tech_counts = [len(job.technologies) for job in jobs if job.technologies]
    stats['promedio_tecnologias_por_oferta'] = round(sum(tech_counts) / len(tech_counts), 1) if tech_counts else 0

    return stats


def save_text_report(jobs, stats, output_path, platform):
    """Guarda informe en formato texto."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"INFORME DE SCRAPING - {platform.upper()}\n")
        f.write("="*80 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total ofertas: {len(jobs)}\n")
        f.write("="*80 + "\n\n")

        # Resumen ejecutivo
        f.write("RESUMEN EJECUTIVO\n")
        f.write("-"*80 + "\n")
        f.write(f"• Total ofertas encontradas: {stats['total_ofertas']}\n")
        f.write(f"• Empresas únicas: {stats['total_empresas_unicas']}\n")
        f.write(f"• Ubicaciones únicas: {stats['total_ubicaciones_unicas']}\n")
        f.write(f"• Tecnologías únicas detectadas: {stats['total_tecnologias_unicas']}\n")
        f.write(f"• Ofertas con tecnologías: {stats['ofertas_con_tecnologias']} ({stats['porcentaje_con_tecnologias']}%)\n")
        f.write(f"• Promedio tecnologías/oferta: {stats['promedio_tecnologias_por_oferta']}\n")
        f.write("\n")

        # Top tecnologías
        f.write("TOP 20 TECNOLOGÍAS MÁS DEMANDADAS\n")
        f.write("-"*80 + "\n")
        for i, item in enumerate(stats['top_tecnologias'], 1):
            f.write(f"{i:2d}. {item['tecnologia']:<30} → {item['menciones']:>4} menciones\n")
        f.write("\n")

        # Top empresas
        f.write("TOP 10 EMPRESAS CON MÁS OFERTAS\n")
        f.write("-"*80 + "\n")
        for i, item in enumerate(stats['top_empresas'], 1):
            f.write(f"{i:2d}. {item['empresa']:<50} → {item['ofertas']:>3} ofertas\n")
        f.write("\n")

        # Top ubicaciones
        f.write("TOP 10 UBICACIONES\n")
        f.write("-"*80 + "\n")
        for i, item in enumerate(stats['top_ubicaciones'], 1):
            f.write(f"{i:2d}. {item['ubicacion']:<50} → {item['ofertas']:>3} ofertas\n")
        f.write("\n")

        # Muestra de ofertas
        f.write("MUESTRA DE OFERTAS (Primeras 20)\n")
        f.write("-"*80 + "\n")
        for i, job in enumerate(jobs[:20], 1):
            f.write(f"\n{i}. {job.title}\n")
            f.write(f"   Empresa: {job.company}\n")
            f.write(f"   Ubicación: {job.location}\n")
            if job.technologies:
                f.write(f"   Tecnologías: {', '.join(job.technologies[:8])}")
                if len(job.technologies) > 8:
                    f.write(f" (+{len(job.technologies)-8} más)")
                f.write("\n")
            f.write(f"   URL: {job.url}\n")

        f.write("\n" + "="*80 + "\n")
        f.write("FIN DEL INFORME\n")
        f.write("="*80 + "\n")


def print_summary(stats, platform):
    """Imprime resumen en pantalla."""
    logger.info("="*80)
    logger.info("📊 RESUMEN DE ESTADÍSTICAS")
    logger.info("="*80)
    logger.info("")

    logger.info(f"📋 Información General:")
    logger.info(f"   • Plataforma: {platform.upper()}")
    logger.info(f"   • Total ofertas: {stats['total_ofertas']}")
    logger.info(f"   • Empresas únicas: {stats['total_empresas_unicas']}")
    logger.info(f"   • Ubicaciones únicas: {stats['total_ubicaciones_unicas']}")
    logger.info("")

    logger.info(f"🛠️  Tecnologías:")
    logger.info(f"   • Tecnologías únicas: {stats['total_tecnologias_unicas']}")
    logger.info(f"   • Ofertas con tecnologías: {stats['ofertas_con_tecnologias']} ({stats['porcentaje_con_tecnologias']}%)")
    logger.info(f"   • Promedio por oferta: {stats['promedio_tecnologias_por_oferta']}")
    logger.info("")

    logger.info(f"🔝 Top 10 Tecnologías:")
    for i, item in enumerate(stats['top_tecnologias'][:10], 1):
        logger.info(f"   {i:2d}. {item['tecnologia']:<25} → {item['menciones']:>3} menciones")
    logger.info("")

    logger.info(f"🏢 Top 5 Empresas:")
    for i, item in enumerate(stats['top_empresas'][:5], 1):
        logger.info(f"   {i}. {item['empresa']:<40} → {item['ofertas']} ofertas")
    logger.info("")

    logger.info(f"📍 Top 5 Ubicaciones:")
    for i, item in enumerate(stats['top_ubicaciones'][:5], 1):
        logger.info(f"   {i}. {item['ubicacion']:<40} → {item['ofertas']} ofertas")
    logger.info("")


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generar informe de ofertas scrapeadas'
    )
    parser.add_argument(
        'platform',
        type=str,
        nargs='?',
        default='indeed',
        help='Nombre del scraper (default: indeed)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/processed',
        help='Directorio de salida (default: data/processed)'
    )

    args = parser.parse_args()

    # Generar informe
    generate_report(args.platform, args.output_dir)


if __name__ == "__main__":
    main()
