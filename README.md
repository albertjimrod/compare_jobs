# Compare Jobs

Herramienta para comparar ofertas de trabajo y facilitar la toma de decisiones en procesos de selección laboral.

## 📋 Descripción

Este proyecto proporciona una plataforma para comparar múltiples ofertas de trabajo basándose en diferentes criterios como salario, beneficios, ubicación, cultura empresarial, oportunidades de crecimiento, y más.

## 🏗️ Estructura del Repositorio

```
compare_jobs/
├── README.md                 # Documentación principal del proyecto
├── .gitignore               # Archivos y directorios a ignorar por Git
├── LICENSE                  # Licencia del proyecto
│
├── src/                     # Código fuente principal
│   ├── __init__.py
│   ├── main.py             # Punto de entrada de la aplicación
│   ├── models/             # Modelos de datos
│   │   ├── __init__.py
│   │   ├── job.py         # Modelo de oferta de trabajo
│   │   └── comparison.py  # Modelo de comparación
│   ├── services/           # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── job_service.py
│   │   └── comparison_service.py
│   └── utils/              # Utilidades y helpers
│       ├── __init__.py
│       ├── validators.py
│       └── formatters.py
│
├── tests/                   # Tests unitarios y de integración
│   ├── __init__.py
│   ├── test_models/
│   ├── test_services/
│   └── test_utils/
│
├── data/                    # Datos de ejemplo y plantillas
│   ├── examples/           # Ejemplos de ofertas de trabajo
│   └── templates/          # Plantillas para comparaciones
│
├── docs/                    # Documentación adicional
│   ├── architecture.md     # Arquitectura del sistema
│   ├── user_guide.md       # Guía de usuario
│   └── api.md             # Documentación de API (si aplica)
│
├── scripts/                 # Scripts de utilidad
│   ├── setup.sh           # Script de configuración inicial
│   └── run_tests.sh       # Script para ejecutar tests
│
└── config/                  # Archivos de configuración
    ├── config.yaml         # Configuración general
    └── criteria.yaml       # Criterios de comparación predefinidos
```

## 🎯 Características Principales

- **Comparación Multi-criterio**: Evalúa ofertas basándose en múltiples factores configurables
- **Sistema de Puntuación**: Asigna pesos a diferentes criterios según tus prioridades
- **Visualización de Resultados**: Presenta comparaciones de forma clara y comprensible
- **Almacenamiento de Datos**: Guarda tus ofertas para futuras referencias
- **Exportación**: Genera reportes en diferentes formatos

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/albertjimrod/compare_jobs.git

# Navegar al directorio
cd compare_jobs

# Instalar dependencias (ejemplo para Python)
pip install -r requirements.txt

# Configurar el entorno
cp config/config.example.yaml config/config.yaml
```

## 📖 Uso

```bash
# Ejemplo básico de uso
python src/main.py --compare job1.json job2.json job3.json

# Con criterios personalizados
python src/main.py --compare jobs/*.json --criteria config/my_criteria.yaml
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
./scripts/run_tests.sh

# O usando pytest directamente
pytest tests/
```

## 📂 Directorio Detallado

### `/src` - Código Fuente
Contiene toda la lógica principal de la aplicación:
- **models/**: Definiciones de las estructuras de datos
- **services/**: Lógica de negocio y procesamiento
- **utils/**: Funciones auxiliares y utilidades compartidas

### `/tests` - Pruebas
Suite completa de tests para garantizar la calidad del código:
- Tests unitarios para cada módulo
- Tests de integración para flujos completos
- Fixtures y mocks para testing

### `/data` - Datos
- **examples/**: Ejemplos de ofertas de trabajo para testing y demostración
- **templates/**: Plantillas reutilizables para crear nuevas comparaciones

### `/docs` - Documentación
Documentación técnica y de usuario:
- Guías de arquitectura
- Manuales de usuario
- Documentación de API

### `/scripts` - Scripts de Automatización
Scripts de utilidad para desarrollo y deployment:
- Scripts de setup y configuración
- Scripts de testing y validación
- Scripts de deployment

### `/config` - Configuración
Archivos de configuración del proyecto:
- Configuración general de la aplicación
- Definición de criterios de comparación
- Variables de entorno

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 👥 Autores

- Alberto Jim Rod - [@albertjimrod](https://github.com/albertjimrod)

## 🔄 Estado del Proyecto

Este proyecto está en desarrollo activo. La estructura documentada representa la organización propuesta para el código.
