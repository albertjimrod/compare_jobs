"""
Sistema de almacenamiento de datos para ofertas de trabajo.
Soporta múltiples formatos: CSV, JSON, SQLite.
"""

import json
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from ..models.job_offer import JobOffer
from ..utils.config_loader import ConfigLoader

Base = declarative_base()


class JobOfferDB(Base):
    """Modelo de base de datos para ofertas de trabajo."""

    __tablename__ = 'job_offers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    platform = Column(String, nullable=False, index=True)
    url = Column(String)
    description = Column(Text)
    location = Column(String)
    work_location_type = Column(String)
    contract_type = Column(String)
    experience_level = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String)
    salary_period = Column(String)
    technologies = Column(Text)  # JSON string
    skills = Column(Text)  # JSON string
    posted_date = Column(DateTime)
    scraped_date = Column(DateTime, nullable=False)
    benefits = Column(Text)  # JSON string
    industry = Column(String)
    company_size = Column(String)
    extra_data = Column(Text)  # JSON string


class DataStorage:
    """Gestiona el almacenamiento de ofertas de trabajo."""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Inicializa el sistema de almacenamiento.

        Args:
            config: Configuración del sistema
        """
        self.config = config or ConfigLoader()
        self.storage_config = self.config.get_storage_config()

        # Configurar directorios
        self.data_dir = Path(self.storage_config.get('data_dir', './data'))
        self.raw_dir = Path(self.storage_config.get('raw_dir', './data/raw'))
        self.processed_dir = Path(self.storage_config.get('processed_dir', './data/processed'))

        # Crear directorios si no existen
        self._ensure_directories()

        # Configurar SQLite
        self.db_path = self.data_dir / 'jobs.db'
        self.engine = None
        self.Session = None

        if self.storage_config.get('save_sqlite', True):
            self._setup_database()

        logger.info("Sistema de almacenamiento inicializado")

    def _ensure_directories(self):
        """Crea los directorios necesarios si no existen."""
        for directory in [self.data_dir, self.raw_dir, self.processed_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _setup_database(self):
        """Configura la base de datos SQLite."""
        try:
            db_url = f"sqlite:///{self.db_path}"
            self.engine = create_engine(db_url, echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"Base de datos SQLite configurada en {self.db_path}")
        except Exception as e:
            logger.error(f"Error configurando base de datos: {str(e)}")
            self.engine = None
            self.Session = None

    def save_jobs(
        self,
        jobs: List[JobOffer],
        prefix: str = "jobs",
        save_csv: Optional[bool] = None,
        save_json: Optional[bool] = None,
        save_sqlite: Optional[bool] = None
    ) -> Dict[str, Path]:
        """
        Guarda ofertas de trabajo en los formatos especificados.

        Args:
            jobs: Lista de ofertas a guardar
            prefix: Prefijo para nombres de archivo
            save_csv: Si guardar en CSV (None usa config)
            save_json: Si guardar en JSON (None usa config)
            save_sqlite: Si guardar en SQLite (None usa config)

        Returns:
            Diccionario con rutas de archivos guardados
        """
        if not jobs:
            logger.warning("No hay ofertas para guardar")
            return {}

        # Usar configuración si no se especifica
        if save_csv is None:
            save_csv = self.storage_config.get('save_csv', True)
        if save_json is None:
            save_json = self.storage_config.get('save_json', True)
        if save_sqlite is None:
            save_sqlite = self.storage_config.get('save_sqlite', True)

        # Generar timestamp para nombres de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}

        # Guardar en CSV
        if save_csv:
            try:
                csv_path = self.raw_dir / f"{prefix}_{timestamp}.csv"
                self._save_to_csv(jobs, csv_path)
                saved_files['csv'] = csv_path
                logger.info(f"Guardadas {len(jobs)} ofertas en CSV: {csv_path}")
            except Exception as e:
                logger.error(f"Error guardando CSV: {str(e)}")

        # Guardar en JSON
        if save_json:
            try:
                json_path = self.raw_dir / f"{prefix}_{timestamp}.json"
                self._save_to_json(jobs, json_path)
                saved_files['json'] = json_path
                logger.info(f"Guardadas {len(jobs)} ofertas en JSON: {json_path}")
            except Exception as e:
                logger.error(f"Error guardando JSON: {str(e)}")

        # Guardar en SQLite
        if save_sqlite and self.engine:
            try:
                self._save_to_sqlite(jobs)
                saved_files['sqlite'] = self.db_path
                logger.info(f"Guardadas {len(jobs)} ofertas en SQLite: {self.db_path}")
            except Exception as e:
                logger.error(f"Error guardando en SQLite: {str(e)}")

        return saved_files

    def _save_to_csv(self, jobs: List[JobOffer], file_path: Path):
        """Guarda ofertas en formato CSV."""
        # Convertir a DataFrame
        data = [job.to_dict() for job in jobs]
        df = pd.DataFrame(data)

        # Convertir listas a strings para CSV
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x
                )

        # Guardar
        df.to_csv(file_path, index=False, encoding='utf-8')

    def _save_to_json(self, jobs: List[JobOffer], file_path: Path):
        """Guarda ofertas en formato JSON."""
        data = [job.to_dict() for job in jobs]

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_to_sqlite(self, jobs: List[JobOffer]):
        """Guarda ofertas en base de datos SQLite."""
        if not self.Session:
            logger.warning("Base de datos no configurada")
            return

        session = self.Session()

        try:
            for job in jobs:
                # Convertir JobOffer a JobOfferDB
                db_job = JobOfferDB(
                    job_id=job.job_id,
                    title=job.title,
                    company=job.company,
                    platform=job.platform,
                    url=job.url,
                    description=job.description,
                    location=job.location,
                    work_location_type=job.work_location_type.value,
                    contract_type=job.contract_type.value,
                    experience_level=job.experience_level.value,
                    salary_min=job.salary_min,
                    salary_max=job.salary_max,
                    salary_currency=job.salary_currency,
                    salary_period=job.salary_period,
                    technologies=json.dumps(job.technologies),
                    skills=json.dumps(job.skills),
                    posted_date=job.posted_date,
                    scraped_date=job.scraped_date,
                    benefits=json.dumps(job.benefits),
                    industry=job.industry,
                    company_size=job.company_size,
                    extra_data=json.dumps(job.extra_data)
                )

                session.add(db_job)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def load_jobs_from_csv(self, file_path: Path) -> List[JobOffer]:
        """
        Carga ofertas desde un archivo CSV.

        Args:
            file_path: Ruta al archivo CSV

        Returns:
            Lista de JobOffer
        """
        df = pd.read_csv(file_path)
        jobs = []

        for _, row in df.iterrows():
            try:
                job_dict = row.to_dict()

                # Convertir strings JSON a listas/dicts
                for key in ['technologies', 'skills', 'benefits', 'extra_data']:
                    if key in job_dict and isinstance(job_dict[key], str):
                        try:
                            job_dict[key] = json.loads(job_dict[key])
                        except:
                            job_dict[key] = []

                job = JobOffer.from_dict(job_dict)
                jobs.append(job)
            except Exception as e:
                logger.warning(f"Error cargando trabajo: {str(e)}")
                continue

        logger.info(f"Cargadas {len(jobs)} ofertas desde {file_path}")
        return jobs

    def load_jobs_from_json(self, file_path: Path) -> List[JobOffer]:
        """
        Carga ofertas desde un archivo JSON.

        Args:
            file_path: Ruta al archivo JSON

        Returns:
            Lista de JobOffer
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        jobs = [JobOffer.from_dict(job_dict) for job_dict in data]
        logger.info(f"Cargadas {len(jobs)} ofertas desde {file_path}")
        return jobs

    def get_all_jobs_from_db(self) -> List[JobOffer]:
        """
        Obtiene todas las ofertas de la base de datos.

        Returns:
            Lista de JobOffer
        """
        if not self.Session:
            logger.warning("Base de datos no configurada")
            return []

        session = self.Session()
        jobs = []

        try:
            db_jobs = session.query(JobOfferDB).all()

            for db_job in db_jobs:
                job_dict = {
                    'job_id': db_job.job_id,
                    'title': db_job.title,
                    'company': db_job.company,
                    'platform': db_job.platform,
                    'url': db_job.url,
                    'description': db_job.description,
                    'location': db_job.location,
                    'work_location_type': db_job.work_location_type,
                    'contract_type': db_job.contract_type,
                    'experience_level': db_job.experience_level,
                    'salary_min': db_job.salary_min,
                    'salary_max': db_job.salary_max,
                    'salary_currency': db_job.salary_currency,
                    'salary_period': db_job.salary_period,
                    'technologies': json.loads(db_job.technologies) if db_job.technologies else [],
                    'skills': json.loads(db_job.skills) if db_job.skills else [],
                    'posted_date': db_job.posted_date,
                    'scraped_date': db_job.scraped_date,
                    'benefits': json.loads(db_job.benefits) if db_job.benefits else [],
                    'industry': db_job.industry,
                    'company_size': db_job.company_size,
                    'extra_data': json.loads(db_job.extra_data) if db_job.extra_data else {}
                }

                jobs.append(JobOffer.from_dict(job_dict))

        finally:
            session.close()

        logger.info(f"Cargadas {len(jobs)} ofertas desde base de datos")
        return jobs
