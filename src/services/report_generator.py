"""
Generador de informes HTML para análisis de ofertas de trabajo.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from loguru import logger

from ..utils.config_loader import ConfigLoader


class ReportGenerator:
    """Genera informes HTML con los resultados del análisis."""

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Ofertas de Trabajo - Ciencia de Datos</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2c3e50;
        }

        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }

        .date {
            color: #95a5a6;
            font-size: 0.9em;
            margin-top: 10px;
        }

        .section {
            margin-bottom: 40px;
        }

        h2 {
            color: #34495e;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }

        h3 {
            color: #2c3e50;
            font-size: 1.3em;
            margin-bottom: 15px;
        }

        .summary-box {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .insight {
            background-color: #e8f5e9;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4caf50;
            border-radius: 3px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .stat-card {
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }

        .stat-card h4 {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .stat-card .value {
            color: #2c3e50;
            font-size: 2em;
            font-weight: bold;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }

        tr:hover {
            background-color: #f5f5f5;
        }

        .chart-container {
            margin: 30px 0;
            text-align: center;
        }

        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
        }

        ul {
            list-style-type: none;
            padding-left: 0;
        }

        ul li {
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
        }

        ul li:before {
            content: "▸";
            position: absolute;
            left: 0;
            color: #3498db;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Informe de Ofertas de Trabajo</h1>
            <p class="subtitle">Análisis del Mercado Laboral en Ciencia de Datos</p>
            <p class="date">Generado el {{ generation_date }}</p>
        </header>

        {% if executive_summary %}
        <div class="section">
            <h2>Resumen Ejecutivo</h2>
            <div class="summary-box">
                {% for insight in insights %}
                <div class="insight">{{ insight }}</div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div class="section">
            <h2>Estadísticas Generales</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Total de Ofertas</h4>
                    <div class="value">{{ stats.total_jobs }}</div>
                </div>
                <div class="stat-card">
                    <h4>Plataformas</h4>
                    <div class="value">{{ stats.platforms_count }}</div>
                </div>
                <div class="stat-card">
                    <h4>Empresas Únicas</h4>
                    <div class="value">{{ stats.companies_count }}</div>
                </div>
                <div class="stat-card">
                    <h4>Tecnologías Detectadas</h4>
                    <div class="value">{{ stats.unique_technologies }}</div>
                </div>
                <div class="stat-card">
                    <h4>Ofertas Remotas</h4>
                    <div class="value">{{ stats.remote_jobs }}</div>
                </div>
                <div class="stat-card">
                    <h4>Con Información Salarial</h4>
                    <div class="value">{{ stats.jobs_with_salary_info }}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Tecnologías Más Demandadas</h2>
            {% if charts.get('top_technologies') %}
            <div class="chart-container">
                <img src="{{ charts.top_technologies }}" alt="Top Tecnologías">
            </div>
            {% endif %}
            {% if technologies %}
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Tecnología</th>
                        <th>Menciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tech, count in technologies[:15] %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ tech }}</td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #7f8c8d; font-style: italic;">No se detectaron tecnologías en las ofertas recopiladas.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Empresas que Más Publican</h2>
            {% if charts.get('top_companies') %}
            <div class="chart-container">
                <img src="{{ charts.top_companies }}" alt="Top Empresas">
            </div>
            {% endif %}
            {% if companies %}
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Empresa</th>
                        <th>Ofertas</th>
                    </tr>
                </thead>
                <tbody>
                    {% for company, count in companies[:15] %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ company }}</td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #7f8c8d; font-style: italic;">No hay datos de empresas disponibles.</p>
            {% endif %}
        </div>

        {% if salary_data.has_data %}
        <div class="section">
            <h2>Análisis Salarial</h2>
            {% if charts.salary_distribution %}
            <div class="chart-container">
                <img src="{{ charts.salary_distribution }}" alt="Distribución Salarial">
            </div>
            {% endif %}
            <p><strong>{{ salary_data.percentage_with_salary|round(1) }}%</strong> de las ofertas incluyen información salarial.</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Salario Medio (Máximo)</h4>
                    <div class="value">{{ salary_data.max_salary.mean|round(0)|int|format_number }} €</div>
                </div>
                <div class="stat-card">
                    <h4>Salario Mediano (Máximo)</h4>
                    <div class="value">{{ salary_data.max_salary.median|round(0)|int|format_number }} €</div>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="section">
            <h2>Plataformas de Origen</h2>
            {% if charts.get('platforms_distribution') %}
            <div class="chart-container">
                <img src="{{ charts.platforms_distribution }}" alt="Distribución por Plataforma">
            </div>
            {% endif %}
            {% if platforms %}
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Plataforma</th>
                        <th>Ofertas</th>
                        <th>Porcentaje</th>
                    </tr>
                </thead>
                <tbody>
                    {% for platform, data in platforms.items() %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ platform }}</td>
                        <td>{{ data.count }}</td>
                        <td>{{ data.percentage|round(1) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #7f8c8d; font-style: italic;">No hay datos de plataformas disponibles.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Distribución Geográfica</h2>
            {% if charts.get('location_distribution') %}
            <div class="chart-container">
                <img src="{{ charts.location_distribution }}" alt="Distribución por Ubicación">
            </div>
            {% endif %}
            {% if locations %}
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Ubicación</th>
                        <th>Ofertas</th>
                    </tr>
                </thead>
                <tbody>
                    {% for location, count in locations[:15] %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ location }}</td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #7f8c8d; font-style: italic;">No hay datos de ubicaciones disponibles.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Tipos de Contrato</h2>
            {% if charts.get('contract_type_distribution') %}
            <div class="chart-container">
                <img src="{{ charts.contract_type_distribution }}" alt="Tipos de Contrato">
            </div>
            {% endif %}
            {% if contract_types %}
            <table>
                <thead>
                    <tr>
                        <th>Tipo de Contrato</th>
                        <th>Ofertas</th>
                        <th>Porcentaje</th>
                    </tr>
                </thead>
                <tbody>
                    {% for contract, data in contract_types.items() %}
                    <tr>
                        <td>{{ contract }}</td>
                        <td>{{ data.count }}</td>
                        <td>{{ data.percentage|round(1) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #7f8c8d; font-style: italic;">No hay datos de tipos de contrato disponibles.</p>
            {% endif %}
        </div>

        {% if charts.technology_correlation %}
        <div class="section">
            <h2>Combinaciones de Tecnologías</h2>
            <div class="chart-container">
                <img src="{{ charts.technology_correlation }}" alt="Correlaciones de Tecnologías">
            </div>
            <p>Estas son las combinaciones de tecnologías que más frecuentemente aparecen juntas en las ofertas.</p>
        </div>
        {% endif %}

        {% if charts.skills_wordcloud %}
        <div class="section">
            <h2>Nube de Habilidades</h2>
            <div class="chart-container">
                <img src="{{ charts.skills_wordcloud }}" alt="Nube de Habilidades">
            </div>
        </div>
        {% endif %}

        <div class="footer">
            <p>Informe generado automáticamente por Job Scraper</p>
            <p>© {{ current_year }} - Análisis de Mercado Laboral</p>
        </div>
    </div>
</body>
</html>
    """

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Inicializa el generador de informes.

        Args:
            config: Configuración del sistema
        """
        self.config = config or ConfigLoader()
        self.reports_config = self.config.get('reports', {})

        # Directorio de salida
        storage_config = self.config.get_storage_config()
        self.output_dir = Path(
            storage_config.get('reports_dir', './data/reports')
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ReportGenerator inicializado")

    def generate_html_report(
        self,
        analysis: Dict,
        insights: List[str],
        chart_paths: Dict[str, Path]
    ) -> Path:
        """
        Genera un informe HTML completo.

        Args:
            analysis: Diccionario con resultados del análisis
            insights: Lista de insights generados
            chart_paths: Diccionario con rutas a gráficos generados

        Returns:
            Ruta del archivo HTML generado
        """
        logger.info("Generando informe HTML...")

        # Preparar datos de plataformas
        platforms_data = {}
        if 'platforms' in analysis:
            total_jobs = analysis['total_jobs']
            for platform, count in analysis['platforms']['counts'].items():
                platforms_data[platform] = {
                    'count': count,
                    'percentage': (count / total_jobs * 100) if total_jobs > 0 else 0
                }

        # Preparar datos de tipos de contrato
        contract_types_data = {}
        if 'contract_types' in analysis:
            for contract_type, count in analysis['contract_types']['counts'].items():
                contract_types_data[contract_type] = {
                    'count': count,
                    'percentage': analysis['contract_types']['percentages'].get(contract_type, 0)
                }

        # Preparar datos para la plantilla
        template_data = {
            'generation_date': datetime.now().strftime('%d de %B de %Y, %H:%M'),
            'current_year': datetime.now().year,
            'executive_summary': self.reports_config.get('executive_summary', True),
            'insights': insights,
            'stats': analysis['summary_stats'],
            'technologies': list(analysis['technologies']['top_20'].items()) if analysis['technologies']['top_20'] else [],
            'companies': list(analysis['companies']['top_20'].items()) if analysis['companies']['top_20'] else [],
            'platforms': platforms_data,
            'locations': list(analysis['locations']['top_15'].items()) if analysis['locations']['top_15'] else [],
            'contract_types': contract_types_data,
            'salary_data': analysis['salaries'],
            'charts': {
                key: str(path.relative_to(self.output_dir.parent))
                for key, path in chart_paths.items()
            }
        }

        # Filtros personalizados para Jinja2
        def format_number(value):
            """Formatea un número con separadores de miles."""
            return f"{value:,}".replace(',', '.')

        # Renderizar plantilla
        template = Template(self.HTML_TEMPLATE)
        template.globals['format_number'] = format_number
        html_content = template.render(**template_data)

        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"informe_{timestamp}.html"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Informe HTML generado: {output_path}")
        return output_path

    def generate_markdown_report(
        self,
        analysis: Dict,
        insights: List[str]
    ) -> Path:
        """
        Genera un informe en formato Markdown.

        Args:
            analysis: Diccionario con resultados del análisis
            insights: Lista de insights generados

        Returns:
            Ruta del archivo Markdown generado
        """
        logger.info("Generando informe Markdown...")

        md_content = []

        # Encabezado
        md_content.append("# Informe de Ofertas de Trabajo - Ciencia de Datos\n")
        md_content.append(f"**Generado:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        md_content.append("---\n")

        # Resumen ejecutivo
        md_content.append("## Resumen Ejecutivo\n")
        for insight in insights:
            md_content.append(f"- {insight}\n")
        md_content.append("\n")

        # Estadísticas generales
        stats = analysis['summary_stats']
        md_content.append("## Estadísticas Generales\n")
        md_content.append(f"- **Total de ofertas:** {stats['total_jobs']}\n")
        md_content.append(f"- **Plataformas:** {stats['platforms_count']}\n")
        md_content.append(f"- **Empresas únicas:** {stats['companies_count']}\n")
        md_content.append(f"- **Tecnologías detectadas:** {stats['unique_technologies']}\n")
        md_content.append(f"- **Ofertas remotas:** {stats['remote_jobs']}\n")
        md_content.append("\n")

        # Top tecnologías
        md_content.append("## Top 15 Tecnologías\n")
        md_content.append("| # | Tecnología | Menciones |\n")
        md_content.append("|---|------------|----------|\n")
        for i, (tech, count) in enumerate(list(analysis['technologies']['top_20'].items())[:15], 1):
            md_content.append(f"| {i} | {tech} | {count} |\n")
        md_content.append("\n")

        # Top empresas
        md_content.append("## Top 15 Empresas\n")
        md_content.append("| # | Empresa | Ofertas |\n")
        md_content.append("|---|---------|--------|\n")
        for i, (company, count) in enumerate(list(analysis['companies']['top_20'].items())[:15], 1):
            md_content.append(f"| {i} | {company} | {count} |\n")
        md_content.append("\n")

        # Salarios
        if analysis['salaries'].get('has_data'):
            md_content.append("## Análisis Salarial\n")
            sal = analysis['salaries']
            md_content.append(f"- **Ofertas con salario:** {sal['percentage_with_salary']:.1f}%\n")
            md_content.append(f"- **Salario medio (máximo):** {sal['max_salary']['mean']:,.0f} €\n")
            md_content.append(f"- **Salario mediano (máximo):** {sal['max_salary']['median']:,.0f} €\n")
            md_content.append("\n")

        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"informe_{timestamp}.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(md_content)

        logger.info(f"Informe Markdown generado: {output_path}")
        return output_path
