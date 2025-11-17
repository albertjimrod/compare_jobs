"""
Módulo para analizar ofertas de trabajo y extraer insights.
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter
import pandas as pd
import numpy as np
from loguru import logger

from ..models.job_offer import JobOffer
from ..utils.config_loader import ConfigLoader


class DataAnalyzer:
    """Analiza datos de ofertas de trabajo para extraer insights."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Inicializa el analizador.

        Args:
            config: Configuración del sistema
        """
        self.config = config or ConfigLoader()
        self.analysis_config = self.config.get_analysis_config()
        logger.info("DataAnalyzer inicializado")

    def _preprocess_jobs(self, jobs: List[JobOffer]) -> List[JobOffer]:
        """
        Preprocesa las ofertas extrayendo tecnologías y skills de las descripciones.
        Esto se hace aquí (lazy loading) para acelerar el scraping.

        Args:
            jobs: Lista de ofertas

        Returns:
            Lista de ofertas con tecnologías y skills extraídas
        """
        import re

        logger.info("Extrayendo tecnologías y habilidades de las descripciones...")

        # Obtener configuración de tecnologías y skills
        tech_config = self.config.get('analysis.technologies', {})
        skills_list = self.config.get('analysis.skills', [])

        for idx, job in enumerate(jobs, 1):
            # Solo extraer si están vacías (lazy loading)
            if not job.technologies and job.description:
                technologies = []
                for category, tech_list in tech_config.items():
                    for tech in tech_list:
                        pattern = r'\b' + re.escape(tech) + r'\b'
                        if re.search(pattern, job.description, re.IGNORECASE):
                            technologies.append(tech)
                job.technologies = list(set(technologies))

            if not job.skills and job.description:
                skills = []
                for skill in skills_list:
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, job.description, re.IGNORECASE):
                        skills.append(skill)
                job.skills = list(set(skills))

            if idx % 10 == 0:
                logger.debug(f"Procesadas {idx}/{len(jobs)} ofertas...")

        logger.info(f"✓ Preprocesamiento completado ({len(jobs)} ofertas)")
        return jobs

    def analyze(self, jobs: List[JobOffer]) -> Dict:
        """
        Realiza un análisis completo de las ofertas.

        Args:
            jobs: Lista de ofertas a analizar

        Returns:
            Diccionario con resultados del análisis
        """
        if not jobs:
            logger.warning("No hay ofertas para analizar")
            return {}

        logger.info(f"Analizando {len(jobs)} ofertas de trabajo...")

        # Preprocesar: extraer tecnologías y skills si no están presentes
        jobs = self._preprocess_jobs(jobs)

        analysis = {
            'total_jobs': len(jobs),
            'platforms': self._analyze_platforms(jobs),
            'technologies': self._analyze_technologies(jobs),
            'skills': self._analyze_skills(jobs),
            'companies': self._analyze_companies(jobs),
            'locations': self._analyze_locations(jobs),
            'salaries': self._analyze_salaries(jobs),
            'work_location_types': self._analyze_work_location_types(jobs),
            'contract_types': self._analyze_contract_types(jobs),
            'experience_levels': self._analyze_experience_levels(jobs),
            'technology_correlations': self._analyze_technology_correlations(jobs),
            'summary_stats': self._generate_summary_stats(jobs)
        }

        logger.info("Análisis completado")
        return analysis

    def _analyze_platforms(self, jobs: List[JobOffer]) -> Dict:
        """Analiza distribución por plataforma."""
        platform_counts = Counter(job.platform for job in jobs)
        total = len(jobs)

        return {
            'counts': dict(platform_counts),
            'percentages': {
                platform: (count / total) * 100
                for platform, count in platform_counts.items()
            },
            'total_platforms': len(platform_counts)
        }

    def _analyze_technologies(self, jobs: List[JobOffer]) -> Dict:
        """Analiza tecnologías más demandadas."""
        all_technologies = []
        for job in jobs:
            all_technologies.extend(job.technologies)

        tech_counts = Counter(all_technologies)
        total_mentions = sum(tech_counts.values())

        # Top 20 tecnologías
        top_technologies = dict(tech_counts.most_common(20))

        return {
            'counts': dict(tech_counts),
            'top_20': top_technologies,
            'total_unique': len(tech_counts),
            'total_mentions': total_mentions,
            'average_per_job': total_mentions / len(jobs) if jobs else 0
        }

    def _analyze_skills(self, jobs: List[JobOffer]) -> Dict:
        """Analiza habilidades más demandadas."""
        all_skills = []
        for job in jobs:
            all_skills.extend(job.skills)

        skill_counts = Counter(all_skills)
        total_mentions = sum(skill_counts.values())

        # Top 15 habilidades
        top_skills = dict(skill_counts.most_common(15))

        return {
            'counts': dict(skill_counts),
            'top_15': top_skills,
            'total_unique': len(skill_counts),
            'total_mentions': total_mentions,
            'average_per_job': total_mentions / len(jobs) if jobs else 0
        }

    def _analyze_companies(self, jobs: List[JobOffer]) -> Dict:
        """Analiza empresas que más publican ofertas."""
        company_counts = Counter(job.company for job in jobs)

        # Top 20 empresas
        top_companies = dict(company_counts.most_common(20))

        return {
            'counts': dict(company_counts),
            'top_20': top_companies,
            'total_unique': len(company_counts)
        }

    def _analyze_locations(self, jobs: List[JobOffer]) -> Dict:
        """Analiza distribución geográfica."""
        location_counts = Counter(
            job.location for job in jobs if job.location
        )

        # Top 15 ubicaciones
        top_locations = dict(location_counts.most_common(15))

        return {
            'counts': dict(location_counts),
            'top_15': top_locations,
            'total_unique': len(location_counts)
        }

    def _analyze_salaries(self, jobs: List[JobOffer]) -> Dict:
        """Analiza información salarial."""
        salaries_min = [
            job.salary_min for job in jobs
            if job.salary_min is not None and job.salary_min > 0
        ]
        salaries_max = [
            job.salary_max for job in jobs
            if job.salary_max is not None and job.salary_max > 0
        ]

        if not salaries_min and not salaries_max:
            return {
                'has_data': False,
                'jobs_with_salary': 0,
                'percentage_with_salary': 0
            }

        return {
            'has_data': True,
            'jobs_with_salary': len(salaries_min),
            'percentage_with_salary': (len(salaries_min) / len(jobs)) * 100,
            'min_salary': {
                'mean': np.mean(salaries_min) if salaries_min else 0,
                'median': np.median(salaries_min) if salaries_min else 0,
                'std': np.std(salaries_min) if salaries_min else 0,
                'min': np.min(salaries_min) if salaries_min else 0,
                'max': np.max(salaries_min) if salaries_min else 0
            },
            'max_salary': {
                'mean': np.mean(salaries_max) if salaries_max else 0,
                'median': np.median(salaries_max) if salaries_max else 0,
                'std': np.std(salaries_max) if salaries_max else 0,
                'min': np.min(salaries_max) if salaries_max else 0,
                'max': np.max(salaries_max) if salaries_max else 0
            }
        }

    def _analyze_work_location_types(self, jobs: List[JobOffer]) -> Dict:
        """Analiza tipos de ubicación de trabajo."""
        location_type_counts = Counter(
            job.work_location_type.value for job in jobs
        )
        total = len(jobs)

        return {
            'counts': dict(location_type_counts),
            'percentages': {
                loc_type: (count / total) * 100
                for loc_type, count in location_type_counts.items()
            }
        }

    def _analyze_contract_types(self, jobs: List[JobOffer]) -> Dict:
        """Analiza tipos de contrato."""
        contract_counts = Counter(
            job.contract_type.value for job in jobs
        )
        total = len(jobs)

        return {
            'counts': dict(contract_counts),
            'percentages': {
                contract: (count / total) * 100
                for contract, count in contract_counts.items()
            }
        }

    def _analyze_experience_levels(self, jobs: List[JobOffer]) -> Dict:
        """Analiza niveles de experiencia."""
        experience_counts = Counter(
            job.experience_level.value for job in jobs
        )
        total = len(jobs)

        return {
            'counts': dict(experience_counts),
            'percentages': {
                level: (count / total) * 100
                for level, count in experience_counts.items()
            }
        }

    def _analyze_technology_correlations(self, jobs: List[JobOffer]) -> Dict:
        """
        Analiza qué tecnologías suelen aparecer juntas.

        Returns:
            Diccionario con pares de tecnologías y su frecuencia de co-ocurrencia
        """
        correlations = Counter()

        for job in jobs:
            techs = job.technologies
            if len(techs) < 2:
                continue

            # Generar todos los pares posibles
            for i, tech1 in enumerate(techs):
                for tech2 in techs[i + 1:]:
                    # Ordenar alfabéticamente para evitar duplicados (A,B) y (B,A)
                    pair = tuple(sorted([tech1, tech2]))
                    correlations[pair] += 1

        # Top 20 correlaciones
        top_correlations = dict(correlations.most_common(20))

        return {
            'top_20_pairs': {
                f"{pair[0]} + {pair[1]}": count
                for pair, count in top_correlations.items()
            },
            'total_pairs': len(correlations)
        }

    def _generate_summary_stats(self, jobs: List[JobOffer]) -> Dict:
        """Genera estadísticas resumidas."""
        return {
            'total_jobs': len(jobs),
            'platforms_count': len(set(job.platform for job in jobs)),
            'companies_count': len(set(job.company for job in jobs)),
            'unique_technologies': len(set(
                tech for job in jobs for tech in job.technologies
            )),
            'unique_skills': len(set(
                skill for job in jobs for skill in job.skills
            )),
            'jobs_with_salary_info': sum(
                1 for job in jobs if job.salary_min or job.salary_max
            ),
            'remote_jobs': sum(
                1 for job in jobs
                if 'remot' in job.work_location_type.value.lower()
            ),
            'date_range': {
                'earliest_scraped': min(
                    (job.scraped_date for job in jobs),
                    default=None
                ),
                'latest_scraped': max(
                    (job.scraped_date for job in jobs),
                    default=None
                )
            }
        }

    def to_dataframe(self, jobs: List[JobOffer]) -> pd.DataFrame:
        """
        Convierte lista de ofertas a DataFrame de pandas.

        Args:
            jobs: Lista de ofertas

        Returns:
            DataFrame con los datos
        """
        data = [job.to_dict() for job in jobs]
        df = pd.DataFrame(data)

        # Convertir listas a strings para mejor visualización
        list_columns = ['technologies', 'skills', 'benefits']
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: ', '.join(x) if isinstance(x, list) else x
                )

        return df

    def export_analysis_to_json(self, analysis: Dict, output_path: str):
        """
        Exporta el análisis a un archivo JSON.

        Args:
            analysis: Diccionario con análisis
            output_path: Ruta del archivo de salida
        """
        import json
        from datetime import datetime

        # Convertir objetos datetime a strings
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=datetime_handler)

        logger.info(f"Análisis exportado a {output_path}")

    def get_insights(self, analysis: Dict) -> List[str]:
        """
        Genera insights legibles del análisis.

        Args:
            analysis: Diccionario con resultados del análisis

        Returns:
            Lista de insights en formato texto
        """
        insights = []

        # Total de ofertas
        insights.append(f"📊 Total de ofertas analizadas: {analysis['total_jobs']}")

        # Tecnologías más demandadas
        if analysis['technologies']['top_20']:
            top_tech = list(analysis['technologies']['top_20'].items())[0]
            insights.append(
                f"💻 Tecnología más demandada: {top_tech[0]} ({top_tech[1]} menciones)"
            )

        # Habilidades más demandadas
        if analysis['skills']['top_15']:
            top_skill = list(analysis['skills']['top_15'].items())[0]
            insights.append(
                f"🎯 Habilidad más demandada: {top_skill[0]} ({top_skill[1]} menciones)"
            )

        # Empresa que más publica
        if analysis['companies']['top_20']:
            top_company = list(analysis['companies']['top_20'].items())[0]
            insights.append(
                f"🏢 Empresa con más ofertas: {top_company[0]} ({top_company[1]} ofertas)"
            )

        # Información salarial
        if analysis['salaries']['has_data']:
            avg_salary = analysis['salaries']['max_salary']['mean']
            insights.append(
                f"💰 Salario promedio máximo: {avg_salary:,.0f} EUR/año"
            )

        # Trabajo remoto
        remote_pct = analysis['work_location_types']['percentages'].get('Remoto', 0)
        insights.append(f"🏠 Ofertas remotas: {remote_pct:.1f}%")

        return insights
