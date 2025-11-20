# Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el Job Scraper en menos de 5 minutos.

## ⚠️ ANTES DE EMPEZAR

**El código está en la rama:** `claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6`

**Ver:** [INSTALACION.md](INSTALACION.md) para detalles completos

## 1️⃣ Clonar el Repositorio (Rama Correcta)

```bash
# Opción 1: Clonar directamente la rama con el código
git clone -b claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6 \
  https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs

# Opción 2: Si ya clonaste, cambia de rama
cd compare_jobs
git checkout claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6
```

## 2️⃣ Verificar la Instalación

Antes de instalar dependencias, verifica que todos los archivos estén presentes:

```bash
python scripts/verify_installation.py
```

Deberías ver:
```
✅ Python 3.11.x
✅ Todos los archivos presentes (13/13)
✅ Todos los directorios presentes (14/14)
```

## 3️⃣ Instalar Dependencias

### Opción A: Con Conda (Recomendado)

```bash
# Crear entorno
conda env create -f environment.yml

# Activar entorno
conda activate job-scraper-env

# Verificar instalación
python scripts/verify_installation.py
```

### Opción B: Con pip

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python scripts/verify_installation.py
```

## 4️⃣ Configuración (Opcional)

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar si necesitas configurar credenciales
nano .env  # o tu editor favorito
```

**Nota:** La configuración por defecto en `config/config.yaml` ya funciona. Solo necesitas editar `.env` si quieres usar APIs que requieren autenticación (LinkedIn, Upwork).

## 5️⃣ Ejecutar tu Primer Scraping

### Opción 1: Ejemplo Rápido

```bash
python scripts/quick_start.py
```

Esto ejecutará un scraping limitado de Indeed (rápido para probar).

### Opción 2: Scraping Completo

```bash
python -m src.main
```

Esto ejecutará scraping de todas las plataformas habilitadas en `config/config.yaml`.

### Opción 3: Scraping Personalizado

```bash
# Solo Indeed, búsqueda específica
python -m src.main --platforms indeed --keywords "machine learning"

# Solo InfoJobs, ubicación específica
python -m src.main --platforms infojobs --location "Madrid"

# Múltiples plataformas
python -m src.main --platforms indeed infojobs --keywords "data scientist"
```

## 6️⃣ Ver Resultados

Después de ejecutar el scraping, encontrarás:

```
data/
├── raw/
│   ├── jobs_TIMESTAMP.csv     ← Datos en CSV
│   └── jobs_TIMESTAMP.json    ← Datos en JSON
├── jobs.db                     ← Base de datos SQLite
├── reports/
│   └── informe_TIMESTAMP.html ← 📊 Abre este en tu navegador
└── visualizations/
    ├── top_technologies.png
    ├── top_companies.png
    └── ... (más gráficos)
```

**Abre el informe HTML en tu navegador** para ver el análisis completo con gráficos interactivos.

## 7️⃣ Siguiente Nivel

### Personalizar Configuración

Edita `config/config.yaml` para:
- Habilitar/deshabilitar plataformas
- Cambiar términos de búsqueda
- Ajustar límites de scraping
- Configurar análisis

### Analizar Datos Existentes

```bash
# Analizar datos guardados sin hacer scraping nuevo
python -m src.main --skip-scraping

# Cargar desde archivo específico
python -m src.main --load-from data/raw/jobs_20240115_120000.csv
```

### Añadir Nuevos Scrapers

Consulta `docs/extending_scrapers.md` para una guía completa de cómo añadir scrapers para nuevas plataformas.

## ❓ Troubleshooting

### Error: "No module named 'pandas'"

```bash
# Reinstala las dependencias
pip install -r requirements.txt
# o
conda env create -f environment.yml --force
```

### Error: "403 Forbidden"

Algunos sitios bloquean scraping. Usa la API oficial si está disponible o prueba con otra plataforma.

### Error: "No hay scrapers disponibles"

Verifica que las plataformas estén habilitadas en `config/config.yaml`:

```yaml
platforms:
  indeed:
    enabled: true  # ← debe ser true
```

### No se generan gráficos

Instala las dependencias de visualización:

```bash
pip install matplotlib seaborn plotly wordcloud
```

## 🎯 Comandos Útiles

```bash
# Ver ayuda completa
python -m src.main --help

# Solo scraping, sin análisis
python -m src.main --no-report --no-visualizations

# Solo análisis de datos existentes
python -m src.main --skip-scraping

# Verificar instalación
python scripts/verify_installation.py
```

## 📚 Más Información

- **README.md**: Documentación completa
- **docs/extending_scrapers.md**: Guía para añadir scrapers
- **config/config.yaml**: Configuración completa con comentarios

## 🆘 Soporte

Si encuentras problemas:
1. Ejecuta `python scripts/verify_installation.py`
2. Revisa la sección Troubleshooting arriba
3. Consulta el README.md completo
4. Abre un issue en GitHub

---

**¡Listo!** Ya puedes empezar a recopilar y analizar ofertas de trabajo 🚀
