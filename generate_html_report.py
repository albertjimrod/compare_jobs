#!/usr/bin/env python3
"""
Generador de Informe HTML Profesional para Ofertas de Trabajo

Genera un informe HTML interactivo con:
- Estadísticas visuales
- Top tecnologías, empresas y ubicaciones
- Tabla completa con enlaces clicables
- Búsqueda en tiempo real
- Filtros interactivos
- Diseño responsive y moderno
"""

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


def generate_html_report(csv_file, output_file=None):
    """
    Genera informe HTML desde un archivo CSV.

    Args:
        csv_file: Ruta al archivo CSV con ofertas
        output_file: Ruta del HTML a generar (opcional)
    """
    print(f"📊 Generando informe HTML desde {csv_file}...")

    # Leer CSV
    jobs = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row)

    if not jobs:
        print("⚠️  No hay ofertas en el CSV")
        return

    print(f"✅ {len(jobs)} ofertas cargadas")

    # Generar estadísticas
    stats = generate_statistics(jobs)

    # Crear HTML
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"informe_ofertas_{timestamp}.html"

    html_content = generate_html_content(jobs, stats)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Informe HTML generado: {output_file}")
    print(f"\n🌐 Abre el archivo en tu navegador:")
    print(f"   firefox {output_file}")
    print(f"   google-chrome {output_file}")
    print(f"   open {output_file}  # En Mac")

    return output_file


def generate_statistics(jobs):
    """Genera estadísticas de las ofertas."""
    # Tecnologías
    all_techs = []
    for job in jobs:
        if job.get('tecnologías') or job.get('tecnologias'):
            techs_str = job.get('tecnologías') or job.get('tecnologias')
            if techs_str:
                techs = [t.strip() for t in techs_str.split(',') if t.strip()]
                all_techs.extend(techs)

    tech_counter = Counter(all_techs)

    # Empresas
    companies = [job.get('empresa') for job in jobs if job.get('empresa')]
    company_counter = Counter(companies)

    # Ubicaciones
    locations = [job.get('ubicación') or job.get('ubicacion') for job in jobs if job.get('ubicación') or job.get('ubicacion')]
    location_counter = Counter(locations)

    # Ofertas con tecnologías
    with_tech = sum(1 for job in jobs if job.get('tecnologías') or job.get('tecnologias'))

    return {
        'total_ofertas': len(jobs),
        'top_tecnologias': tech_counter.most_common(30),
        'top_empresas': company_counter.most_common(20),
        'top_ubicaciones': location_counter.most_common(15),
        'total_tecnologias': len(tech_counter),
        'total_empresas': len(company_counter),
        'total_ubicaciones': len(location_counter),
        'ofertas_con_tecnologias': with_tech,
        'porcentaje_con_tecnologias': round((with_tech / len(jobs)) * 100, 1) if jobs else 0
    }


def generate_html_content(jobs, stats):
    """Genera el contenido HTML completo."""

    # Generar filas de la tabla
    table_rows = ""
    for i, job in enumerate(jobs, 1):
        titulo = job.get('título') or job.get('titulo', '')
        empresa = job.get('empresa', '')
        ubicacion = job.get('ubicación') or job.get('ubicacion', '')
        tecnologias = job.get('tecnologías') or job.get('tecnologias', '')
        url = job.get('url', '')

        # Crear badge de tecnologías
        tech_badges = ""
        if tecnologias:
            techs = [t.strip() for t in tecnologias.split(',')[:8] if t.strip()]
            for tech in techs:
                tech_badges += f'<span class="tech-badge">{tech}</span>'
            if ',' in tecnologias and len(tecnologias.split(',')) > 8:
                remaining = len(tecnologias.split(',')) - 8
                tech_badges += f'<span class="tech-badge more">+{remaining}</span>'

        table_rows += f"""
        <tr data-empresa="{empresa.lower()}" data-ubicacion="{ubicacion.lower()}" data-tecnologias="{tecnologias.lower()}">
            <td class="numero">{i}</td>
            <td class="titulo">
                <a href="{url}" target="_blank" rel="noopener">{titulo}</a>
            </td>
            <td class="empresa">{empresa}</td>
            <td class="ubicacion">{ubicacion}</td>
            <td class="tecnologias">{tech_badges}</td>
        </tr>
        """

    # Generar barras de tecnologías
    max_tech_count = stats['top_tecnologias'][0][1] if stats['top_tecnologias'] else 1
    tech_bars = ""
    for tech, count in stats['top_tecnologias'][:20]:
        percentage = (count / max_tech_count) * 100
        tech_bars += f"""
        <div class="stat-bar">
            <div class="stat-label">{tech}</div>
            <div class="stat-bar-container">
                <div class="stat-bar-fill" style="width: {percentage}%"></div>
                <span class="stat-count">{count}</span>
            </div>
        </div>
        """

    # Generar lista de empresas
    empresa_list = ""
    for empresa, count in stats['top_empresas'][:15]:
        empresa_list += f"""
        <div class="list-item">
            <span class="item-name">{empresa}</span>
            <span class="item-count">{count} ofertas</span>
        </div>
        """

    # Generar lista de ubicaciones
    ubicacion_list = ""
    for ubicacion, count in stats['top_ubicaciones'][:10]:
        ubicacion_list += f"""
        <div class="list-item">
            <span class="item-name">{ubicacion}</span>
            <span class="item-count">{count} ofertas</span>
        </div>
        """

    # HTML completo
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Ofertas de Trabajo - {datetime.now().strftime('%d/%m/%Y')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}

        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }}

        .section {{
            padding: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            margin-bottom: 25px;
            color: #333;
            border-left: 5px solid #667eea;
            padding-left: 15px;
        }}

        .stat-bar {{
            margin-bottom: 15px;
        }}

        .stat-bar .stat-label {{
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }}

        .stat-bar-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .stat-bar-fill {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            padding: 0 15px;
            color: white;
            font-weight: bold;
        }}

        .stat-count {{
            font-weight: bold;
            color: #667eea;
            min-width: 40px;
        }}

        .list-item {{
            display: flex;
            justify-content: space-between;
            padding: 15px;
            background: #f8f9fa;
            margin-bottom: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }}

        .list-item:hover {{
            background: #e9ecef;
        }}

        .item-name {{
            font-weight: 600;
            color: #333;
        }}

        .item-count {{
            color: #667eea;
            font-weight: bold;
        }}

        .search-box {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}

        .search-input {{
            width: 100%;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            transition: border-color 0.3s ease;
        }}

        .search-input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        tbody tr {{
            transition: background 0.3s ease;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        .numero {{
            width: 50px;
            text-align: center;
            color: #999;
            font-weight: bold;
        }}

        .titulo a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }}

        .titulo a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        .tech-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            margin: 2px;
            font-weight: 500;
        }}

        .tech-badge.more {{
            background: #999;
        }}

        .hidden {{
            display: none !important;
        }}

        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }}

        footer {{
            background: #2d3436;
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 40px;
        }}

        .export-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            margin: 10px;
            transition: transform 0.3s ease;
        }}

        .export-btn:hover {{
            transform: scale(1.05);
        }}

        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
            }}

            h1 {{
                font-size: 1.8em;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            table {{
                font-size: 0.9em;
            }}

            td, th {{
                padding: 10px 5px;
            }}
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .search-box, .export-btn {{
                display: none;
            }}

            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Informe de Ofertas de Trabajo</h1>
            <p class="subtitle">Generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}</p>
            <div style="margin-top: 20px;">
                <button class="export-btn" onclick="window.print()">📄 Exportar a PDF</button>
                <button class="export-btn" onclick="exportToCSV()">📊 Descargar CSV</button>
            </div>
        </header>

        <!-- Estadísticas Generales -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_ofertas']}</div>
                <div class="stat-label">Ofertas Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_tecnologias']}</div>
                <div class="stat-label">Tecnologías Únicas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_empresas']}</div>
                <div class="stat-label">Empresas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_ubicaciones']}</div>
                <div class="stat-label">Ubicaciones</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['porcentaje_con_tecnologias']}%</div>
                <div class="stat-label">Con Tecnologías</div>
            </div>
        </div>

        <!-- Top Tecnologías -->
        <div class="section">
            <h2 class="section-title">🛠️ Top 20 Tecnologías Más Demandadas</h2>
            {tech_bars}
        </div>

        <!-- Estadísticas Detalladas -->
        <div class="section">
            <div class="stats-summary">
                <div>
                    <h2 class="section-title">🏢 Top 15 Empresas</h2>
                    {empresa_list}
                </div>
                <div>
                    <h2 class="section-title">📍 Top 10 Ubicaciones</h2>
                    {ubicacion_list}
                </div>
            </div>
        </div>

        <!-- Tabla de Ofertas -->
        <div class="section" style="padding: 0;">
            <div class="search-box">
                <input type="text"
                       class="search-input"
                       id="searchInput"
                       placeholder="🔍 Buscar por título, empresa, ubicación o tecnología..."
                       onkeyup="filterTable()">
            </div>
            <div style="overflow-x: auto;">
                <table id="offersTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Título del Puesto</th>
                            <th>Empresa</th>
                            <th>Ubicación</th>
                            <th>Tecnologías</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            <p>📊 Informe generado automáticamente con {stats['total_ofertas']} ofertas de trabajo</p>
            <p>🤖 Sistema de Scraping Multi-Fuente • {datetime.now().year}</p>
        </footer>
    </div>

    <script>
        // Búsqueda en tiempo real
        function filterTable() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const table = document.getElementById('offersTable');
            const rows = table.getElementsByTagName('tr');

            let visibleCount = 0;

            for (let i = 1; i < rows.length; i++) {{
                const row = rows[i];
                const text = row.textContent.toLowerCase();

                if (text.includes(filter)) {{
                    row.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    row.classList.add('hidden');
                }}
            }}

            console.log(`Mostrando ${{visibleCount}} de ${{rows.length - 1}} ofertas`);
        }}

        // Exportar a CSV
        function exportToCSV() {{
            const table = document.getElementById('offersTable');
            const rows = table.querySelectorAll('tr:not(.hidden)');

            let csv = [];
            for (let row of rows) {{
                const cols = row.querySelectorAll('td, th');
                const rowData = [];
                for (let col of cols) {{
                    let text = col.textContent.trim();
                    text = text.replace(/"/g, '""'); // Escape quotes
                    rowData.push(`"${{text}}"`);
                }}
                csv.push(rowData.join(','));
            }}

            const csvContent = csv.join('\\n');
            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);

            link.setAttribute('href', url);
            link.setAttribute('download', 'ofertas_filtradas.csv');
            link.style.visibility = 'hidden';

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        // Animaciones al cargar
        window.addEventListener('load', function() {{
            const bars = document.querySelectorAll('.stat-bar-fill');
            bars.forEach((bar, index) => {{
                setTimeout(() => {{
                    bar.style.opacity = '1';
                }}, index * 50);
            }});
        }});
    </script>
</body>
</html>
    """

    return html


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python generate_html_report.py <archivo.csv> [salida.html]")
        print("\nEjemplo:")
        print("  python generate_html_report.py indeed.csv")
        print("  python generate_html_report.py indeed.csv mi_informe.html")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(csv_file).exists():
        print(f"❌ Error: No se encuentra el archivo {csv_file}")
        sys.exit(1)

    generate_html_report(csv_file, output_file)
