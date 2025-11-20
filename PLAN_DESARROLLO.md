# Plan de Desarrollo - Integración Modular de Nuevas Fuentes

**Versión Estable Actual:** `claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6`
**Ofertas Actuales:** 684 ofertas (Indeed)
**Objetivo:** Añadir 7-8 fuentes nuevas → 400-600 ofertas únicas totales

---

## 1. ESTRATEGIA GIT - DESARROLLO SEGURO

### 1.1 Estructura de Ramas

```
main (producción)
│
├── claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6 (ESTABLE - 684 ofertas)
│   └── [NO TOCAR - versión funcional actual]
│
└── feature/multi-source-scrapers (NUEVA)
    ├── feature/randstad-scraper
    ├── feature/tecnoempleo-scraper
    ├── feature/hays-scraper
    ├── feature/infoemple

o-scraper
    ├── feature/monster-scraper
    └── feature/michaelpage-scraper
```

### 1.2 Workflow de Desarrollo

```bash
# 1. Crear rama de desarrollo principal (desde estable)
git checkout claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6
git checkout -b feature/multi-source-scrapers

# 2. Para cada nueva fuente, crear sub-rama
git checkout -b feature/randstad-scraper

# 3. Desarrollar y probar scraper individual
# ...código...

# 4. Merge a feature/multi-source-scrapers solo si funciona
git checkout feature/multi-source-scrapers
git merge feature/randstad-scraper

# 5. NUNCA hacer merge a rama estable hasta que TODO esté probado
```

### 1.3 Tags de Seguridad

```bash
# Tag de la versión estable actual (backup)
git tag -a v1.0-stable-indeed-only -m "Versión estable: 684 ofertas de Indeed"
git push origin v1.0-stable-indeed-only

# Tags por cada fuente añadida
git tag -a v1.1-randstad -m "Añadido scraper de Randstad"
git tag -a v1.2-tecnoempleo -m "Añadido scraper de TecnoEmpleo"
# etc...
```

---

## 2. ARQUITECTURA MODULAR

### 2.1 Estructura de Archivos (NUEVA)

```
compare_jobs/
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py              [✅ YA EXISTE]
│   │   ├── indeed_scraper_selenium.py   [✅ FUNCIONAL]
│   │   │
│   │   ├── __scrapers_v2__/            [🆕 NUEVOS]
│   │   │   ├── __init__.py
│   │   │   ├── base_scraper_v2.py      [🆕 Mejorado]
│   │   │   ├── randstad_scraper.py     [🆕 FASE 1]
│   │   │   ├── tecnoempleo_scraper.py  [🆕 FASE 1]
│   │   │   ├── hays_scraper.py         [🆕 FASE 1]
│   │   │   ├── infoemple_scraper.py    [🆕 FASE 2]
│   │   │   ├── monster_scraper.py      [🆕 FASE 2]
│   │   │   └── michaelpage_scraper.py  [🆕 FASE 2]
│   │   │
│   │   └── scraper_factory.py          [✅ YA EXISTE - ACTUALIZAR]
│   │
│   ├── services/
│   │   ├── deduplicator.py             [🆕 Servicio de deduplicación]
│   │   ├── scraper_pool.py             [🆕 Gestor de scrapers paralelos]
│   │   └── rate_limiter.py             [🆕 Control de rate limits]
│   │
│   └── utils/
│       ├── anti_ban.py                 [🆕 Utilidades anti-ban]
│       └── selenium_helpers.py         [🆕 Helpers Selenium]
│
├── config/
│   ├── config.yaml                     [✅ ACTUALIZAR]
│   └── scrapers_config.yaml            [🆕 Config por scraper]
│
├── scripts/
│   ├── search_all_platforms.py         [✅ ACTUALIZAR]
│   ├── test_single_scraper.py          [🆕 Test individual]
│   └── validate_scrapers.py            [🆕 Validación batch]
│
└── tests/
    ├── test_randstad.py                [🆕]
    ├── test_tecnoempleo.py             [🆕]
    └── test_integration.py             [🆕]
```

### 2.2 Base Scraper V2 (Mejorado)

**Nuevas Características:**
```python
class BaseScraperV2(BaseScraper):
    """
    Scraper base mejorado con:
    - Soporte undetected-chromedriver
    - Rate limiting integrado
    - Retry automático con backoff
    - Métricas de éxito/fallo
    - Logging estructurado
    - Health checks
    """

    def __init__(self, config):
        super().__init__(config)
        self.driver_type = 'undetected'  # o 'selenium'
        self.rate_limiter = RateLimiter(requests_per_minute=5)
        self.metrics = ScraperMetrics()
        self.max_retries = 3
        self.retry_backoff = [30, 60, 120]  # segundos

    @retry_with_backoff(max_attempts=3)
    def scrape_jobs(self, keywords, location):
        """Con retry automático y rate limiting."""
        pass

    def health_check(self) -> bool:
        """Verifica que el scraper está funcionando."""
        pass

    def get_metrics(self) -> dict:
        """Retorna métricas de scraping."""
        return {
            'total_requests': self.metrics.requests,
            'successful': self.metrics.successful,
            'failed': self.metrics.failed,
            'avg_response_time': self.metrics.avg_time,
            'rate_limit_hits': self.metrics.rate_limits,
        }
```

### 2.3 Scraper Factory (Actualizado)

```python
class ScraperFactory:
    """Factory pattern mejorado con registro dinámico."""

    _scrapers_v1 = {
        'indeed': IndeedScraperSelenium,
    }

    _scrapers_v2 = {
        'randstad': RandstadScraper,
        'tecnoempleo': TecnoEmpleoScraper,
        'hays': HaysScraper,
        'infoemple': InfoEmpleoScraper,
        'monster': MonsterScraper,
        'michaelpage': MichaelPageScraper,
    }

    @classmethod
    def create(cls, platform: str, config, version='v2'):
        """
        Crea scraper según plataforma.

        Args:
            platform: 'indeed', 'randstad', etc.
            config: ConfigLoader
            version: 'v1' (estable) o 'v2' (nuevos)
        """
        scrapers = cls._scrapers_v1 if version == 'v1' else cls._scrapers_v2

        if platform in scrapers:
            return scrapers[platform](config)

        raise ValueError(f"Scraper '{platform}' no encontrado")

    @classmethod
    def get_all_active(cls, config) -> List[BaseScraper]:
        """Retorna todos los scrapers habilitados en config."""
        active = []

        # V1 (estable)
        if config.get('platforms.indeed.enabled'):
            active.append(cls.create('indeed', config, version='v1'))

        # V2 (nuevos)
        for platform in cls._scrapers_v2.keys():
            if config.get(f'platforms_v2.{platform}.enabled'):
                active.append(cls.create(platform, config, version='v2'))

        return active
```

---

## 3. CONFIGURACIÓN MODULAR

### 3.1 config/scrapers_config.yaml (NUEVO)

```yaml
# Configuración específica por scraper

scrapers_v2:
  randstad:
    enabled: true
    priority: 1
    driver_type: 'selenium'  # no necesita undetected
    delay_between_pages: 5
    max_pages: 10
    selectors:
      job_card: 'div.job-item'
      title: 'h2.job-title'
      company: 'span.company-name'
      location: 'span.location'
      description: 'div.description'

  tecnoempleo:
    enabled: true
    priority: 2
    driver_type: 'selenium'
    delay_between_pages: 8
    max_pages: 12
    selectors:
      job_card: 'article.oferta'
      title: 'h2.titulo'
      company: 'a.empresa'
      location: 'span.ubicacion'

  hays:
    enabled: true
    priority: 3
    driver_type: 'selenium'
    delay_between_pages: 5
    max_pages: 10

  infoemple:
    enabled: false  # Fase 2
    priority: 4
    driver_type: 'undetected'  # Necesita anti-Cloudflare
    delay_between_pages: 15
    max_pages: 8

  monster:
    enabled: false  # Fase 2
    priority: 5
    driver_type: 'undetected'
    delay_between_pages: 12
    max_pages: 10

  michaelpage:
    enabled: false  # Fase 2
    priority: 6
    driver_type: 'selenium'
    delay_between_pages: 8
    max_pages: 8

# Anti-ban global
anti_ban:
  min_delay: 5
  max_delay: 15
  jitter_percent: 20
  user_agent_rotation: true
  max_requests_per_hour: 200

# Deduplicación
deduplication:
  method: 'url+title+company'  # Cómo identificar duplicados
  similarity_threshold: 0.85  # Para fuzzy matching
  keep_first: true  # Mantener primera ocurrencia
```

---

## 4. SERVICIOS DE SOPORTE

### 4.1 Deduplicador (src/services/deduplicator.py)

```python
class JobDeduplicator:
    """
    Elimina ofertas duplicadas entre múltiples fuentes.

    Métodos:
    - Por URL exacta
    - Por título + empresa
    - Por fuzzy matching (similar pero no idéntico)
    """

    def deduplicate(self, jobs: List[JobOffer]) -> List[JobOffer]:
        """
        Elimina duplicados de lista de ofertas.

        Returns:
            Lista sin duplicados + estadísticas
        """
        pass

    def get_stats(self) -> dict:
        """
        Returns:
            {
                'total_input': 500,
                'total_output': 380,
                'duplicates_removed': 120,
                'by_source': {'indeed': 10, 'monster': 25, ...}
            }
        """
        pass
```

### 4.2 Scraper Pool (src/services/scraper_pool.py)

```python
class ScraperPool:
    """
    Ejecuta múltiples scrapers en paralelo o secuencial.

    Features:
    - Ejecución paralela (ThreadPool)
    - Timeout por scraper
    - Agregación de resultados
    - Manejo de errores individual
    """

    def run_all(self, scrapers: List[BaseScraper],
                keywords, location, parallel=False):
        """
        Ejecuta todos los scrapers.

        Args:
            parallel: True = paralelo, False = secuencial
        """
        if parallel:
            return self._run_parallel(scrapers, keywords, location)
        else:
            return self._run_sequential(scrapers, keywords, location)

    def _run_parallel(self, scrapers, keywords, location):
        """Ejecuta scrapers en paralelo (más rápido, más riesgo)."""
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(s.scrape_jobs, keywords, location): s
                for s in scrapers
            }
            # ...
```

### 4.3 Rate Limiter (src/services/rate_limiter.py)

```python
class RateLimiter:
    """
    Control de rate limiting por scraper.

    Evita:
    - Demasiados requests por minuto
    - Bloqueos por exceso de tráfico
    - Sobrecarga del servidor target
    """

    def __init__(self, requests_per_minute=10):
        self.rpm = requests_per_minute
        self.requests = deque()

    def wait_if_needed(self):
        """Espera si se excedió el rate limit."""
        now = time.time()
        # Limpiar requests antiguos (>1 minuto)
        while self.requests and self.requests[0] < now - 60:
            self.requests.popleft()

        if len(self.requests) >= self.rpm:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit alcanzado, esperando {sleep_time:.1f}s")
                time.sleep(sleep_time)

        self.requests.append(now)
```

---

## 5. SCRIPT PRINCIPAL ACTUALIZADO

### 5.1 search_all_platforms_v2.py (NUEVO)

```python
#!/usr/bin/env python3
"""
Scraper multi-fuente con soporte V1 (estable) + V2 (nuevos).
"""

from src.scrapers.scraper_factory import ScraperFactory
from src.services.deduplicator import JobDeduplicator
from src.services.scraper_pool import ScraperPool

def main():
    config = ConfigLoader()
    keywords = config.get('search_terms.keywords')
    location = config.get('search_terms.locations')[0]

    logger.info("=" * 80)
    logger.info("🚀 JOB SCRAPER MULTI-FUENTE V2")
    logger.info("=" * 80)

    # Obtener todos los scrapers activos (V1 + V2)
    scrapers = ScraperFactory.get_all_active(config)

    logger.info(f"📋 Scrapers habilitados: {len(scrapers)}")
    for s in scrapers:
        logger.info(f"   - {s._get_platform_name()}")

    # Ejecutar scrapers
    pool = ScraperPool()
    all_jobs = pool.run_all(
        scrapers,
        keywords,
        location,
        parallel=False  # Secuencial para evitar bloqueos
    )

    logger.info(f"\n📦 Total ofertas recopiladas: {len(all_jobs)}")

    # Deduplicación
    deduplicator = JobDeduplicator()
    unique_jobs = deduplicator.deduplicate(all_jobs)

    logger.info(f"🔧 Ofertas únicas: {len(unique_jobs)}")
    logger.info(f"🗑️  Duplicados eliminados: {len(all_jobs) - len(unique_jobs)}")

    # Análisis y reportes (igual que antes)
    # ...

if __name__ == "__main__":
    main()
```

---

## 6. TESTING STRATEGY

### 6.1 Tests Individuales

```python
# tests/test_randstad.py
def test_randstad_scraper():
    """Test básico de Randstad scraper."""
    config = ConfigLoader()
    scraper = RandstadScraper(config)

    jobs = scraper.scrape_jobs(['data scientist'], 'España')

    assert len(jobs) > 0, "Debe encontrar al menos 1 oferta"
    assert all(j.title for j in jobs), "Todas las ofertas deben tener título"
    assert all(j.company for j in jobs), "Todas deben tener empresa"
```

### 6.2 Test de Integración

```python
# tests/test_integration.py
def test_multi_source_integration():
    """Test de integración completo."""
    config = ConfigLoader()

    # Habilitar solo Randstad + TecnoEmpleo + Hays
    config.set('platforms_v2.randstad.enabled', True)
    config.set('platforms_v2.tecnoempleo.enabled', True)
    config.set('platforms_v2.hays.enabled', True)

    scrapers = ScraperFactory.get_all_active(config)
    pool = ScraperPool()

    all_jobs = pool.run_all(scrapers, ['data scientist'], 'España')

    # Verificaciones
    assert len(all_jobs) > 50, "Debe encontrar al menos 50 ofertas combinadas"

    # Verificar que hay ofertas de múltiples fuentes
    sources = set(j.platform for j in all_jobs)
    assert len(sources) >= 2, "Debe haber ofertas de al menos 2 fuentes"
```

---

## 7. CRONOGRAMA DE DESARROLLO

### Semana 1: Setup + FASE 1
- **Día 1-2:** Setup rama feature/multi-source-scrapers
- **Día 3:** Implementar Randstad scraper
- **Día 4:** Implementar Hays scraper
- **Día 5:** Implementar TecnoEmpleo scraper
- **Día 6-7:** Testing + integración FASE 1

**Entregable:** 3 nuevos scrapers funcionando + 160-280 ofertas adicionales

### Semana 2: FASE 2
- **Día 8-9:** Implementar InfoEmpleo (con undetected)
- **Día 10:** Implementar Monster
- **Día 11:** Implementar Michael Page
- **Día 12-14:** Testing + optimización

**Entregable:** 6 scrapers totales + 380-630 ofertas adicionales

### Semana 3: Refinamiento
- **Día 15-16:** Deduplicación avanzada
- **Día 17:** Mejoras de performance
- **Día 18-19:** Documentación
- **Día 20-21:** Testing completo + bug fixing

**Entregable:** Sistema completo con 400-600 ofertas únicas

---

## 8. MÉTRICAS DE ÉXITO

### Por Scraper
- ✅ Tasa de éxito >80%
- ✅ Ofertas encontradas >30
- ✅ Tiempo ejecución <10 minutos
- ✅ Sin crashes

### Global
- ✅ Total ofertas únicas: 400-600
- ✅ Duplicados <20%
- ✅ Tiempo total <2 horas
- ✅ Indeed (V1) sigue funcionando perfectamente

---

## 9. ROLLBACK PLAN

Si algo sale mal:

```bash
# 1. Volver a rama estable
git checkout claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6

# 2. O volver a tag específico
git checkout v1.0-stable-indeed-only

# 3. Versión estable siempre disponible
git checkout -b hotfix/emergency-rollback v1.0-stable-indeed-only
```

**La versión estable NUNCA se toca hasta que todo esté 100% probado.**

---

## 10. PRÓXIMOS PASOS

1. ✅ Revisar y aprobar este plan
2. ✅ Crear rama `feature/multi-source-scrapers`
3. ✅ Crear tag de backup `v1.0-stable-indeed-only`
4. ⏳ Implementar PoC (Randstad + TecnoEmpleo)
5. ⏳ Testing PoC
6. ⏳ Continuar con FASE 1 completa

**¿Aprobamos el plan y procedemos con el PoC?**
