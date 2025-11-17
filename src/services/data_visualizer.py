"""
Módulo para crear visualizaciones de datos de ofertas de trabajo.
"""

from typing import List, Dict, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import pandas as pd
from loguru import logger

from ..models.job_offer import JobOffer
from ..utils.config_loader import ConfigLoader


class DataVisualizer:
    """Crea visualizaciones de datos de ofertas de trabajo."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Inicializa el visualizador.

        Args:
            config: Configuración del sistema
        """
        self.config = config or ConfigLoader()
        self.viz_config = self.config.get_visualization_config()

        # Configurar estilo de matplotlib/seaborn
        style = self.viz_config.get('style', 'seaborn')
        plt.style.use(style if style in plt.style.available else 'default')

        # Configurar paleta de colores
        palette = self.viz_config.get('color_palette', 'husl')
        sns.set_palette(palette)

        # DPI para gráficos
        self.dpi = self.viz_config.get('dpi', 300)

        # Directorio de salida
        storage_config = self.config.get_storage_config()
        self.output_dir = Path(
            storage_config.get('visualizations_dir', './data/visualizations')
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("DataVisualizer inicializado")

    def create_all_visualizations(
        self,
        analysis: Dict,
        jobs: Optional[List[JobOffer]] = None
    ) -> Dict[str, Path]:
        """
        Crea todas las visualizaciones configuradas.

        Args:
            analysis: Diccionario con resultados del análisis
            jobs: Lista opcional de ofertas (necesaria para algunas visualizaciones)

        Returns:
            Diccionario con rutas de archivos generados
        """
        logger.info("Generando visualizaciones...")
        saved_files = {}

        charts_to_create = self.viz_config.get('charts', [])

        for chart_type in charts_to_create:
            try:
                if chart_type == 'top_technologies':
                    path = self.plot_top_technologies(analysis['technologies'])
                    saved_files['top_technologies'] = path

                elif chart_type == 'top_companies':
                    path = self.plot_top_companies(analysis['companies'])
                    saved_files['top_companies'] = path

                elif chart_type == 'salary_distribution':
                    if analysis['salaries'].get('has_data'):
                        path = self.plot_salary_distribution(analysis['salaries'])
                        saved_files['salary_distribution'] = path

                elif chart_type == 'location_distribution':
                    path = self.plot_location_distribution(analysis['locations'])
                    saved_files['location_distribution'] = path

                elif chart_type == 'contract_type_distribution':
                    path = self.plot_contract_types(analysis['contract_types'])
                    saved_files['contract_type_distribution'] = path

                elif chart_type == 'experience_level_distribution':
                    path = self.plot_experience_levels(analysis['experience_levels'])
                    saved_files['experience_level_distribution'] = path

                elif chart_type == 'technology_correlation':
                    path = self.plot_technology_correlations(
                        analysis['technology_correlations']
                    )
                    saved_files['technology_correlation'] = path

                elif chart_type == 'skills_wordcloud' and jobs:
                    path = self.create_skills_wordcloud(jobs)
                    saved_files['skills_wordcloud'] = path

            except Exception as e:
                logger.error(f"Error creando visualización '{chart_type}': {str(e)}")
                continue

        logger.info(f"Generadas {len(saved_files)} visualizaciones")
        return saved_files

    def plot_top_technologies(self, tech_data: Dict, top_n: int = 15) -> Path:
        """
        Crea gráfico de barras con las tecnologías más demandadas.

        Args:
            tech_data: Datos de tecnologías del análisis
            top_n: Número de tecnologías a mostrar

        Returns:
            Ruta del archivo generado
        """
        top_tech = dict(list(tech_data['top_20'].items())[:top_n])

        fig, ax = plt.subplots(figsize=(12, 8))

        technologies = list(top_tech.keys())
        counts = list(top_tech.values())

        bars = ax.barh(technologies, counts, color=sns.color_palette("viridis", len(technologies)))

        ax.set_xlabel('Número de menciones', fontsize=12)
        ax.set_ylabel('Tecnología', fontsize=12)
        ax.set_title(f'Top {top_n} Tecnologías Más Demandadas', fontsize=14, fontweight='bold')

        # Añadir valores en las barras
        for i, (tech, count) in enumerate(zip(technologies, counts)):
            ax.text(count, i, f' {count}', va='center', fontsize=10)

        plt.tight_layout()

        output_path = self.output_dir / 'top_technologies.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de tecnologías guardado en {output_path}")
        return output_path

    def plot_top_companies(self, company_data: Dict, top_n: int = 15) -> Path:
        """
        Crea gráfico de barras con las empresas que más publican.

        Args:
            company_data: Datos de empresas del análisis
            top_n: Número de empresas a mostrar

        Returns:
            Ruta del archivo generado
        """
        top_companies = dict(list(company_data['top_20'].items())[:top_n])

        fig, ax = plt.subplots(figsize=(12, 8))

        companies = list(top_companies.keys())
        counts = list(top_companies.values())

        bars = ax.barh(companies, counts, color=sns.color_palette("rocket", len(companies)))

        ax.set_xlabel('Número de ofertas', fontsize=12)
        ax.set_ylabel('Empresa', fontsize=12)
        ax.set_title(f'Top {top_n} Empresas con Más Ofertas', fontsize=14, fontweight='bold')

        # Añadir valores en las barras
        for i, (company, count) in enumerate(zip(companies, counts)):
            ax.text(count, i, f' {count}', va='center', fontsize=10)

        plt.tight_layout()

        output_path = self.output_dir / 'top_companies.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de empresas guardado en {output_path}")
        return output_path

    def plot_salary_distribution(self, salary_data: Dict) -> Path:
        """
        Crea histograma de distribución salarial.

        Args:
            salary_data: Datos salariales del análisis

        Returns:
            Ruta del archivo generado
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Información del salario mínimo
        min_stats = salary_data['min_salary']
        ax1.text(0.5, 0.7, 'Salario Mínimo', ha='center', fontsize=16, fontweight='bold')
        ax1.text(0.5, 0.5, f"Media: {min_stats['mean']:,.0f} €", ha='center', fontsize=12)
        ax1.text(0.5, 0.4, f"Mediana: {min_stats['median']:,.0f} €", ha='center', fontsize=12)
        ax1.text(0.5, 0.3, f"Rango: {min_stats['min']:,.0f} - {min_stats['max']:,.0f} €", ha='center', fontsize=12)
        ax1.axis('off')

        # Información del salario máximo
        max_stats = salary_data['max_salary']
        ax2.text(0.5, 0.7, 'Salario Máximo', ha='center', fontsize=16, fontweight='bold')
        ax2.text(0.5, 0.5, f"Media: {max_stats['mean']:,.0f} €", ha='center', fontsize=12)
        ax2.text(0.5, 0.4, f"Mediana: {max_stats['median']:,.0f} €", ha='center', fontsize=12)
        ax2.text(0.5, 0.3, f"Rango: {max_stats['min']:,.0f} - {max_stats['max']:,.0f} €", ha='center', fontsize=12)
        ax2.axis('off')

        plt.suptitle('Distribución Salarial', fontsize=16, fontweight='bold')
        plt.tight_layout()

        output_path = self.output_dir / 'salary_distribution.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de salarios guardado en {output_path}")
        return output_path

    def plot_location_distribution(self, location_data: Dict, top_n: int = 10) -> Path:
        """
        Crea gráfico de pie con distribución de ubicaciones.

        Args:
            location_data: Datos de ubicaciones del análisis
            top_n: Número de ubicaciones a mostrar

        Returns:
            Ruta del archivo generado
        """
        top_locations = dict(list(location_data['top_15'].items())[:top_n])

        fig, ax = plt.subplots(figsize=(10, 8))

        locations = list(top_locations.keys())
        counts = list(top_locations.values())

        colors = sns.color_palette("pastel", len(locations))
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=locations,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )

        # Mejorar legibilidad
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.set_title(f'Top {top_n} Ubicaciones', fontsize=14, fontweight='bold')

        plt.tight_layout()

        output_path = self.output_dir / 'location_distribution.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de ubicaciones guardado en {output_path}")
        return output_path

    def plot_contract_types(self, contract_data: Dict) -> Path:
        """
        Crea gráfico de barras con tipos de contrato.

        Args:
            contract_data: Datos de tipos de contrato del análisis

        Returns:
            Ruta del archivo generado
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        contracts = list(contract_data['counts'].keys())
        counts = list(contract_data['counts'].values())
        percentages = [contract_data['percentages'][c] for c in contracts]

        bars = ax.bar(contracts, counts, color=sns.color_palette("muted", len(contracts)))

        ax.set_xlabel('Tipo de Contrato', fontsize=12)
        ax.set_ylabel('Número de ofertas', fontsize=12)
        ax.set_title('Distribución por Tipo de Contrato', fontsize=14, fontweight='bold')

        # Rotar etiquetas si son muchas
        plt.xticks(rotation=45, ha='right')

        # Añadir valores y porcentajes
        for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{count}\n({pct:.1f}%)',
                ha='center',
                va='bottom',
                fontsize=9
            )

        plt.tight_layout()

        output_path = self.output_dir / 'contract_types.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de tipos de contrato guardado en {output_path}")
        return output_path

    def plot_experience_levels(self, experience_data: Dict) -> Path:
        """
        Crea gráfico de barras con niveles de experiencia.

        Args:
            experience_data: Datos de niveles de experiencia del análisis

        Returns:
            Ruta del archivo generado
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        levels = list(experience_data['counts'].keys())
        counts = list(experience_data['counts'].values())
        percentages = [experience_data['percentages'][l] for l in levels]

        bars = ax.bar(levels, counts, color=sns.color_palette("coolwarm", len(levels)))

        ax.set_xlabel('Nivel de Experiencia', fontsize=12)
        ax.set_ylabel('Número de ofertas', fontsize=12)
        ax.set_title('Distribución por Nivel de Experiencia', fontsize=14, fontweight='bold')

        plt.xticks(rotation=45, ha='right')

        # Añadir valores y porcentajes
        for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{count}\n({pct:.1f}%)',
                ha='center',
                va='bottom',
                fontsize=9
            )

        plt.tight_layout()

        output_path = self.output_dir / 'experience_levels.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de niveles de experiencia guardado en {output_path}")
        return output_path

    def plot_technology_correlations(self, correlation_data: Dict, top_n: int = 15) -> Path:
        """
        Crea gráfico de barras con pares de tecnologías correlacionadas.

        Args:
            correlation_data: Datos de correlaciones del análisis
            top_n: Número de pares a mostrar

        Returns:
            Ruta del archivo generado
        """
        top_pairs = dict(list(correlation_data['top_20_pairs'].items())[:top_n])

        fig, ax = plt.subplots(figsize=(12, 8))

        pairs = list(top_pairs.keys())
        counts = list(top_pairs.values())

        bars = ax.barh(pairs, counts, color=sns.color_palette("flare", len(pairs)))

        ax.set_xlabel('Frecuencia de co-ocurrencia', fontsize=12)
        ax.set_ylabel('Par de Tecnologías', fontsize=12)
        ax.set_title(f'Top {top_n} Combinaciones de Tecnologías', fontsize=14, fontweight='bold')

        # Añadir valores en las barras
        for i, (pair, count) in enumerate(zip(pairs, counts)):
            ax.text(count, i, f' {count}', va='center', fontsize=10)

        plt.tight_layout()

        output_path = self.output_dir / 'technology_correlations.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico de correlaciones guardado en {output_path}")
        return output_path

    def create_skills_wordcloud(self, jobs: List[JobOffer]) -> Path:
        """
        Crea nube de palabras con habilidades.

        Args:
            jobs: Lista de ofertas de trabajo

        Returns:
            Ruta del archivo generado
        """
        # Recopilar todas las habilidades
        all_skills = []
        for job in jobs:
            all_skills.extend(job.skills)
            all_skills.extend(job.technologies)

        # Crear texto para la nube
        text = ' '.join(all_skills)

        # Generar nube de palabras
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5
        ).generate(text)

        # Crear figura
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Habilidades y Tecnologías Más Demandadas', fontsize=16, fontweight='bold')

        plt.tight_layout(pad=0)

        output_path = self.output_dir / 'skills_wordcloud.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"Nube de palabras guardada en {output_path}")
        return output_path
