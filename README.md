# 🔍 Compare Jobs - Sistema Multi-Fuente de Scraping de Ofertas Laborales

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/albertjimrod/compare_jobs)

Sistema avanzado de web scraping para recopilar, analizar y comparar ofertas de trabajo de múltiples plataformas laborales. Automatiza la búsqueda de empleo extrayendo datos de 19 portales diferentes y proporcionando análisis inteligente de tecnologías, salarios y tendencias del mercado.

---

## 📋 Descripción

**Compare Jobs** es una herramienta profesional de scraping que:

- 🌐 **Extrae ofertas** de 19 plataformas laborales diferentes
- 🤖 **Automatiza** la búsqueda con técnicas anti-ban avanzadas
- 🔍 **Analiza** automáticamente tecnologías y skills requeridas
- 📊 **Visualiza** tendencias del mercado laboral
- 💾 **Almacena** resultados en múltiples formatos (CSV, JSON, SQLite)
- 📈 **Genera reportes** personalizados con estadísticas detalladas

---

## ✨ Características Principales

### 🚀 Scraping Multi-Fuente
- **19 scrapers implementados** para diferentes plataformas
- **Arquitectura modular** con patrón Factory
- **Sistema anti-ban** robusto (delays aleatorios, retry automático, rate limiting)
- **Soporte Selenium + undetected-chromedriver** para evasión de detección

### 🧠 Análisis Inteligente
- **Extracción automática** de tecnologías mencionadas (Python, Java, React, etc.)
- **Detección de skills** (Machine Learning, DevOps, Agile, etc.)
- **Análisis de salarios** por tecnología y ubicación
- **Deduplicación** inteligente de ofertas repetidas

### 📊 Visualización y Reportes
- **Gráficas interactivas** con Plotly y Matplotlib
- **Word clouds** de tecnologías más demandadas
- **Reportes en PDF/HTML** personalizables
- **Dashboard** de estadísticas en tiempo real

---

## 🌐 Plataformas Soportadas

### ✅ Totalmente Funcionales (4)
| Plataforma | Tipo | Ofertas Esperadas | Dificultad |
|------------|------|-------------------|------------|
| **Indeed** | Agregador | 500+ | 🟢 Media |
| **InfoJobs** | Portal español | 300+ | 🟢 Baja |
| **LinkedIn** | Red profesional | 400+ | 🟡 Media |
| **Monster** | Agregador | 200+ | 🔴 Alta |

### 🔧 Implementados (Requieren ajuste de selectores) (15)

#### Portales Corporativos (Más fáciles)
- **MichaelPage** - Consultoría RR.HH. (🟢 Fácil - empezar por este)
- **Randstad** - Empresa RR.HH. internacional (🟢 Fácil)
- **Hays** - Especialización por sectores (🟢 Fácil)

#### Portales Españoles Especializados
- **Tecnoempleo** - Especializado en tecnología (🟡 Media - Alta prioridad)
- **InfoEmpleo** - Portal generalista español (🟡 Media)
- **iTalenters** - Especializado IT (🟡 Media)

#### Agregadores Internacionales
- **Glassdoor** - Con reviews de empresas (🔴 Difícil - protección fuerte)
- **SimplyHired** - Agregador (🟡 Media)
- **ZipRecruiter** - Agregador internacional (🟡 Media)
- **CareerBuilder** - Agregador (🟡 Media)

#### Plataformas Freelance
- **Upwork** - Freelance global (🟡 Media)
- **Freelancer** - Proyectos freelance (🟡 Media)
- **Workana** - Freelance latinoamérica (🟡 Media)
- **Malt** - Freelance Europa (🟡 Media)
- **Fiverr** - Servicios freelance (🟡 Media)

**Objetivo**: 800-1000+ ofertas únicas combinando múltiples fuentes

---

## 🏗️ Arquitectura del Sistema

### Estructura del Proyecto

```
compare_jobs/
│
├── 📄 README.md                          # Este archivo
├── 📄 LICENSE                            # Licencia MIT
├── 📄 requirements.txt                   # Dependencias Python
├── 📄 environment.yml                    # Entorno Conda (opcional)
├── 📄 .env.example                       # Variables de entorno de ejemplo
│
├── 📚 Documentación/
│   ├── RESUMEN_EJECUTIVO.md              # Plan de acción y próximos pasos
│   ├── PLAN_INTEGRACION_SCRAPERS.md      # Análisis técnico de fuentes
│   ├── ANALISIS_NUEVAS_FUENTES.md        # Evaluación de protecciones anti-scraping
│   ├── IMPLEMENTATION_SUMMARY.md         # Resumen de implementación
│   ├── PLAN_DESARROLLO.md                # Plan de desarrollo modular
│   ├── ANTI_SCRAPING_SOLUTIONS.md        # Técnicas anti-ban
│   ├── SCRAPERS_GUIDE.md                 # Guía de uso de scrapers
│   ├── SELENIUM_GUIDE.md                 # Guía específica de Selenium
│   ├── INSTALACION.md                    # Instrucciones de instalación
│   └── QUICKSTART.md                     # Inicio rápido
│
├── 🧪 Scripts de Testing/
│   ├── test_multi_scrapers_poc.py        # Prueba de concepto (10 ofertas/scraper)
│   └── test_scraper_individual.py        # Testing individual configurable
│
├── 📁 src/                               # Código fuente principal
│   ├── __init__.py
│   ├── main.py                           # Punto de entrada
│   │
│   ├── 🤖 scrapers/                      # 19 Scrapers implementados
│   │   ├── base_scraper.py               # Clase base abstracta
│   │   ├── scraper_factory.py            # Factory pattern
│   │   ├── _scraper_template.py          # Template para nuevos scrapers
│   │   │
│   │   ├── indeed_scraper_selenium.py    # ✅ Totalmente funcional
│   │   ├── infojobs_scraper.py           # ✅ Funcional
│   │   ├── linkedin_scraper.py           # ✅ Funcional
│   │   ├── monster_scraper.py            # ✅ Funcional
│   │   │
│   │   ├── glassdoor_scraper.py          # 🔧 Ajustar selectores
│   │   ├── michaelpage_scraper.py        # 🔧 Ajustar selectores
│   │   ├── randstad_scraper.py           # 🔧 Ajustar selectores
│   │   ├── hays_scraper.py               # 🔧 Ajustar selectores
│   │   ├── tecnoempleo_scraper.py        # 🔧 Ajustar selectores
│   │   ├── infoempleo_scraper.py         # 🔧 Ajustar selectores
│   │   ├── simplyhired_scraper.py        # 🔧 Ajustar selectores
│   │   ├── ziprecruiter_scraper.py       # 🔧 Ajustar selectores
│   │   ├── careerbuilder_scraper.py      # 🔧 Ajustar selectores
│   │   ├── italenters_scraper.py         # 🔧 Ajustar selectores
│   │   ├── upwork_scraper.py             # 🔧 Ajustar selectores
│   │   ├── freelancer_scraper.py         # 🔧 Ajustar selectores
│   │   ├── workana_scraper.py            # 🔧 Ajustar selectores
│   │   ├── malt_scraper.py               # 🔧 Ajustar selectores
│   │   └── fiverr_scraper.py             # 🔧 Ajustar selectores
│   │
│   ├── 📊 models/                        # Modelos de datos
│   │   ├── __init__.py
│   │   └── job_offer.py                  # JobOffer dataclass unificado
│   │
│   ├── ⚙️  services/                     # Servicios de negocio
│   │   ├── __init__.py
│   │   ├── data_analyzer.py              # Análisis de datos
│   │   ├── data_storage.py               # Persistencia (CSV/JSON/SQLite)
│   │   ├── data_visualizer.py            # Gráficas y visualizaciones
│   │   └── report_generator.py           # Generación de reportes
│   │
│   └── 🛠️  utils/                        # Utilidades
│       ├── __init__.py
│       ├── config_loader.py              # Carga de configuración YAML
│       └── scraping_utils.py             # Utilidades de scraping
│
├── 🧪 tests/                             # Tests unitarios
│   ├── __init__.py
│   ├── test_models/
│   ├── test_scrapers/
│   └── test_services/
│
├── 📊 data/                              # Almacenamiento de datos
│   ├── raw/                              # Datos sin procesar
│   ├── processed/                        # Datos limpios y deduplicados
│   ├── reports/                          # Reportes generados
│   └── visualizations/                   # Gráficas guardadas
│
├── 📜 scripts/                           # Scripts de automatización
│   ├── search_all_platforms.py           # Ejecutar todos los scrapers
│   ├── quick_start.py                    # Demo rápido
│   ├── generate_scrapers.py              # Generador de scrapers
│   ├── verify_installation.py            # Verificar setup
│   ├── check_chrome.py                   # Verificar Chrome/Chromedriver
│   └── setup.sh                          # Setup inicial
│
├── ⚙️  config/                           # Configuración
│   ├── config.yaml                       # Config general
│   └── scrapers_config.yaml              # Config por scraper
│
└── 📂 docs/                              # Documentación adicional
    ├── architecture.md                   # Arquitectura detallada
    └── extending_scrapers.md             # Crear nuevos scrapers
```

### Patrón de Diseño: Factory + Template Method

```python
# Factory crea scrapers dinámicamente
from src.scrapers.scraper_factory import ScraperFactory

scraper = ScraperFactory.create_scraper('indeed', config)
jobs = scraper.scrape_jobs(keywords=['python', 'data science'], location='Madrid')

# Template Method define flujo común
class BaseScraper(ABC):
    def scrape_jobs(self, keywords, location):
        self._setup_driver()          # Implementado en subclase
        for keyword in keywords:
            jobs = self._search_keyword()  # Implementado en subclase
        self._cleanup()
        return jobs
```

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- Google Chrome o Chromium
- pip o conda

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs

# 2. Cambiar a la rama estable (tiene todos los scrapers)
git checkout claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6

# 3. Instalar dependencias
pip install -r requirements.txt

# O con conda (recomendado para entornos aislados)
conda env create -f environment.yml
conda activate compare_jobs

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
nano .env

# 5. Verificar instalación
python scripts/verify_installation.py

# 6. Verificar Chrome/Chromedriver
python scripts/check_chrome.py
```

### Dependencias Principales

```yaml
Web Scraping:
  - selenium 4.15.0+              # Automatización de navegador
  - undetected-chromedriver 3.5.4+ # Anti-detección
  - beautifulsoup4 4.12.0+        # Parsing HTML
  - playwright 1.40.0+            # Alternativa a Selenium
  - cloudscraper 1.2.71+          # Bypass Cloudflare

Análisis de Datos:
  - pandas 2.1.0+                 # Manipulación de datos
  - numpy 1.24.0+                 # Computación numérica
  - scikit-learn 1.3.0+           # Machine learning

NLP:
  - nltk 3.8.0+                   # Procesamiento de lenguaje
  - spacy 3.7.0+                  # NLP avanzado

Visualización:
  - matplotlib 3.8.0+             # Gráficas
  - seaborn 0.13.0+               # Gráficas estadísticas
  - plotly 5.18.0+                # Gráficas interactivas
  - wordcloud 1.9.3+              # Nubes de palabras

Utilidades:
  - loguru 0.7.0+                 # Logging elegante
  - tqdm 4.66.0+                  # Barras de progreso
  - pyyaml 6.0+                   # Parsing YAML
```

---

## 📖 Uso

### Quick Start - Demo Rápido (5 minutos)

```bash
# Demo rápido con Indeed (scraper más confiable)
python scripts/quick_start.py
```

### Uso Básico - Scraping de Una Plataforma

```python
from src.scrapers.scraper_factory import ScraperFactory
from src.utils.config_loader import ConfigLoader

# Crear scraper
config = ConfigLoader()
scraper = ScraperFactory.create_scraper('indeed', config)

# Scraping
jobs = scraper.scrape_jobs(
    keywords=['python', 'data science', 'machine learning'],
    location='Madrid, España'
)

# Ver resultados
print(f"Encontradas {len(jobs)} ofertas")
for job in jobs[:5]:
    print(f"- {job.title} @ {job.company}")
    print(f"  Tecnologías: {', '.join(job.technologies[:5])}")
```

### Uso Avanzado - Scraping Multi-Plataforma

```bash
# Ejecutar todos los scrapers disponibles
python scripts/search_all_platforms.py \
  --keywords "python,data science,machine learning" \
  --location "Madrid, España" \
  --platforms indeed,infojobs,linkedin,monster \
  --max-jobs 100

# Guardar resultados en CSV
python scripts/search_all_platforms.py \
  --keywords "python" \
  --output results.csv \
  --format csv
```

### Testing Individual de Scrapers

```bash
# Probar un scraper específico en modo visual
python test_scraper_individual.py michaelpage \
  --headless=false \
  --max-jobs=5 \
  --keywords="python,django" \
  --location="Barcelona"

# Ver todas las opciones
python test_scraper_individual.py --help

# Ejemplos con diferentes scrapers:
python test_scraper_individual.py randstad --headless=false --max-jobs=10
python test_scraper_individual.py tecnoempleo --keywords="react,nodejs"
python test_scraper_individual.py indeed --save=results_indeed.csv
```

### Prueba de Concepto - 10 Scrapers

```bash
# Probar los 10 scrapers principales (10 ofertas cada uno)
python test_multi_scrapers_poc.py

# Genera reporte automático con:
# - Scrapers exitosos vs fallidos
# - Número de ofertas por scraper
# - Tiempo de ejecución
# - Muestra de ofertas encontradas
```

### Análisis de Datos

```python
from src.services.data_analyzer import DataAnalyzer
from src.services.data_visualizer import DataVisualizer

# Cargar datos
analyzer = DataAnalyzer('data/processed/jobs.csv')

# Análisis
top_tech = analyzer.get_top_technologies(n=10)
salaries = analyzer.analyze_salaries_by_tech()
locations = analyzer.analyze_by_location()

# Visualización
visualizer = DataVisualizer()
visualizer.plot_technology_trends(top_tech)
visualizer.generate_wordcloud(all_descriptions)
visualizer.plot_salary_distribution()
```

### Generación de Reportes

```bash
# Generar reporte completo en HTML
python scripts/generate_report.py \
  --input data/processed/jobs.csv \
  --output reports/market_analysis.html \
  --format html

# Generar reporte en PDF
python scripts/generate_report.py \
  --input data/processed/jobs.csv \
  --output reports/market_analysis.pdf \
  --format pdf
```

---

## ⚙️ Configuración

### Archivo config/config.yaml

```yaml
# Configuración de scraping
scraping:
  headless_mode: true                # false para ver navegador
  delay_between_requests: 5          # Segundos entre requests
  max_retries: 3                     # Reintentos en caso de fallo
  page_load_timeout: 30              # Timeout de carga de página
  max_jobs_per_platform: 100         # Máximo de ofertas por plataforma
  max_pages_per_session: 5           # Máximo de páginas por sesión

# Términos de búsqueda por defecto
search_terms:
  keywords:
    - python
    - data science
    - machine learning
    - data engineer
  locations:
    - "Madrid, España"
    - "Barcelona, España"
    - "Remote"

# Tecnologías a detectar
analysis:
  technologies:
    languages:
      - Python
      - Java
      - JavaScript
      - TypeScript
      - Go
      - Rust
    frameworks:
      - Django
      - Flask
      - FastAPI
      - React
      - Vue
      - Angular
    tools:
      - Docker
      - Kubernetes
      - AWS
      - Azure
      - GCP
    databases:
      - PostgreSQL
      - MongoDB
      - MySQL
      - Redis

  skills:
    - Machine Learning
    - Deep Learning
    - Data Analysis
    - DevOps
    - CI/CD
    - Agile
    - Scrum

# Almacenamiento
storage:
  output_format: csv                 # csv, json, sqlite
  output_directory: data/processed
  keep_raw_data: true
```

---

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
# Todos los tests
pytest tests/

# Tests específicos
pytest tests/test_scrapers/
pytest tests/test_services/

# Con cobertura
pytest --cov=src tests/
```

### Testing de Scrapers

```bash
# Test individual con verificación
python test_scraper_individual.py <platform> \
  --headless=false \
  --verbose \
  --max-jobs=5

# Test de múltiples scrapers
python test_multi_scrapers_poc.py
```

---

## 📊 Características Técnicas Avanzadas

### Sistema Anti-Ban

```python
✅ Delays Aleatorios con Jitter
   - Delay base + variación aleatoria (20-50%)
   - Implementado en: base_scraper.py:_sleep()

✅ Backoff Exponencial en Reintentos
   - 2s, 4s, 8s, 16s entre reintentos
   - Implementado en: base_scraper.py:_retry_on_failure()

✅ User-Agent Rotation
   - Librería fake-useragent
   - Implementado en: scraping_utils.py

✅ Anti-Detección Selenium
   - Desactivar webdriver flag
   - Experimental options para Chrome
   - Implementado en cada scraper

✅ Rate Limiting Configurable
   - Por plataforma y global
   - Implementado en: config.yaml + base_scraper.py

✅ Deduplicación Automática
   - Por URL o título+empresa
   - Implementado en: base_scraper.py:remove_duplicates()
```

### Extracción Inteligente de Datos

- **Múltiples selectores con fallback**: Si un selector falla, prueba alternativas
- **Regex avanzados**: Extracción de salarios, fechas, tecnologías
- **NLP**: Análisis de descripciones para detectar skills implícitas
- **Lazy loading**: Manejo de contenido dinámico con JavaScript

---

## 📚 Documentación Adicional

| Documento | Descripción |
|-----------|-------------|
| [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) | Plan de acción inmediato y próximos pasos |
| [PLAN_INTEGRACION_SCRAPERS.md](PLAN_INTEGRACION_SCRAPERS.md) | Análisis técnico completo de las 10 fuentes |
| [ANALISIS_NUEVAS_FUENTES.md](ANALISIS_NUEVAS_FUENTES.md) | Evaluación de barreras anti-scraping |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumen de implementación y estado |
| [SCRAPERS_GUIDE.md](SCRAPERS_GUIDE.md) | Guía de uso de scrapers |
| [SELENIUM_GUIDE.md](SELENIUM_GUIDE.md) | Guía específica de Selenium |
| [ANTI_SCRAPING_SOLUTIONS.md](ANTI_SCRAPING_SOLUTIONS.md) | Técnicas para evadir detección |
| [docs/extending_scrapers.md](docs/extending_scrapers.md) | Cómo crear nuevos scrapers |

---

## 🎯 Roadmap

### Fase 1: Estabilización (Semana 1-2) ✅
- [x] Arquitectura modular con 19 scrapers
- [x] Sistema anti-ban robusto
- [x] Análisis automático de tecnologías
- [x] Deduplicación de ofertas
- [x] Documentación completa

### Fase 2: Testing y Ajustes (Semana 3-4) 🔄
- [x] Scripts de testing individual
- [x] Prueba de concepto multi-scraper
- [ ] Completar selectores CSS por plataforma
- [ ] Validación de 5+ scrapers funcionales

### Fase 3: Expansión (Mes 2) 🔜
- [ ] 10+ scrapers completamente funcionales
- [ ] Dataset de 500-1000 ofertas únicas
- [ ] Dashboard de visualización
- [ ] Sistema de alertas

### Fase 4: Automatización (Mes 3) 🔜
- [ ] Scraping programado (cron jobs)
- [ ] Notificaciones de nuevas ofertas
- [ ] API REST para consultas
- [ ] Base de datos centralizada

### Fase 5: Inteligencia (Futuro) 💡
- [ ] ML para predicción de salarios
- [ ] Recomendación personalizada de ofertas
- [ ] Análisis de tendencias del mercado
- [ ] Comparación automática con tu perfil

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

### Reportar Bugs

```bash
# Crea un issue en GitHub con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Logs relevantes
```

### Añadir Nuevo Scraper

1. Usa el template: `src/scrapers/_scraper_template.py`
2. Implementa los métodos abstractos
3. Añade selectores CSS específicos
4. Prueba con `test_scraper_individual.py`
5. Crea PR con documentación

### Mejorar Scraper Existente

1. Identifica el scraper: `src/scrapers/<platform>_scraper.py`
2. Ejecuta en modo visual para debuggear
3. Actualiza selectores CSS
4. Prueba exhaustivamente
5. Documenta cambios en PR

---

## ⚠️ Consideraciones Legales y Éticas

### Uso Responsable

Este proyecto es para **uso educacional y personal**. Al usar este software:

- ✅ Respeta los Terms of Service de cada plataforma
- ✅ Usa delays razonables (5-10 segundos mínimo)
- ✅ No hagas scraping masivo (max 100-200 ofertas/sesión)
- ✅ Respeta robots.txt cuando sea posible
- ❌ NO uses para reventa de datos
- ❌ NO hagas scraping comercial sin permiso
- ❌ NO sobrecarges los servidores

### APIs Oficiales Recomendadas

Cuando estén disponibles, **usa APIs oficiales** en lugar de scraping:

- **Indeed**: https://www.indeed.com/publisher
- **LinkedIn**: https://developer.linkedin.com/
- **Glassdoor**: https://www.glassdoor.com/developer/
- **InfoJobs**: https://developer.infojobs.net/

---

## 🐛 Troubleshooting

### Problema: Scraper no encuentra ofertas

```bash
# 1. Ejecutar en modo visual para ver qué sucede
python test_scraper_individual.py <platform> --headless=false

# 2. Revisar logs
tail -f logs/test_<platform>_*.log

# 3. Verificar selectores CSS actualizados
# Los sitios cambian, los selectores pueden quedar obsoletos
```

### Problema: Error 403 Forbidden

```bash
# Incrementar delays en config.yaml
scraping:
  delay_between_requests: 10  # Aumentar de 5 a 10+

# Usar undetected-chromedriver
# Ya está configurado en los scrapers
```

### Problema: ChromeDriver no funciona

```bash
# Verificar instalación
python scripts/check_chrome.py

# Reinstalar chromedriver
pip install --upgrade webdriver-manager
```

### Problema: Ofertas duplicadas

```python
# La deduplicación está automática, pero puedes forzarla:
scraper.remove_duplicates()

# O al cargar datos:
analyzer = DataAnalyzer('data.csv', remove_duplicates=True)
```

---

## 📊 Estadísticas del Proyecto

- 📁 **19 scrapers** implementados
- 🎯 **10 plataformas** prioritarias
- 📄 **2000+ líneas** de código
- 📚 **8 documentos** de ayuda
- 🧪 **2 scripts** de testing
- ⏱️ **500-1000 ofertas** esperadas/scraping completo

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2024 Alberto Jim Rod

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👥 Autores

- **Alberto Jim Rod** - [@albertjimrod](https://github.com/albertjimrod)
  - 📧 Email: [tu-email@example.com]
  - 💼 LinkedIn: [tu-perfil-linkedin]

---

## 🙏 Agradecimientos

- **Selenium Team** - Por la herramienta de automatización
- **BeautifulSoup** - Por el excelente parser HTML
- **undetected-chromedriver** - Por la evasión de detección
- **Comunidad Open Source** - Por las librerías utilizadas

---

## 📞 Soporte

¿Necesitas ayuda?

1. 📖 **Documentación**: Lee los docs en la carpeta raíz
2. 🐛 **Issues**: Abre un issue en GitHub
3. 💬 **Discussions**: Participa en GitHub Discussions
4. 📧 **Email**: Contacto directo (para consultas privadas)

---

## 🔄 Estado del Proyecto

**Estado**: 🟢 Desarrollo Activo

**Última actualización**: 2025-11-20

**Versión actual**: v1.0-beta

**Próxima release**: v1.1 (Testing completo de 10 scrapers)

---

## ⭐ Si te gusta el proyecto

Si este proyecto te resulta útil:

- ⭐ Dale una estrella en GitHub
- 🔀 Haz fork para tus propias modificaciones
- 📢 Compártelo con otros developers
- 🤝 Contribuye con mejoras
- ☕ Invítame un café (opcional)

---

**Happy Scraping! 🚀🔍**

```
                    🔍 Compare Jobs
              ┌─────────────────────────┐
              │  19 Scrapers Working   │
              │  For Your Dream Job!   │
              └─────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    🏢 Indeed      📊 LinkedIn     💼 InfoJobs
    🔍 Glassdoor   🌐 Monster      🎯 Tecnoempleo
    💻 MichaelPage 🚀 Randstad     ⭐ And 11 more!
```

---

