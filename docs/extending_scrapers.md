# Guía para Extender el Sistema con Nuevos Scrapers

Esta guía te ayudará a implementar scrapers para las plataformas que actualmente solo tienen template.

## Estructura de un Scraper

Todos los scrapers heredan de `BaseScraper` y deben implementar dos métodos principales:

```python
from src.scrapers.base_scraper import BaseScraper
from src.models.job_offer import JobOffer

class MiScraper(BaseScraper):
    BASE_URL = "https://plataforma.com"

    def _get_platform_name(self) -> str:
        return "NombrePlataforma"

    def scrape_jobs(self, keywords, location) -> List[JobOffer]:
        # Implementación del scraping
        pass
```

## Pasos para Implementar un Nuevo Scraper

### 1. Analizar el Sitio Web

Antes de escribir código, analiza la estructura del sitio:

```bash
# Inspecciona la página con DevTools del navegador
# Identifica:
# - URL de búsqueda y sus parámetros
# - Selectores CSS de las tarjetas de trabajo
# - Estructura de paginación
# - Protecciones anti-bot (Cloudflare, etc.)
```

### 2. Crear el Archivo del Scraper

```bash
# Copia el template
cp src/scrapers/generic_scraper.py src/scrapers/miplataforma_scraper.py
```

### 3. Implementar los Métodos

#### Método `_build_search_url`

```python
def _build_search_url(self, keyword: str, location: str, page: int) -> str:
    """Construye la URL de búsqueda."""
    params = {
        'q': keyword,          # Parámetro de búsqueda
        'l': location,         # Parámetro de ubicación
        'start': (page - 1) * 20  # Offset de paginación
    }

    return ScrapingUtils.build_search_url(
        f"{self.BASE_URL}/jobs/search",
        params,
        page
    )
```

#### Método `_parse_job_element`

```python
def _parse_job_element(self, elem) -> Optional[JobOffer]:
    """Extrae información de un elemento de oferta."""
    try:
        # 1. Título (REQUERIDO)
        title_elem = elem.find('h2', class_='job-title')
        if not title_elem:
            return None
        title = ScrapingUtils.clean_text(title_elem.get_text())

        # 2. Empresa (REQUERIDO)
        company_elem = elem.find('span', class_='company')
        company = ScrapingUtils.clean_text(
            company_elem.get_text() if company_elem else "Desconocido"
        )

        # 3. URL (REQUERIDO)
        link_elem = elem.find('a', class_='job-link')
        job_url = ""
        if link_elem and link_elem.get('href'):
            job_url = link_elem['href']
            if not job_url.startswith('http'):
                job_url = self.BASE_URL + job_url

        # 4. Ubicación (OPCIONAL)
        location_elem = elem.find('span', class_='location')
        location = ScrapingUtils.clean_text(
            location_elem.get_text() if location_elem else ""
        )

        # 5. Descripción (OPCIONAL)
        desc_elem = elem.find('div', class_='description')
        description = ScrapingUtils.clean_text(
            desc_elem.get_text() if desc_elem else ""
        )

        # 6. Salario (OPCIONAL)
        salary_elem = elem.find('span', class_='salary')
        salary_info = {'salary_min': None, 'salary_max': None, 'currency': 'EUR'}
        if salary_elem:
            salary_text = salary_elem.get_text()
            salary_info = ScrapingUtils.extract_salary(salary_text)

        # 7. Tipo de ubicación (OPCIONAL)
        work_location = WorkLocation.UNKNOWN
        if location:
            location_lower = location.lower()
            if 'remot' in location_lower:
                work_location = WorkLocation.REMOTE
            elif 'híbrid' in location_lower or 'hybrid' in location_lower:
                work_location = WorkLocation.HYBRID
            else:
                work_location = WorkLocation.ONSITE

        # 8. Crear oferta
        return self._create_job_offer(
            title=title,
            company=company,
            url=job_url,
            description=description,
            location=location,
            work_location_type=work_location,
            **salary_info
        )

    except Exception as e:
        logger.warning(f"Error parseando elemento: {str(e)}")
        return None
```

### 4. Registrar el Scraper

Edita `src/scrapers/scraper_factory.py`:

```python
from .miplataforma_scraper import MiPlataformaScraper

class ScraperFactory:
    _SCRAPERS: Dict[str, Type[BaseScraper]] = {
        'indeed': IndeedScraper,
        'infojobs': InfojobsScraper,
        'miplataforma': MiPlataformaScraper,  # ← Añadir aquí
    }
```

### 5. Configurar en config.yaml

```yaml
platforms:
  miplataforma:
    enabled: true
    requires_api: false
    priority: 20
```

### 6. Probar el Scraper

```bash
# Probar solo tu scraper
python -m src.main --platforms miplataforma --keywords "data scientist"
```

## Casos Especiales

### Sitios con JavaScript Dinámico (Selenium)

Si el sitio requiere JavaScript para cargar contenido:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class SeleniumScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        options = webdriver.ChromeOptions()
        if self.config.get('scraping.headless_mode', True):
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def scrape_jobs(self, keywords, location):
        try:
            # Navegar a la página
            self.driver.get(url)

            # Esperar que los elementos se carguen
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.CLASS_NAME, 'job-card')
            )

            # Obtener HTML renderizado
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Continuar con parsing normal...

        finally:
            self.driver.quit()
```

### Sitios con Paginación Dinámica (Scroll Infinito)

```python
def _scroll_to_load_all(self):
    """Hace scroll para cargar más ofertas."""
    last_height = self.driver.execute_script(
        "return document.body.scrollHeight"
    )

    while True:
        # Scroll hasta el final
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        # Esperar a que cargue
        time.sleep(2)

        # Calcular nueva altura
        new_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )

        if new_height == last_height:
            break

        last_height = new_height
```

### Sitios con Protección Cloudflare

```python
import cloudscraper

class CloudflareScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.scraper = cloudscraper.create_scraper()

    def _make_request(self, url):
        """Hace request evitando Cloudflare."""
        response = self.scraper.get(
            url,
            headers=ScrapingUtils.get_headers(),
            timeout=self.timeout
        )
        return response
```

### APIs Oficiales

Si la plataforma tiene API oficial, úsala en vez de scraping:

```python
class APIScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get_env_var('PLATAFORMA_API_KEY')
        self.api_url = "https://api.plataforma.com/v1"

    def scrape_jobs(self, keywords, location):
        jobs = []

        for keyword in keywords:
            # Hacer request a la API
            response = requests.get(
                f"{self.api_url}/jobs/search",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                params={
                    'q': keyword,
                    'location': location,
                    'limit': 100
                }
            )

            data = response.json()

            # Parsear respuesta
            for job_data in data['results']:
                job = self._parse_api_job(job_data)
                jobs.append(job)

        return jobs

    def _parse_api_job(self, data: dict) -> JobOffer:
        """Parsea un trabajo desde respuesta de API."""
        return self._create_job_offer(
            title=data['title'],
            company=data['company']['name'],
            url=data['url'],
            description=data.get('description', ''),
            location=data.get('location', ''),
            salary_min=data.get('salary', {}).get('min'),
            salary_max=data.get('salary', {}).get('max'),
        )
```

## Mejores Prácticas

1. **Respeta Rate Limits**: Usa `self._sleep()` entre requests
2. **Manejo de Errores**: Siempre usa try/except
3. **Logging**: Usa `logger.info()` para progreso y `logger.error()` para errores
4. **Validación**: Verifica que los campos requeridos (título, empresa, URL) existan
5. **Testing**: Prueba con diferentes keywords y ubicaciones
6. **Documentación**: Añade docstrings explicando la lógica

## Debugging

```bash
# Ver logs detallados
LOG_LEVEL=DEBUG python -m src.main --platforms miplataforma

# Guardar HTML para inspección
with open('debug.html', 'w') as f:
    f.write(response.text)

# Imprimir selectores encontrados
print(soup.find_all('div', class_='job-card'))
```

## Recursos Útiles

- **Inspección de Selectores**: Chrome DevTools (F12)
- **Testing de Expresiones Regulares**: https://regex101.com/
- **Documentación Beautiful Soup**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Documentación Selenium**: https://selenium-python.readthedocs.io/

## Contribuir

Una vez que hayas implementado un scraper funcional:

1. Asegúrate de que funcione correctamente
2. Añade tests si es posible
3. Documenta cualquier particularidad
4. Crea un Pull Request

---

**Nota Legal**: Siempre verifica los Términos de Servicio del sitio web antes de implementar scraping. Muchos sitios prohíben esta práctica. Usar APIs oficiales es siempre preferible y legal.
