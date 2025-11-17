# 🛡️ Soluciones para Protección Anti-Scraping

## El Problema

Indeed y otras plataformas modernas de empleo tienen **protección anti-scraping muy agresiva** que detecta y bloquea peticiones automatizadas.

### Errores Comunes:
- **403 Forbidden**: El servidor detectó que no eres un navegador real
- **429 Too Many Requests**: Demasiadas peticiones en poco tiempo
- **CAPTCHA**: El sitio requiere verificación humana

## ¿Por Qué Ocurre?

Las plataformas detectan scraping mediante:

1. **Análisis de headers HTTP**: Headers incompletos o sospechosos
2. **Fingerprinting de navegador**: Falta de JavaScript, cookies, etc.
3. **Patrones de comportamiento**: Peticiones demasiado rápidas o regulares
4. **Falta de interacciones**: No hay movimiento de mouse, scroll, etc.

## 🔧 Soluciones Implementadas (Limitadas)

Este proyecto ya incluye varias medidas anti-detección:

✅ User agents rotativos realistas
✅ Headers HTTP completos
✅ Delays aleatorios con jitter
✅ Sesiones persistentes con cookies
✅ Detección y manejo de rate limiting (429)
✅ Límite de páginas por sesión

**PERO** esto **NO es suficiente** para sitios con protección agresiva como Indeed.

## 🎯 Soluciones Recomendadas

### Opción 1: Usar APIs Oficiales (RECOMENDADO)

La mejor solución es usar APIs oficiales:

| Plataforma | API Disponible | Enlace |
|------------|----------------|--------|
| Indeed | ✅ Sí | https://developer.indeed.com/ |
| InfoJobs | ✅ Sí | https://developer.infojobs.net/ |
| LinkedIn | ✅ Sí | https://developer.linkedin.com/ |
| Glassdoor | ❌ No pública | - |
| Monster | ✅ Sí (limitada) | https://partner.monster.com/ |

**Ventajas:**
- Legal y autorizado
- Datos estructurados y completos
- Sin bloqueos ni baneos
- Datos actualizados y confiables

**Desventajas:**
- Requiere registro y aprobación
- Puede tener costos o límites de uso
- Requiere implementación específica

### Opción 2: Usar Selenium/Playwright (Más Realista)

Para sitios sin API, usar navegadores automatizados reales:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
# ... scraping code
```

**Ventajas:**
- Ejecuta JavaScript real
- Cookies y sesiones automáticas
- Puede resolver CAPTCHAs manualmente
- Más difícil de detectar

**Desventajas:**
- Mucho más lento (5-10x)
- Consume más recursos (CPU, RAM)
- Requiere gestionar drivers del navegador
- Aún puede ser detectado

### Opción 3: Servicios Profesionales de Scraping

Usar servicios especializados:

- **ScrapingBee**: https://www.scrapingbee.com/
- **Bright Data**: https://brightdata.com/
- **ScraperAPI**: https://www.scraperapi.com/
- **Apify**: https://apify.com/

**Ventajas:**
- Rotan IPs automáticamente
- Manejan CAPTCHAs
- Altas tasas de éxito
- Infraestructura gestionada

**Desventajas:**
- Costos mensuales
- Dependencia de terceros

### Opción 4: Plataformas Menos Restrictivas

Enfocarse en plataformas con menos protección:

**✅ Más Accesibles:**
- Tecnoempleo
- Turijobs
- Empleate
- Portales locales/regionales

**❌ Muy Restrictivas:**
- Indeed
- LinkedIn
- Glassdoor
- Upwork

## 🚀 Qué Hacer Ahora

### Para Desarrollo/Pruebas:

1. **Usa plataformas menos restrictivas** para probar tu código
2. **Implementa logs detallados** para entender los bloqueos
3. **Aumenta delays** entre peticiones (5-10 segundos)
4. **Limita requests** a muy pocas ofertas por sesión

### Para Producción:

1. **Registra y usa APIs oficiales** (Indeed, InfoJobs, LinkedIn)
2. **Implementa Selenium** para sitios sin API
3. **Considera servicios de scraping** si el presupuesto lo permite
4. **Combina fuentes**: APIs + scraping selectivo de sitios menos restrictivos

## 📝 Modificar la Configuración

### Aumentar Delays (config/config.yaml):

```yaml
scraping:
  # Aumentar delay entre requests
  delay_between_requests: 10  # De 3 a 10 segundos

  # Reducir ofertas por plataforma
  max_jobs_per_platform: 10   # De 50 a 10

  # Reducir páginas por sesión
  max_pages_per_session: 2    # De 5 a 2

  # Delay tras rate limit
  rate_limit_delay: 120       # De 60 a 120 segundos
```

### Habilitar Solo Plataformas Accesibles:

```yaml
platforms:
  indeed:
    enabled: false  # ← Deshabilitar Indeed temporalmente

  infojobs:
    enabled: true   # ← Usar solo con API oficial

  tecnoempleo:
    enabled: true   # ← Menos restrictivo
```

## 📚 Recursos Adicionales

- [Web Scraping Best Practices](https://scrapinghub.com/best-practices/)
- [Indeed API Documentation](https://developer.indeed.com/docs/getting-started)
- [InfoJobs API Documentation](https://developer.infojobs.net/getting-started.xhtml)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)

## ⚖️ Consideraciones Legales

**IMPORTANTE**: El web scraping puede violar los términos de servicio de algunos sitios.

- ✅ **Legal**: Usar APIs oficiales con autorización
- ⚠️ **Zona gris**: Scraping de datos públicos para uso personal/investigación
- ❌ **Ilegal**: Scraping comercial sin autorización, violación de ToS

**Recomendación**: Siempre leer y respetar los `robots.txt` y términos de servicio de cada sitio.

---

## 🎓 Conclusión

El scraping web moderno es cada vez más difícil debido a las protecciones anti-bot. Para un proyecto serio:

1. **Prioriza APIs oficiales**
2. **Usa Selenium para casos sin API**
3. **Respeta límites y términos de servicio**
4. **Considera servicios profesionales si es necesario**

Este proyecto proporciona una base sólida, pero **es responsabilidad del usuario adaptarlo** según sus necesidades y restricciones legales/técnicas.
