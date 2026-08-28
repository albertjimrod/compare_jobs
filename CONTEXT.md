# CONTEXT — Compare Jobs

Documento de retoma de proyecto. Destila el estado real del repositorio a
2026-08-28. No sustituye a README ni a `docs/`.

## 1. Qué es

Herramienta para comparar ofertas de trabajo y apoyar la decisión en procesos
de selección. La idea es evaluar varias ofertas con criterios configurables
(salario, beneficios, ubicación, cultura, crecimiento…), ponderarlos según las
prioridades del usuario y producir un informe/ranking.

En las ramas de trabajo activo el foco se ha desplazado a un paso previo:
**scraping de portales de empleo** (Indeed, MichaelPage y otros) para obtener
las ofertas que luego se compararían.

## 2. Stack

- **Lenguaje:** Python (`__version__ = "0.1.0"`; sin versión mínima declarada —
  PENDIENTE DE CONFIRMAR).
- **Testing:** pytest (referenciado en README y `scripts/run_tests.sh`, que
  todavía no existe).
- **Config prevista:** YAML (`config/config.yaml`, `config/criteria.yaml`).
- **Scraping (ramas activas):** Selenium / `undetected-chromedriver` para sortear
  Cloudflare; paginación y, en iteraciones recientes, scroll infinito.
- **No hay** `pyproject.toml`, `requirements.txt` ni `package.json` en la rama
  actual. Las dependencias reales están PENDIENTE DE CONFIRMAR (probablemente
  declaradas en las ramas de scraper).
- **Despliegue:** ninguno. Uso local por CLI (`python src/main.py --compare …`).
- **Licencia:** MIT (Alberto Jim Rod).

## 3. Arquitectura

Diseño modular en tres capas dentro de `src/` (según `docs/architecture.md`):

- **`models/`** — estructuras de datos: `Job` (una oferta con sus atributos) y
  `Comparison` (comparación entre varias ofertas).
- **`services/`** — lógica de negocio: `JobService` (CRUD de ofertas) y
  `ComparisonService` (comparación y puntuación ponderada).
- **`utils/`** — validadores de datos, formateadores de salida, helpers.

Flujo previsto: `Input (JSON/YAML) → JobService → Models → ComparisonService →
Output (Report)`.

Estado real: sólo existen los paquetes vacíos (`src/`, `src/models/`,
`src/services/`, `src/utils/`, `tests/`) con sus `__init__.py`. `main.py`,
los modelos, servicios, utils y tests **no están implementados**. Los
directorios `data/`, `scripts/` y `config/` que describe el README tampoco
existen aún.

Las ramas de scraper añaden una capa de adquisición de datos (scrapers por
portal + scripts de diagnóstico + generador de informe HTML) que en la rama
actual no está presente.

## 4. Decisiones clave

- **Arquitectura por capas (models/services/utils)** para separar
  responsabilidades, favorecer testabilidad y poder añadir criterios sin tocar
  el resto.
- **Criterios de comparación configurables y ponderables** vía YAML, en lugar de
  fórmula fija: el usuario ajusta pesos a sus prioridades.
- **Entrada por ficheros JSON/YAML y CLI**, sin servicio web ni base de datos en
  esta fase (SQLite aparece sólo en `.gitignore` como precaución).
- **En las ramas de scraper:** se abandonó la paginación clásica en favor de
  **scroll infinito** y se adoptó **`undetected-chromedriver`** por bloqueos de
  Cloudflare en Indeed (commits "CRÍTICO: Cambia de paginación a scroll
  infinito…", "Implementa undetected-chromedriver con paginación funcional").
  Se decidió preservar una **rama estable del scraper** (`preserve-stable-
  scraper`) mientras otra rama explora la **integración multi-fuente**.
- Alternativas descartadas / no elegidas: no hay registro explícito de
  alternativas (no existen `DECISIONS.md`, `TODO.md` ni `JOURNAL/`).
  PENDIENTE DE CONFIRMAR el resto de motivaciones.

## 5. Estado actual

- **Rama activa (checkout):**
  `claude/document-repo-structure-01Ec8t4kjc44jSjZydH1yuTK` (también es el "main"
  configurado del repo local). Árbol de trabajo **limpio, sin cambios sin
  commitear**. Un único commit: "Documenta la estructura inicial del
  repositorio".
- **Qué funciona:** nada ejecutable. Sólo documentación (`README.md`,
  `docs/architecture.md`) y esqueleto de paquetes Python.
- **Qué falta:** toda la implementación (modelos, servicios, utils, `main.py`,
  CLI, tests), ficheros de dependencias, `config/`, `data/`, `scripts/`.
- **Otras ramas remotas con trabajo real (no fusionadas aquí):**
  - `origin/claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6` — scraper
    con `undetected-chromedriver`, tests de paginación/scroll, y un "análisis y
    plan de desarrollo para integración multi-fuente" (último commit `d69a61d`).
  - `origin/claude/preserve-stable-scraper-01WhBVc7aCYKbHTBUDHnrBwE` — versión
    estable del scraper: 6+ scrapers por portal con selectores CSS robustos,
    script de diagnóstico, generador de informe HTML, CHANGELOG (último commit
    `f96e39f`).
  - Contenido detallado de estas ramas PENDIENTE DE CONFIRMAR (no inspeccionado
    fichero a fichero en esta sesión).
- No hay CI, ni releases, ni issues rastreados en el repo.

## 6. Próximos pasos

Priorizados:

1. **Decidir la línea de trabajo principal:** consolidar el scraper (fusionar
   `preserve-stable-scraper` y/o `job-scraper-data-science`) frente a arrancar
   la lógica de comparación en la rama de estructura. Hoy están divergentes.
2. **Añadir gestión de dependencias** (`pyproject.toml` o `requirements.txt`)
   que refleje Selenium/`undetected-chromedriver`, pytest y demás.
3. **Implementar el núcleo de comparación:** modelos `Job`/`Comparison`,
   `JobService`, `ComparisonService` con puntuación ponderada, y `main.py` con
   la CLI descrita en el README.
4. **Crear `config/` y `data/`:** `config.yaml`, `criteria.yaml` con criterios y
   pesos por defecto; ejemplos y plantillas de ofertas.
5. **Tests:** suite pytest para modelos, servicios y utils; `scripts/run_tests.sh`.
6. **Cerrar el pipeline:** conectar salida del scraper (ofertas normalizadas) →
   entrada de `JobService` → informe (reutilizar el generador HTML de la rama
   estable).
7. **Documentar decisiones:** crear `DECISIONS.md` / `TODO.md` para no perder el
   contexto que hoy sólo vive en mensajes de commit.
