#!/usr/bin/env python
"""
Script de verificación de instalación.
Verifica que todos los archivos y directorios necesarios estén presentes.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent

# Archivos requeridos
REQUIRED_FILES = [
    'requirements.txt',
    'environment.yml',
    '.env.example',
    'config/config.yaml',
    'README.md',
    'src/main.py',
    'src/__init__.py',
    'src/models/job_offer.py',
    'src/scrapers/base_scraper.py',
    'src/services/data_storage.py',
    'src/utils/config_loader.py',
    'scripts/setup.sh',
    'scripts/quick_start.py',
]

# Directorios requeridos
REQUIRED_DIRS = [
    'src',
    'src/models',
    'src/scrapers',
    'src/services',
    'src/utils',
    'config',
    'data',
    'data/raw',
    'data/processed',
    'data/reports',
    'data/visualizations',
    'scripts',
    'docs',
    'tests',
]


def check_files() -> Tuple[List[str], List[str]]:
    """Verifica archivos requeridos."""
    found = []
    missing = []

    for file_path in REQUIRED_FILES:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            found.append(file_path)
        else:
            missing.append(file_path)

    return found, missing


def check_directories() -> Tuple[List[str], List[str]]:
    """Verifica directorios requeridos."""
    found = []
    missing = []

    for dir_path in REQUIRED_DIRS:
        full_path = ROOT_DIR / dir_path
        if full_path.exists() and full_path.is_dir():
            found.append(dir_path)
        else:
            missing.append(dir_path)

    return found, missing


def check_python_version() -> bool:
    """Verifica versión de Python."""
    version_info = sys.version_info
    required_major = 3
    required_minor = 11

    return (version_info.major >= required_major and
            version_info.minor >= required_minor)


def main():
    """Función principal."""
    print("=" * 60)
    print("JOB SCRAPER - VERIFICACIÓN DE INSTALACIÓN")
    print("=" * 60)
    print()

    # Verificar Python
    print("1. Verificando versión de Python...")
    if check_python_version():
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("   ⚠️  Se requiere Python 3.11 o superior")
    print()

    # Verificar archivos
    print("2. Verificando archivos requeridos...")
    found_files, missing_files = check_files()

    if not missing_files:
        print(f"   ✅ Todos los archivos presentes ({len(found_files)}/{len(REQUIRED_FILES)})")
    else:
        print(f"   ⚠️  Archivos encontrados: {len(found_files)}/{len(REQUIRED_FILES)}")
        print("   ❌ Archivos faltantes:")
        for file_path in missing_files:
            print(f"      - {file_path}")
    print()

    # Verificar directorios
    print("3. Verificando directorios...")
    found_dirs, missing_dirs = check_directories()

    if not missing_dirs:
        print(f"   ✅ Todos los directorios presentes ({len(found_dirs)}/{len(REQUIRED_DIRS)})")
    else:
        print(f"   ⚠️  Directorios encontrados: {len(found_dirs)}/{len(REQUIRED_DIRS)}")
        print("   ❌ Directorios faltantes:")
        for dir_path in missing_dirs:
            print(f"      - {dir_path}")
    print()

    # Verificar archivo .env
    print("4. Verificando configuración...")
    env_file = ROOT_DIR / '.env'
    if env_file.exists():
        print("   ✅ Archivo .env configurado")
    else:
        print("   ℹ️  Archivo .env no encontrado (opcional)")
        print("      Ejecuta: cp .env.example .env")
    print()

    # Verificar dependencias
    print("5. Verificando dependencias...")
    try:
        import pandas
        import requests
        import bs4
        import loguru
        print("   ✅ Dependencias principales instaladas")
    except ImportError as e:
        print(f"   ❌ Falta instalar dependencias: {e}")
        print("      Ejecuta: pip install -r requirements.txt")
        print("      O: conda env create -f environment.yml")
    print()

    # Resumen
    print("=" * 60)
    if not missing_files and not missing_dirs:
        print("✅ INSTALACIÓN VERIFICADA - TODO CORRECTO")
        print()
        print("Próximos pasos:")
        print("1. Si aún no has instalado dependencias:")
        print("   - Con Conda: conda env create -f environment.yml")
        print("   - Con pip: pip install -r requirements.txt")
        print("2. (Opcional) Copia y edita .env: cp .env.example .env")
        print("3. Ejecuta el scraper: python -m src.main")
        print("4. O prueba el ejemplo rápido: python scripts/quick_start.py")
    else:
        print("⚠️  INSTALACIÓN INCOMPLETA")
        print()
        print("Por favor:")
        print("1. Verifica que clonaste el repositorio completo")
        print("2. Revisa los archivos y directorios faltantes arriba")
        print("3. Si el problema persiste, vuelve a clonar el repositorio")
    print("=" * 60)


if __name__ == '__main__':
    main()
