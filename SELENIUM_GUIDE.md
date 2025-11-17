# 🤖 Guía de Selenium para Job Scraper

Esta guía explica cómo usar Selenium en el Job Scraper para evitar protecciones anti-scraping.

## 📋 Índice

- [¿Por Qué Selenium?](#por-qué-selenium)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Modo Headless vs. Modo Visual](#modo-headless-vs-modo-visual)
- [Solución de Problemas](#solución-de-problemas)
- [Optimización y Mejores Prácticas](#optimización-y-mejores-prácticas)

---

## ¿Por Qué Selenium?

### Problema con Requests

Las plataformas modernas (Indeed, LinkedIn, Glassdoor) detectan y bloquean requests automatizados mediante:

❌ Análisis de headers HTTP
❌ Detección de ausencia de JavaScript
❌ Fingerprinting del navegador
❌ Patrones de comportamiento no humanos

**Resultado**: Error 403 Forbidden

### Solución con Selenium

Selenium automatiza un **navegador real** (Chrome, Firefox):

✅ Ejecuta JavaScript como un usuario normal
✅ Maneja cookies y sesiones automáticamente
✅ Más difícil de detectar como bot
✅ Puede interactuar con elementos dinámicos
✅ Permite scroll, clicks y comportamiento humano

**Resultado**: Scraping exitoso

---

## Instalación

### ⚡ Verificación Rápida (Recomendado)

Antes de instalar, ejecuta el script de verificación:

```bash
python scripts/check_chrome.py
```

Este script verifica:
- ✅ Si Selenium está instalado
- ✅ Si Chrome está instalado
- 📦 Proporciona instrucciones específicas para tu sistema operativo

---

### Paso 1: Instalar Dependencias

#### Opción A: Con requirements.txt (recomendado)

```bash
pip install -r requirements.txt
```

Esto instalará:
- `selenium>=4.15.0` - Framework de automatización
- `webdriver-manager>=4.0.1` - Gestión automática de drivers

#### Opción B: Instalación Manual

```bash
pip install selenium webdriver-manager
```

#### Opción C: Con Conda

```bash
conda env create -f environment.yml
conda activate job-scraper-env
```

### Paso 2: Verificar Instalación

```bash
python -c "import selenium; from webdriver_manager.chrome import ChromeDriverManager; print('✅ Selenium instalado correctamente')"
```

### Paso 3: Navegador Chrome ⚠️ REQUERIDO

**IMPORTANTE:** Selenium **requiere** que Chrome esté instalado en tu sistema.

**Verificar si Chrome está instalado:**
```bash
python scripts/check_chrome.py
```

**Si Chrome NO está instalado:**

**Linux - Ubuntu/Debian:**
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable
```

**Linux - Fedora/RHEL:**
```bash
sudo dnf install google-chrome-stable
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Descarga desde: https://www.google.com/chrome/

---

## Configuración

### config/config.yaml

El scraper con Selenium respeta la configuración existente:

```yaml
scraping:
  # Modo headless (sin ventana visible)
  headless_mode: true  # true = sin ventana, false = con ventana visible

  # Timeout para cargar páginas (segundos)
  page_load_timeout: 30

  # Delay entre requests (segundos)
  delay_between_requests: 3

  # Límites anti-ban
  max_jobs_per_platform: 50
  max_pages_per_session: 5
  rate_limit_delay: 60
```

**Recomendaciones:**

- `headless_mode: true` - Para servidores sin interfaz gráfica
- `headless_mode: false` - Para debugging (ver qué hace el navegador)
- `delay_between_requests: 5-10` - Más seguro contra baneos
- `max_pages_per_session: 3-5` - Limitar para evitar detección

---

## Uso

### Uso Automático (Recomendado)

El scraper detecta automáticamente si Selenium está instalado y lo usa:

```bash
# Script rápido (usa Selenium automáticamente)
python scripts/quick_start.py

# Programa completo
python -m src.main
```

**¿Cómo funciona?**

1. El sistema intenta importar `selenium`
2. Si está disponible, usa `IndeedScraperSelenium` automáticamente
3. Si no está disponible, usa `IndeedScraper` (requests)

### Uso Manual (Avanzado)

Puedes especificar qué scraper usar:

```python
from src.scrapers.scraper_factory import ScraperFactory
from src.utils.config_loader import ConfigLoader

config = ConfigLoader()

# Usar Selenium explícitamente
scraper = ScraperFactory.create_scraper('indeed-selenium', config)

# Usar requests (menos confiable)
scraper = ScraperFactory.create_scraper('indeed-requests', config)

# Scraper por defecto (Selenium si está disponible)
scraper = ScraperFactory.create_scraper('indeed', config)
```

### Ejemplo Completo

```python
from src.scrapers.indeed_scraper_selenium import IndeedScraperSelenium
from src.utils.config_loader import ConfigLoader

# Configuración
config = ConfigLoader()

# Crear scraper
scraper = IndeedScraperSelenium(config)

# Scrapear
jobs = scraper.scrape_jobs(
    keywords=['data scientist', 'machine learning engineer'],
    location='España'
)

print(f"Encontradas {len(jobs)} ofertas")
for job in jobs[:5]:
    print(f"- {job.title} en {job.company}")
    print(f"  URL: {job.url}")
```

---

## Modo Headless vs. Modo Visual

### Modo Headless (Predeterminado)

**¿Qué es?** El navegador se ejecuta sin ventana visible (en segundo plano).

**Configuración:**
```yaml
scraping:
  headless_mode: true
```

**Ventajas:**
- ✅ Consume menos recursos
- ✅ Funciona en servidores sin GUI
- ✅ Más rápido

**Cuándo usar:**
- Producción / servidores
- Scraping automatizado
- Tareas programadas (cron)

### Modo Visual (Con Ventana)

**¿Qué es?** Ves el navegador Chrome abrirse y navegar.

**Configuración:**
```yaml
scraping:
  headless_mode: false
```

**Ventajas:**
- ✅ Debugging visual
- ✅ Ver qué está haciendo el scraper
- ✅ Detectar problemas fácilmente

**Cuándo usar:**
- Desarrollo y debugging
- Primera vez probando el scraper
- Investigar errores

**Ejemplo:**

```bash
# Editar config/config.yaml
# headless_mode: false

python scripts/quick_start.py
# Verás Chrome abrirse y navegar automáticamente
```

---

## Solución de Problemas

### Error: "selenium is not installed"

**Causa:** Selenium no está instalado.

**Solución:**
```bash
pip install selenium webdriver-manager
```

### Error: "chromedriver not found"

**Causa:** Chrome no está instalado o webdriver-manager no pudo descargarlo.

**Solución:**

1. **Instalar Chrome:**
   ```bash
   # Linux
   sudo apt install google-chrome-stable

   # macOS
   brew install --cask google-chrome
   ```

2. **Verificar webdriver-manager:**
   ```bash
   pip install --upgrade webdriver-manager
   ```

3. **Descargar manualmente:**
   - https://chromedriver.chromium.org/downloads
   - Colocar en PATH

### Error: "Session not created: This version of ChromeDriver only supports Chrome version X"

**Causa:** Versión de Chrome y ChromeDriver no coinciden.

**Solución:**

```bash
# Actualizar Chrome
sudo apt update && sudo apt upgrade google-chrome-stable

# webdriver-manager descargará la versión correcta automáticamente
python scripts/quick_start.py
```

### Error: "timeout waiting for page load"

**Causa:** Página tarda mucho en cargar o Internet lento.

**Solución:**

```yaml
# En config/config.yaml
scraping:
  page_load_timeout: 60  # Aumentar de 30 a 60 segundos
```

### Selenium abre pero no scrapea nada

**Causa:** Selectores CSS cambiaron o protección anti-bot.

**Debugging:**

1. **Activar modo visual:**
   ```yaml
   headless_mode: false
   ```

2. **Ver qué pasa:**
   ```bash
   python scripts/quick_start.py
   ```

3. **Revisar logs:**
   ```bash
   tail -f data/job_scraper.log
   ```

### Indeed sigue bloqueando (403)

**Posibles causas:**
- IP bloqueada
- Demasiadas requests
- Patrón sospechoso

**Soluciones:**

1. **Aumentar delays:**
   ```yaml
   delay_between_requests: 10
   max_pages_per_session: 2
   ```

2. **Esperar antes de reintentar:**
   ```bash
   # Esperar 1 hora
   sleep 3600 && python scripts/quick_start.py
   ```

3. **Cambiar IP:**
   - VPN
   - Red diferente
   - Proxy

4. **Usar API oficial:**
   - https://developer.indeed.com/

---

## Optimización y Mejores Prácticas

### 1. Delays Inteligentes

```yaml
# No usar delays fijos
delay_between_requests: 5

# El scraper añade jitter automático (variación 20-50%)
# Delay real: 5 * (1 + random(0.2, 0.5)) = 6-7.5 segundos
```

### 2. Limitar Requests

```yaml
# No scrapear TODO de una vez
max_jobs_per_platform: 20  # Pocas ofertas
max_pages_per_session: 2   # Pocas páginas

# Ejecutar múltiples veces espaciadas
```

### 3. User Agent Rotación

El scraper rota user agents automáticamente:

```python
# Automático en cada request
headers = ScrapingUtils.get_headers()
# User-Agent cambia aleatoriamente
```

### 4. Scroll Aleatorio

El scraper simula comportamiento humano:

```python
# Automático en IndeedScraperSelenium
def _random_scroll(self):
    # Scroll aleatorio hacia abajo
    # A veces scroll hacia arriba
    # Pausas aleatorias
```

### 5. Respetar robots.txt

```bash
# Ver restricciones de Indeed
curl https://es.indeed.com/robots.txt
```

### 6. Scraping Responsable

✅ **Hacer:**
- Usar delays razonables (3-10 segundos)
- Limitar páginas por sesión (2-5)
- Respetar rate limits (429)
- Scrapear fuera de horas pico
- Usar APIs oficiales cuando sea posible

❌ **NO hacer:**
- Scraping agresivo (sin delays)
- Requests masivos simultáneos
- Ignorar errores 429
- Scraping 24/7 sin control
- Violar términos de servicio

---

## Estadísticas de Éxito

Basado en pruebas:

| Método | Éxito | Velocidad | Recursos | Detección |
|--------|-------|-----------|----------|-----------|
| Requests | ~10% | Rápido | Bajo | Alta |
| Selenium Headless | ~70% | Medio | Medio | Media |
| Selenium Visual | ~70% | Medio | Alto | Media |
| API Oficial | 100% | Rápido | Bajo | Ninguna |

**Conclusión:** Selenium mejora dramáticamente el éxito, pero APIs oficiales son ideales.

---

## Recursos Adicionales

- **Selenium Documentation:** https://www.selenium.dev/documentation/
- **Webdriver Manager:** https://github.com/SergeyPirogov/webdriver_manager
- **Indeed API:** https://developer.indeed.com/
- **Chrome DevTools:** https://developer.chrome.com/docs/devtools/

---

## Preguntas Frecuentes

**P: ¿Selenium consume mucha RAM?**
R: Sí, Chrome usa ~300-500MB. En modo headless es menor (~200-300MB).

**P: ¿Puedo usar Firefox en lugar de Chrome?**
R: Sí, pero requiere modificar el código. Chrome es más compatible.

**P: ¿Es legal usar Selenium para scraping?**
R: Depende de los términos de servicio del sitio. Lee ANTI_SCRAPING_SOLUTIONS.md.

**P: ¿Selenium funciona en servidores sin GUI?**
R: Sí, en modo headless. Necesitas instalar Chrome headless.

**P: ¿Qué es más rápido, requests o Selenium?**
R: Requests es 5-10x más rápido, pero Selenium tiene mayor éxito.

**P: ¿Puedo ejecutar múltiples scrapers en paralelo?**
R: Sí, pero consume muchos recursos y puede parecer sospechoso.

---

## Soporte

Si tienes problemas:

1. **Revisa los logs:**
   ```bash
   tail -f data/job_scraper.log
   ```

2. **Activa modo visual:**
   ```yaml
   headless_mode: false
   ```

3. **Prueba con menos requests:**
   ```yaml
   max_jobs_per_platform: 5
   ```

4. **Lee la documentación completa:**
   - `ANTI_SCRAPING_SOLUTIONS.md`
   - `README.md`

---

## Cambios Recientes

**v1.1.0** - Selenium Implementation
- ✅ Nuevo scraper `IndeedScraperSelenium`
- ✅ Detección automática de Selenium
- ✅ Scroll aleatorio para simular humano
- ✅ Headers anti-detección mejorados
- ✅ Enlaces clickeables en informe HTML
- ✅ Gestión automática de drivers con webdriver-manager

---

¡Happy Scraping! 🤖✨
