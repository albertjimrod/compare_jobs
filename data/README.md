# Directorio de Datos

Este directorio contiene los datos generados por el Job Scraper.

## Estructura

```
data/
├── raw/              # Datos sin procesar (CSV, JSON)
├── processed/        # Datos procesados
├── reports/          # Informes HTML/Markdown generados
├── visualizations/   # Gráficos y visualizaciones
└── jobs.db          # Base de datos SQLite (se genera automáticamente)
```

## Archivos Generados

Cuando ejecutes el scraper, se generarán automáticamente:

- `raw/jobs_TIMESTAMP.csv` - Ofertas en formato CSV
- `raw/jobs_TIMESTAMP.json` - Ofertas en formato JSON
- `jobs.db` - Base de datos SQLite con todas las ofertas
- `reports/informe_TIMESTAMP.html` - Informe completo en HTML
- `visualizations/*.png` - Gráficos de análisis

## Nota

Los archivos de datos (*.csv, *.json, *.db) están excluidos del repositorio por `.gitignore` para evitar subir datos sensibles. Solo se preserva la estructura de directorios con archivos `.gitkeep`.
