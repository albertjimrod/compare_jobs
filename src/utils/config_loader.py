"""
Módulo para cargar y gestionar la configuración del sistema.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Carga y gestiona la configuración del sistema."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el cargador de configuración.

        Args:
            config_path: Ruta al archivo de configuración YAML.
                        Si no se proporciona, usa la ruta por defecto.
        """
        # Cargar variables de entorno
        load_dotenv()

        # Determinar ruta del archivo de configuración
        if config_path is None:
            # Buscar config.yaml en el directorio config/
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._override_with_env_vars()

    def _load_config(self) -> Dict[str, Any]:
        """Carga el archivo de configuración YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {self.config_path}"
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _override_with_env_vars(self):
        """Sobrescribe valores de configuración con variables de entorno."""
        # Sobrescribir configuraciones de scraping si están definidas en .env
        if os.getenv('MAX_JOBS_PER_PLATFORM'):
            self.config['scraping']['max_jobs_per_platform'] = int(
                os.getenv('MAX_JOBS_PER_PLATFORM')
            )

        if os.getenv('DELAY_BETWEEN_REQUESTS'):
            self.config['scraping']['delay_between_requests'] = float(
                os.getenv('DELAY_BETWEEN_REQUESTS')
            )

        if os.getenv('HEADLESS_MODE'):
            self.config['scraping']['headless_mode'] = (
                os.getenv('HEADLESS_MODE').lower() == 'true'
            )

        if os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de puntos.

        Args:
            key: Clave en notación de puntos (ej: 'scraping.delay_between_requests')
            default: Valor por defecto si la clave no existe

        Returns:
            El valor de configuración o el valor por defecto
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_enabled_platforms(self) -> Dict[str, Dict]:
        """
        Obtiene las plataformas habilitadas ordenadas por prioridad.

        Returns:
            Diccionario de plataformas habilitadas con su configuración
        """
        platforms = self.config.get('platforms', {})
        enabled = {
            name: config
            for name, config in platforms.items()
            if config.get('enabled', False)
        }

        # Ordenar por prioridad
        return dict(
            sorted(
                enabled.items(),
                key=lambda x: x[1].get('priority', 999)
            )
        )

    def get_search_terms(self) -> Dict[str, list]:
        """Obtiene los términos de búsqueda configurados."""
        return self.config.get('search_terms', {
            'keywords': [],
            'locations': []
        })

    def get_storage_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de almacenamiento."""
        return self.config.get('storage', {})

    def get_analysis_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de análisis."""
        return self.config.get('analysis', {})

    def get_visualization_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de visualización."""
        return self.config.get('visualization', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de logging."""
        return self.config.get('logging', {})

    @staticmethod
    def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtiene una variable de entorno.

        Args:
            key: Nombre de la variable de entorno
            default: Valor por defecto si no existe

        Returns:
            El valor de la variable de entorno o el valor por defecto
        """
        return os.getenv(key, default)

    def __getitem__(self, key: str) -> Any:
        """Permite acceso tipo diccionario."""
        return self.get(key)

    def __repr__(self) -> str:
        """Representación en string del objeto."""
        return f"ConfigLoader(config_path='{self.config_path}')"
