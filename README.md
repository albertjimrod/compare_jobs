# Job Scraper - Ciencia de Datos

Sistema automatizado para recopilar, analizar y visualizar ofertas laborales de ciencia de datos desde múltiples plataformas de empleo.

## 📋 Descripción

Job Scraper es una herramienta integral que automatiza el proceso de búsqueda y análisis de ofertas de trabajo en el campo de la ciencia de datos. Recopila ofertas de hasta 19 plataformas diferentes, analiza las tecnologías y habilidades más demandadas, y genera informes visuales completos.

### Características Principales

- 🔍 **Scraping Multi-Plataforma**: Recopila ofertas de Indeed, InfoJobs, LinkedIn, Glassdoor, y más
- 💾 **Almacenamiento Flexible**: Guarda datos en CSV, JSON y SQLite
- 📊 **Análisis Avanzado**: Detecta tecnologías demandadas, empresas activas y patrones de mercado
- 📈 **Visualizaciones**: Genera gráficos profesionales y nubes de palabras
- 📄 **Informes HTML**: Crea informes completos y profesionales automáticamente
- ⚙️ **Altamente Configurable**: Personaliza búsquedas, plataformas y análisis

## 🚀 Instalación

### Requisitos Previos

- Python 3.11 o superior
- Conda (recomendado) o pip

### Opción 1: Usar Conda (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs

# Crear entorno con conda
conda env create -f environment.yml

# Activar el entorno
conda activate job-scraper-env
```

### Opción 2: Usar pip

```bash
# Clonar el repositorio
git clone https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración Inicial

```bash
# Copiar archivo de ejemplo de variables de entorno
cp .env.example .env

# Editar .env si necesitas configurar credenciales (opcional)
# nano .env
```

### Verificar Instalación

Después de clonar el repositorio, puedes verificar que todo esté correcto:

```bash
# Verificar que todos los archivos necesarios estén presentes
python scripts/verify_installation.py
```

Este script verificará:
- Versión de Python
- Archivos requeridos
- Estructura de directorios
- Dependencias instaladas

## 📖 Uso

### Uso Básico

```bash
# Ejecutar scraping completo con configuración por defecto
python -m src.main

# Esto realizará:
# 1. Scraping de todas las plataformas habilitadas
# 2. Guardado de datos en CSV, JSON y SQLite
# 3. Análisis de los datos
# 4. Generación de visualizaciones
# 5. Creación de informe HTML
```

### Uso Avanzado

```bash
# Scrapear plataformas específicas
python -m src.main --platforms indeed infojobs

# Buscar términos específicos
python -m src.main --keywords "machine learning" "data engineer"

# Buscar en ubicación específica
python -m src.main --location "Madrid"

# Cargar datos existentes desde archivo
python -m src.main --load-from data/raw/jobs_20240115_120000.csv

# Analizar datos existentes sin scrapear
python -m src.main --skip-scraping

# Solo analizar, sin generar visualizaciones
python -m src.main --skip-scraping --no-visualizations

# Solo analizar, sin generar informe
python -m src.main --skip-scraping --no-report
```

### Combinando Opciones

```bash
# Buscar "data scientist" en Barcelona usando Indeed y LinkedIn
python -m src.main \
  --platforms indeed linkedin \
  --keywords "data scientist" \
  --location "Barcelona"

# Analizar datos guardados y generar solo el informe
python -m src.main \
  --load-from data/raw/jobs_20240115_120000.csv \
  --no-visualizations
```

## ⚙️ Configuración

### Archivo config.yaml

El archivo `config/config.yaml` contiene toda la configuración del sistema:

```yaml
# Habilitar/deshabilitar plataformas
platforms:
  indeed:
    enabled: true
  infojobs:
    enabled: true
  linkedin:
    enabled: false  # Requiere credenciales

# Términos de búsqueda
search_terms:
  keywords:
    - "data scientist"
    - "machine learning"
    - "data engineer"
  locations:
    - "España"
    - "Madrid"
    - "Barcelona"

# Límites de scraping
scraping:
  max_jobs_per_platform: 100
  delay_between_requests: 2
```

### Variables de Entorno (.env)

Para plataformas que requieren autenticación:

```env
# LinkedIn (opcional)
LINKEDIN_EMAIL=tu_email@example.com
LINKEDIN_PASSWORD=tu_password

# Configuración de scraping
MAX_JOBS_PER_PLATFORM=100
HEADLESS_MODE=true
LOG_LEVEL=INFO
```

## 📊 Plataformas Soportadas

El sistema soporta las siguientes plataformas (en diferentes niveles de implementación):

### Implementadas
- ✅ Indeed
- ✅ InfoJobs (con limitaciones anti-scraping)

### Template Disponible
- 📝 Glassdoor
- 📝 Monster
- 📝 Infoempleo
- 📝 Workana
- 📝 Freelancer
- 📝 Malt
- 📝 Fiverr
- 📝 SimplyHired
- 📝 ZipRecruiter
- 📝 CareerBuilder
- 📝 Randstad
- 📝 iTalenters
- 📝 MichaelPage
- 📝 Tecnoempleo
- 📝 Hays

### Requieren API/Credenciales
- 🔐 LinkedIn
- 🔐 Upwork

## 📂 Estructura del Proyecto

```
compare_jobs/
├── config/
│   └── config.yaml           # Configuración principal
├── data/                     # Datos generados
│   ├── raw/                  # Datos sin procesar (CSV, JSON)
│   ├── processed/            # Datos procesados
│   ├── reports/              # Informes HTML/MD
│   ├── visualizations/       # Gráficos generados
│   └── jobs.db              # Base de datos SQLite
├── src/
│   ├── main.py              # Punto de entrada
│   ├── models/
│   │   └── job_offer.py     # Modelo de datos
│   ├── scrapers/
│   │   ├── base_scraper.py  # Clase base
│   │   ├── indeed_scraper.py
│   │   ├── infojobs_scraper.py
│   │   ├── generic_scraper.py  # Template para nuevos scrapers
│   │   └── scraper_factory.py
│   ├── services/
│   │   ├── data_storage.py       # Almacenamiento
│   │   ├── data_analyzer.py      # Análisis
│   │   ├── data_visualizer.py    # Visualizaciones
│   │   └── report_generator.py   # Informes
│   └── utils/
│       ├── config_loader.py      # Configuración
│       └── scraping_utils.py     # Utilidades
├── environment.yml           # Entorno Conda
├── requirements.txt         # Dependencias pip
└── README.md
```

## 🎨 Resultados

### Datos Recopilados

Cada oferta incluye:
- Título del puesto
- Empresa
- Ubicación
- Tipo de contrato
- Modalidad (remoto/presencial/híbrido)
- Rango salarial (si disponible)
- Tecnologías detectadas
- Habilidades requeridas
- Descripción completa

### Análisis Generados

- Top tecnologías más demandadas
- Empresas que más publican ofertas
- Distribución salarial
- Distribución geográfica
- Tipos de contrato
- Niveles de experiencia
- Correlaciones entre tecnologías
- Patrones y tendencias del mercado

### Visualizaciones

- Gráficos de barras de tecnologías
- Gráficos de empresas
- Distribución de ubicaciones
- Nubes de palabras
- Gráficos de correlaciones

### Informe HTML

Informe completo con:
- Resumen ejecutivo
- Estadísticas generales
- Gráficos interactivos
- Tablas de datos
- Insights principales

## 🔧 Desarrollo

### Añadir Nuevo Scraper

1. Copia `src/scrapers/generic_scraper.py`
2. Renombra la clase y actualiza el nombre de plataforma
3. Implementa los métodos de parsing específicos
4. Registra en `scraper_factory.py`:

```python
from .tu_scraper import TuScraper
ScraperFactory._SCRAPERS['tuplataforma'] = TuScraper
```

### Estructura de un Scraper

```python
class MiScraper(BaseScraper):
    def _get_platform_name(self) -> str:
        return "MiPlataforma"

    def scrape_jobs(self, keywords, location) -> List[JobOffer]:
        # Implementar lógica de scraping
        pass
```

## ⚠️ Consideraciones Legales y Éticas

- **Respeta los Términos de Servicio**: Muchos sitios web prohíben scraping en sus TOS
- **Usa APIs cuando estén disponibles**: Preferible a scraping
- **Rate Limiting**: El sistema incluye delays para no sobrecargar servidores
- **Datos Personales**: No recopiles ni almacenes datos personales sensibles
- **Uso Educativo/Personal**: Este proyecto es para uso educativo y personal

## 🐛 Solución de Problemas

### Error: "No hay scrapers disponibles"

```bash
# Verifica que las plataformas estén habilitadas en config.yaml
# O especifica plataformas manualmente:
python -m src.main --platforms indeed
```

### Error: "403 Forbidden"

```bash
# Algunos sitios bloquean scraping. Opciones:
# 1. Usar su API oficial (si está disponible)
# 2. Usar Selenium/Playwright (más lento pero más robusto)
# 3. Configurar proxies (avanzado)
```

### No se generan visualizaciones

```bash
# Instala dependencias de visualización:
pip install matplotlib seaborn plotly wordcloud

# O reinstala el entorno:
conda env create -f environment.yml --force
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 👥 Autor

- Alberto Jim Rod - [@albertjimrod](https://github.com/albertjimrod)

## 🙏 Agradecimientos

- Beautiful Soup - Web scraping
- Pandas - Análisis de datos
- Matplotlib/Seaborn - Visualizaciones
- Jinja2 - Generación de informes

## 📮 Contacto y Soporte

Para reportar bugs o sugerir mejoras, abre un issue en GitHub.

---

**Nota**: Este proyecto está en desarrollo activo. Las implementaciones de scrapers para algunas plataformas son templates que requieren personalización según la estructura actual de cada sitio web.
