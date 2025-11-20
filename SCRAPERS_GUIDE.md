# 🕷️ Guía de Scrapers - 19 Plataformas

Esta guía documenta todos los scrapers implementados en el sistema de Job Scraper.

## 📊 Estado de Implementación

| # | Plataforma | Estado | Tipo | Notas |
|---|------------|--------|------|-------|
| 1 | Indeed | ✅ Completo | Empleo | Selenium con fallback a requests |
| 2 | InfoJobs | ✅ Completo | Empleo | Requests básico, API disponible |
| 3 | LinkedIn | ⚠️ Stub | Empleo | Requiere login, API recomendada |
| 4 | Glassdoor | ⚠️ Stub | Empleo | Protección fuerte, API disponible |
| 5 | Monster | ⚠️ Stub | Empleo | Implementación básica |
| 6 | Upwork | ⚠️ Stub | Freelance | Requiere login para detalles |
| 7 | Freelancer | ⚠️ Stub | Freelance | Requiere completar selectores |
| 8 | Workana | ⚠️ Stub | Freelance | Enfoque Latinoamérica/España |
| 9 | Malt | ⚠️ Stub | Freelance | Enfoque Europa, requiere login |
| 10 | Fiverr | ⚠️ Stub | Freelance | Modelo inverso (gigs) |
| 11 | SimplyHired | ⚠️ Stub | Agregador | Requiere completar selectores |
| 12 | ZipRecruiter | ⚠️ Stub | Empleo | Requiere completar selectores |
| 13 | CareerBuilder | ⚠️ Stub | Empleo | API disponible |
| 14 | Randstad | ⚠️ Stub | RR.HH. | Ofertas propias |
| 15 | iTalenters | ⚠️ Stub | Tech España | Requiere completar selectores |
| 16 | MichaelPage | ⚠️ Stub | RR.HH. | Headhunting, alta cualificación |
| 17 | Tecnoempleo | ⚠️ Stub | Tech España | Requiere completar selectores |
| 18 | Hays | ⚠️ Stub | RR.HH. | Internacional |
| 19 | Infoempleo | ⚠️ Stub | Empleo España | Requiere completar selectores |

**Leyenda:**
- ✅ **Completo**: Funcionalmente completo y probado
- ⚠️ **Stub**: Estructura base implementada, requiere completar selectores CSS

---

## 🚀 Uso Rápido

### Usar un scraper específico:

```python
from src.scrapers.scraper_factory import ScraperFactory
from src.utils.config_loader import ConfigLoader

config = ConfigLoader()

# Scraper específico
scraper = ScraperFactory.create_scraper('linkedin', config)
jobs = scraper.scrape_jobs(keywords=['data scientist'])
print(f"Encontradas {len(jobs)} ofertas")
```

### Usar múltiples scrapers:

```python
platforms = ['indeed', 'infojobs', 'tecnoempleo']
all_jobs = []

for platform_name in platforms:
    scraper = ScraperFactory.create_scraper(platform_name, config)
    if scraper:
        jobs = scraper.scrape_jobs(keywords=['python developer'])
        all_jobs.extend(jobs)

print(f"Total: {len(all_jobs)} ofertas de {len(platforms)} plataformas")
```

### Ver plataformas disponibles:

```python
platforms = ScraperFactory.get_available_platforms()
print(f"Disponibles: {', '.join(platforms)}")
```

---

## 📋 Plataformas por Categoría

### 🏢 Empleo Generalista

#### **Indeed**
- **URL**: https://es.indeed.com
- **Estado**: ✅ Completo
- **Características**:
  - Selenium con lazy loading de tecnologías
  - Fallback automático a requests si Chrome no está disponible
  - Múltiples selectores CSS con fallbacks
  - Protección anti-scraping fuerte
- **Uso**:
  ```python
  scraper = ScraperFactory.create_scraper('indeed', config)
  ```

#### **LinkedIn**
- **URL**: https://www.linkedin.com
- **Estado**: ⚠️ Stub (estructura base)
- **Notas**:
  - Requiere autenticación para ofertas completas
  - API oficial recomendada: https://developer.linkedin.com/
  - Protección anti-scraping MUY AGRESIVA
- **TODO**: Completar selectores o implementar login

#### **Glassdoor**
- **URL**: https://www.glassdoor.es
- **Estado**: ⚠️ Stub
- **Notas**:
  - Protección anti-scraping agresiva
  - API disponible: https://www.glassdoor.com/developer/
  - Requiere delays largos
- **TODO**: Completar selectores CSS

#### **Monster**
- **URL**: https://www.monster.es
- **Estado**: ⚠️ Stub
- **Características**:
  - Implementación básica con múltiples selectores
  - Protección moderada
- **TODO**: Validar selectores con pruebas reales

### 💼 Freelance

#### **Upwork**
- **URL**: https://www.upwork.com
- **Estado**: ⚠️ Stub
- **Notas**:
  - Requiere autenticación para detalles completos
  - API oficial: https://developers.upwork.com/
  - Usa infinite scroll
  - Muestra tecnologías como tags directamente
- **Características especiales**:
  ```python
  # Upwork proporciona skills directamente en las tarjetas
  job.technologies  # Ya extraídas, no lazy loading
  ```

#### **Freelancer, Workana, Malt, Fiverr**
- **Estado**: ⚠️ Stubs
- **Notas comunes**:
  - Todas requieren login para acceso completo
  - Modelo freelance/proyecto (no empleo tradicional)
  - Consideran ubicación siempre como "Remote"
- **TODO**: Completar selectores específicos de cada plataforma

### 🔍 Agregadores

#### **SimplyHired, ZipRecruiter, CareerBuilder**
- **Estado**: ⚠️ Stubs
- **Características**:
  - Agregan ofertas de múltiples fuentes
  - CareerBuilder tiene API disponible
- **TODO**: Completar selectores CSS

### 🏢 Empresas de RR.HH.

#### **Randstad, MichaelPage, Hays**
- **Estado**: ⚠️ Stubs
- **Características**:
  - Ofertas propias (no agregadores)
  - Enfoque en perfiles cualificados
  - MichaelPage: headhunting ejecutivo
- **TODO**: Completar selectores CSS

### 🇪🇸 Portales Españoles

#### **InfoJobs**
- **URL**: https://www.infojobs.net
- **Estado**: ✅ Completo
- **Notas**: API oficial disponible (recomendado)

#### **Tecnoempleo, iTalenters, Infoempleo**
- **Estado**: ⚠️ Stubs
- **Características**:
  - Enfoque en mercado español
  - Tecnoempleo e iTalenters: especializados en tecnología
  - Protección anti-scraping más suave (generalmente)
- **TODO**: Completar selectores CSS

---

## 🛠️ Completar un Scraper Stub

Los scrapers stub tienen la estructura completa pero requieren actualizar los selectores CSS.

### Pasos para completar:

1. **Abrir el archivo del scraper**:
   ```bash
   # Ejemplo: completar LinkedIn
   code src/scrapers/linkedin_scraper.py
   ```

2. **Buscar TODOs**:
   ```python
   # Busca comentarios como:
   # TODO: Ajustar selector del título
   # TODO: Completar selectores CSS
   ```

3. **Encontrar selectores CSS correctos**:

   **Método A - Herramientas de desarrollo del navegador:**
   ```bash
   # 1. Abre la página de búsqueda en Chrome
   # 2. Presiona F12 (DevTools)
   # 3. Click derecho en elemento → Inspeccionar
   # 4. Copia el selector CSS
   # 5. Prueba en consola: document.querySelector('.tu-selector')
   ```

   **Método B - Modo visual (debugging):**
   ```yaml
   # En config/config.yaml
   scraping:
     headless_mode: false  # Ver navegador en acción
   ```

4. **Actualizar selectores**:
   ```python
   # Antes (genérico):
   title_elem = card.find_element(By.CLASS_NAME, "job-title")

   # Después (específico para la plataforma):
   title_elem = card.find_element(By.CSS_SELECTOR, "h2[data-job-title]")
   ```

5. **Probar el scraper**:
   ```python
   from src.scrapers.scraper_factory import ScraperFactory
   from src.utils.config_loader import ConfigLoader

   config = ConfigLoader()
   scraper = ScraperFactory.create_scraper('linkedin', config)
   jobs = scraper.scrape_jobs(keywords=['python'])

   print(f"Encontradas: {len(jobs)}")
   for job in jobs[:3]:
       print(f"- {job.title} | {job.company}")
   ```

---

## 📝 Selectores CSS Comunes

### Patrones frecuentes por elemento:

**Títulos de trabajo:**
```python
"h2.job-title"
"h3.title"
"a[data-job-title]"
"[data-test='job-title']"
".jobTitle"
```

**Empresas:**
```python
".company-name"
"[data-company]"
"[data-test='employer-name']"
".companyName"
```

**Ubicaciones:**
```python
".job-location"
"[data-location]"
"[data-test='location']"
".location"
```

**Descripciones:**
```python
".job-description"
".job-snippet"
"[data-test='description']"
"div.description"
```

---

## ⚠️ Consideraciones Importantes

### Protección Anti-Scraping

**Nivel de protección por plataforma:**

| Protección | Plataformas | Recomendación |
|------------|-------------|---------------|
| 🔴 Muy Alta | LinkedIn, Glassdoor, Indeed | Usar API oficial o delays largos |
| 🟡 Media | Monster, Upwork, ZipRecruiter | Selenium + delays moderados |
| 🟢 Baja | Tecnoempleo, iTalenters | Selenium básico funciona |

### Mejores Prácticas

1. **Delays Generosos**:
   ```yaml
   scraping:
     delay_between_requests: 5  # Mínimo 3-5 segundos
     max_pages_per_session: 3   # Limitar páginas
   ```

2. **Respetar Límites**:
   ```python
   # No scrapear todo de una vez
   scraper.max_jobs = 20  # Pocas ofertas por sesión
   ```

3. **Usar APIs cuando estén disponibles**:
   - LinkedIn: https://developer.linkedin.com/
   - Glassdoor: https://www.glassdoor.com/developer/
   - Indeed: https://developer.indeed.com/
   - Upwork: https://developers.upwork.com/
   - CareerBuilder: API disponible

4. **Modo Headless**:
   ```yaml
   # Producción
   headless_mode: true

   # Debugging
   headless_mode: false  # Ver qué está haciendo
   ```

---

## 🐛 Debugging

### Si un scraper no funciona:

1. **Activar modo visual**:
   ```yaml
   scraping:
     headless_mode: false
   ```

2. **Ver logs detallados**:
   ```bash
   tail -f data/job_scraper.log
   ```

3. **Probar selectores en consola del navegador**:
   ```javascript
   // En DevTools Console
   document.querySelectorAll('.job-card')  // Ver si encuentra elementos
   ```

4. **Verificar que la URL es correcta**:
   ```python
   print(scraper.JOBS_URL)  # Verificar URL de búsqueda
   ```

5. **Aumentar timeouts**:
   ```yaml
   scraping:
     page_load_timeout: 60  # Aumentar si la red es lenta
   ```

---

## 📚 Recursos Adicionales

- **Plantilla de scraper**: `src/scrapers/_scraper_template.py`
- **Script generador**: `scripts/generate_scrapers.py`
- **Guía de Selenium**: `SELENIUM_GUIDE.md`
- **Soluciones anti-scraping**: `ANTI_SCRAPING_SOLUTIONS.md`

---

## 🤝 Contribuir

Para añadir un nuevo scraper:

1. Copiar `_scraper_template.py`
2. Renombrar a `{plataforma}_scraper.py`
3. Completar TODOs (URLs, selectores, etc.)
4. Registrar en `scraper_factory.py`:
   ```python
   from .{plataforma}_scraper import {Plataforma}Scraper

   _SCRAPERS = {
       '{plataforma}': {Plataforma}Scraper,
   }
   ```
5. Probar con `python -m pytest tests/test_{plataforma}_scraper.py`
6. Documentar en este archivo

---

## 📊 Estadísticas

**Implementación actual:**
- ✅ 2 scrapers completamente funcionales (Indeed, InfoJobs)
- ⚠️ 17 scrapers stub listos para completar
- 📝 Plantilla y herramientas de generación incluidas
- 🎯 19/19 plataformas cubiertas (100% de cobertura estructural)

**Próximos pasos:**
1. Completar selectores CSS en scrapers stub
2. Probar cada scraper con datos reales
3. Ajustar delays y configuración anti-ban
4. Considerar implementar APIs oficiales donde estén disponibles

---

¡Happy Scraping! 🕷️✨
