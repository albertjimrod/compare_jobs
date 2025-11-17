"""
Modelo de datos para ofertas de trabajo.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
import json


class ContractType(Enum):
    """Tipos de contrato laboral."""
    FULL_TIME = "Tiempo completo"
    PART_TIME = "Tiempo parcial"
    FREELANCE = "Freelance"
    CONTRACT = "Contrato"
    INTERNSHIP = "Prácticas"
    TEMPORARY = "Temporal"
    UNKNOWN = "Desconocido"


class WorkLocation(Enum):
    """Tipos de ubicación de trabajo."""
    REMOTE = "Remoto"
    ONSITE = "Presencial"
    HYBRID = "Híbrido"
    UNKNOWN = "Desconocido"


class ExperienceLevel(Enum):
    """Nivel de experiencia requerido."""
    ENTRY = "Junior"
    MID = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    UNKNOWN = "Desconocido"


@dataclass
class JobOffer:
    """Representa una oferta de trabajo."""

    # Identificación
    title: str
    company: str
    platform: str
    url: str

    # Detalles del trabajo
    description: str = ""
    location: str = ""
    work_location_type: WorkLocation = WorkLocation.UNKNOWN
    contract_type: ContractType = ContractType.UNKNOWN
    experience_level: ExperienceLevel = ExperienceLevel.UNKNOWN

    # Información salarial
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "EUR"
    salary_period: str = "anual"  # anual, mensual, hora

    # Tecnologías y habilidades
    technologies: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

    # Metadata
    posted_date: Optional[datetime] = None
    scraped_date: datetime = field(default_factory=datetime.now)
    job_id: Optional[str] = None

    # Información adicional
    benefits: List[str] = field(default_factory=list)
    industry: str = ""
    company_size: str = ""
    extra_data: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convierte la oferta a diccionario."""
        data = asdict(self)

        # Convertir enums a sus valores
        data['work_location_type'] = self.work_location_type.value
        data['contract_type'] = self.contract_type.value
        data['experience_level'] = self.experience_level.value

        # Convertir fechas a strings
        if self.posted_date:
            data['posted_date'] = self.posted_date.isoformat()
        data['scraped_date'] = self.scraped_date.isoformat()

        return data

    def to_json(self) -> str:
        """Convierte la oferta a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'JobOffer':
        """Crea una oferta desde un diccionario."""
        # Convertir strings a enums
        if isinstance(data.get('work_location_type'), str):
            data['work_location_type'] = WorkLocation(data['work_location_type'])
        if isinstance(data.get('contract_type'), str):
            data['contract_type'] = ContractType(data['contract_type'])
        if isinstance(data.get('experience_level'), str):
            data['experience_level'] = ExperienceLevel(data['experience_level'])

        # Convertir strings a fechas
        if data.get('posted_date') and isinstance(data['posted_date'], str):
            data['posted_date'] = datetime.fromisoformat(data['posted_date'])
        if data.get('scraped_date') and isinstance(data['scraped_date'], str):
            data['scraped_date'] = datetime.fromisoformat(data['scraped_date'])

        return cls(**data)

    def __str__(self) -> str:
        """Representación en string de la oferta."""
        return (
            f"JobOffer(title='{self.title}', company='{self.company}', "
            f"platform='{self.platform}', location='{self.location}')"
        )

    def __repr__(self) -> str:
        """Representación detallada de la oferta."""
        return self.__str__()
