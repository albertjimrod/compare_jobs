#!/bin/bash
# Script de configuración inicial para Job Scraper

echo "=== Job Scraper - Configuración Inicial ==="
echo ""

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detectado"
echo ""

# Preguntar método de instalación
echo "¿Cómo deseas instalar las dependencias?"
echo "1) Conda (recomendado)"
echo "2) pip + venv"
read -p "Selecciona (1 o 2): " choice

if [ "$choice" = "1" ]; then
    # Instalación con Conda
    echo ""
    echo "Instalando con Conda..."

    if ! command -v conda &> /dev/null; then
        echo "❌ Conda no está instalado"
        echo "Instala Miniconda desde: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi

    echo "Creando entorno conda..."
    conda env create -f environment.yml

    echo ""
    echo "✅ Entorno creado exitosamente"
    echo ""
    echo "Para activar el entorno ejecuta:"
    echo "  conda activate job-scraper-env"

elif [ "$choice" = "2" ]; then
    # Instalación con pip
    echo ""
    echo "Instalando con pip..."

    echo "Creando entorno virtual..."
    python3 -m venv venv

    echo "Activando entorno..."
    source venv/bin/activate

    echo "Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt

    echo ""
    echo "✅ Dependencias instaladas exitosamente"
    echo ""
    echo "Para activar el entorno ejecuta:"
    echo "  source venv/bin/activate"

else
    echo "Opción inválida"
    exit 1
fi

# Configurar archivo .env
echo ""
echo "Configurando variables de entorno..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Archivo .env creado (edítalo si necesitas configurar credenciales)"
else
    echo "ℹ️  Archivo .env ya existe"
fi

# Crear directorios necesarios
echo ""
echo "Creando directorios de datos..."
mkdir -p data/{raw,processed,reports,visualizations}
echo "✅ Directorios creados"

echo ""
echo "=== Configuración completada ==="
echo ""
echo "Próximos pasos:"
echo "1. Activa el entorno virtual"
echo "2. (Opcional) Edita config/config.yaml para personalizar la configuración"
echo "3. (Opcional) Edita .env si necesitas configurar credenciales"
echo "4. Ejecuta el scraper:"
echo "   python -m src.main"
echo ""
echo "Para un ejemplo rápido, ejecuta:"
echo "   python scripts/quick_start.py"
echo ""
