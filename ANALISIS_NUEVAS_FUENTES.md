# Análisis de Nuevas Fuentes de Ofertas Laborales

**Fecha:** 2025-11-19
**Objetivo:** Integrar 10 nuevas fuentes al scraper existente sin perder funcionalidad actual

---

## 1. ANÁLISIS INDIVIDUAL DE FUENTES

### 🔴 NIVEL ALTO - Protección Fuerte (Requiere undetected-chromedriver)

#### 1.1 Glassdoor (https://www.glassdoor.es)
- **Carga:** JavaScript pesado + React
- **Protección:** Cloudflare + detección de bot avanzada
- **Autenticación:** NO requerida para ver ofertas, SÍ para detalles completos
- **Paginación:** Scroll infinito + lazy loading
- **Selectores:** Dinámicos, cambian frecuentemente
- **Barreras:**
  - ❌ Bloquea requests simples (403)
  - ❌ Detecta Selenium estándar
  - ⚠️  Límite de ~50 ofertas sin login
  - ⚠️  Cookies y fingerprinting
- **Estrategia:** undetected-chromedriver + delays largos (15-20s)
- **Prioridad:** MEDIA (valor alto pero difícil)

#### 1.2 Monster (https://www.monster.es)
- **Carga:** JavaScript + API REST
- **Protección:** Cloudflare + rate limiting agresivo
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional (?page=1,2,3)
- **Selectores:** Relativamente estables
- **Barreras:**
  - ❌ Bloquea requests (403)
  - ⚠️  API puede ser más fácil que scraping HTML
  - ⚠️  Rate limit: ~1 request/10s
- **Estrategia:** undetected-chromedriver O requests a API (si se descubre)
- **Prioridad:** ALTA (muchas ofertas)

#### 1.3 InfoEmpleo (https://www.infoempleo.com)
- **Carga:** JavaScript moderado
- **Protección:** Cloudflare
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional
- **Selectores:** Estables
- **Barreras:**
  - ❌ Bloquea fetch directo
  - ✅ Menos agresivo que Glassdoor
- **Estrategia:** undetected-chromedriver + delays moderados (10s)
- **Prioridad:** ALTA (específico para España)

### 🟡 NIVEL MEDIO - Protección Moderada (Selenium + delays)

#### 1.4 Workana (https://www.workana.com)
- **Carga:** JavaScript + filtros dinámicos
- **Protección:** Moderada (sin Cloudflare visible)
- **Autenticación:** NO requerida para ver proyectos
- **Paginación:** Scroll infinito
- **Selectores:** Razonablemente estables
- **Barreras:**
  - ❌ Bloquea requests simples
  - ✅ Acepta Selenium con headers correctos
  - ⚠️  Enfocado en freelance, no empleo tradicional
- **Estrategia:** Selenium estándar + user-agent rotation
- **Prioridad:** BAJA (diferente perfil de ofertas)

#### 1.5 SimplyHired (https://www.simplyhired.com)
- **Carga:** JavaScript + lazy loading
- **Protección:** Moderada
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional + algunos filtros con scroll
- **Selectores:** Moderadamente estables
- **Barreras:**
  - ⚠️  Geo-blocking para algunas regiones
  - ⚠️  Agregador (muchas duplicadas)
- **Estrategia:** Selenium + delays + filtro de duplicados robusto
- **Prioridad:** MEDIA

#### 1.6 ZipRecruiter (https://www.ziprecruiter.ie)
- **Carga:** JavaScript pesado
- **Protección:** Moderada-Alta
- **Autenticación:** NO requerida
- **Paginación:** Paginación con parámetros en URL
- **Selectores:** Dinámicos
- **Barreras:**
  - ⚠️  .ie (Irlanda) - posible geo-blocking
  - ⚠️  Agregador con muchas duplicadas
- **Estrategia:** Selenium + verificar si .es existe
- **Prioridad:** BAJA (fuera de España)

### 🟢 NIVEL BAJO - Más Accesibles

#### 1.7 Randstad (https://www.randstad.com)
- **Carga:** JavaScript ligero
- **Protección:** Baja
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional
- **Selectores:** Estables (sitio corporativo)
- **Barreras:**
  - ✅ Menos agresivo con bots
  - ⚠️  Estructura puede variar por país
- **Estrategia:** Selenium simple + delays cortos (5s)
- **Prioridad:** ALTA (ETT grande, muchas ofertas en España)

#### 1.8 Michael Page (https://www.michaelpage.com)
- **Carga:** JavaScript moderado
- **Protección:** Baja-Moderada
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional
- **Selectores:** Estables
- **Barreras:**
  - ✅ Sitio corporativo bien estructurado
  - ✅ HTML semántico
- **Estrategia:** Selenium simple
- **Prioridad:** MEDIA (ofertas especializadas)

#### 1.9 TecnoEmpleo (https://www.tecnoempleo.com)
- **Carga:** JavaScript moderado
- **Protección:** Moderada
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional
- **Selectores:** Estables
- **Barreras:**
  - ❌ Bloquea requests simples
  - ✅ Acepta Selenium bien
  - ✅ Específico para tech en España
- **Estrategia:** Selenium + delays moderados
- **Prioridad:** ALTA (específico para Data Science)

#### 1.10 Hays (https://www.hays.es)
- **Carga:** JavaScript ligero
- **Protección:** Baja
- **Autenticación:** NO requerida
- **Paginación:** Paginación tradicional
- **Selectores:** Estables
- **Barreras:**
  - ✅ Sitio corporativo accesible
  - ✅ Buena estructura HTML
- **Estrategia:** Selenium simple
- **Prioridad:** MEDIA (ETT especializada)

---

## 2. RESUMEN ESTRATÉGICO

### Herramientas Necesarias por Nivel

| Nivel | Fuentes | Herramienta | Delays | Éxito Estimado |
|-------|---------|-------------|--------|----------------|
| 🔴 Alto | Glassdoor, Monster, InfoEmpleo | undetected-chromedriver | 15-20s | 60-70% |
| 🟡 Medio | Workana, SimplyHired, TecnoEmpleo | Selenium + user-agent | 8-12s | 80-85% |
| 🟢 Bajo | Randstad, Michael Page, Hays | Selenium estándar | 5-8s | 90-95% |

### Priorización Recomendada

**FASE 1 (Quick Wins):**
1. ✅ Randstad - Alta prioridad, baja dificultad
2. ✅ TecnoEmpleo - Alta prioridad para tech, dificultad media
3. ✅ Hays - Media prioridad, baja dificultad

**FASE 2 (Valor Alto):**
4. ⚠️  InfoEmpleo - Alta prioridad, alta dificultad
5. ⚠️  Monster - Alta prioridad, alta dificultad
6. ⚠️  Michael Page - Media prioridad, dificultad media

**FASE 3 (Complementarias):**
7. ⚠️  SimplyHired - Media prioridad
8. ⚠️  Glassdoor - Media prioridad, muy difícil

**DESCARTABLES (por ahora):**
9. ❌ Workana - Perfil diferente (freelance)
10. ❌ ZipRecruiter - Fuera de España (.ie)

---

## 3. BARRERAS TÉCNICAS COMUNES

### 3.1 Cloudflare
- **Afecta:** Glassdoor, Monster, InfoEmpleo, TecnoEmpleo
- **Solución:** undetected-chromedriver
- **Indicador:** Página "Un momento..." o "Checking your browser"

### 3.2 Rate Limiting
- **Afecta:** Todas
- **Solución:** Delays entre requests (5-20s según nivel)
- **Indicador:** 429 Too Many Requests o bloqueos temporales

### 3.3 Geo-blocking
- **Afecta:** ZipRecruiter (.ie)
- **Solución:** Proxies o buscar versión .es
- **Indicador:** Redirecciones o contenido diferente

### 3.4 Contenido Dinámico
- **Afecta:** Todas (JavaScript)
- **Solución:** Selenium/Playwright con waits
- **Indicador:** HTML vacío con requests

### 3.5 Selectores Dinámicos
- **Afecta:** Glassdoor, Monster
- **Solución:** Múltiples selectores fallback + actualizaciones frecuentes
- **Indicador:** NoSuchElementException

---

## 4. ESTRATEGIA ANTI-BAN GENERAL

### 4.1 Headers Realistas
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Accept': 'text/html,application/xhtml+xml',
    'Referer': 'https://www.google.com/',
}
```

### 4.2 Delays Inteligentes
- Entre páginas: 5-20s (según nivel)
- Entre keywords: 30-60s
- Random jitter: ±20%

### 4.3 User-Agent Rotation
- Pool de 10-15 user-agents reales
- Cambiar cada N requests

### 4.4 Cookies y Sesiones
- Mantener sesión entre requests
- Aceptar cookies si es necesario
- Simular navegación humana (homepage → search)

### 4.5 Límites de Scraping
- Max ofertas por fuente: 100-200
- Max páginas por fuente: 10-15
- Timeout total por fuente: 10 minutos

---

## 5. ESTIMACIÓN DE OFERTAS

| Fuente | Ofertas Estimadas | Tiempo Estimado | Fiabilidad |
|--------|-------------------|-----------------|------------|
| Indeed (actual) | 150-200 | 15min | ✅ Alta |
| Randstad | 50-100 | 8min | ✅ Alta |
| TecnoEmpleo | 80-120 | 10min | 🟡 Media |
| InfoEmpleo | 100-150 | 12min | 🟡 Media |
| Monster | 80-120 | 12min | 🟡 Media |
| Hays | 30-60 | 6min | ✅ Alta |
| Michael Page | 40-80 | 8min | ✅ Alta |
| SimplyHired | 60-100 | 10min | 🟡 Media |
| Glassdoor | 30-50 | 15min | ⚠️  Baja |
| **TOTAL** | **620-980 únicas** | **~2h** | - |

*Después de eliminar duplicados: **400-600 ofertas únicas***

---

## 6. RECOMENDACIÓN FINAL

### Implementar en Fases:

**FASE 1 (1-2 semanas):**
- Randstad
- Hays
- TecnoEmpleo
- Resultado: +160-280 ofertas

**FASE 2 (2-3 semanas):**
- InfoEmpleo
- Monster
- Michael Page
- Resultado: +220-350 ofertas

**FASE 3 (opcional):**
- SimplyHired
- Glassdoor
- Resultado: +90-150 ofertas

**Total estimado:** 400-600 ofertas únicas de Data Science en España
