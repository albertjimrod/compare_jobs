# Arquitectura del Sistema

## Visión General

Compare Jobs está diseñado con una arquitectura modular que separa claramente las responsabilidades:

## Componentes Principales

### 1. Capa de Modelos (`src/models/`)
Define las estructuras de datos principales:
- **Job**: Representa una oferta de trabajo con todos sus atributos
- **Comparison**: Representa una comparación entre múltiples ofertas

### 2. Capa de Servicios (`src/services/`)
Contiene la lógica de negocio:
- **JobService**: Gestión de ofertas de trabajo (CRUD)
- **ComparisonService**: Lógica de comparación y puntuación

### 3. Capa de Utilidades (`src/utils/`)
Funciones auxiliares compartidas:
- Validadores de datos
- Formateadores de salida
- Helpers generales

## Flujo de Datos

```
Input (JSON/YAML) → JobService → Models → ComparisonService → Output (Report)
```

## Principios de Diseño

- **Separación de Responsabilidades**: Cada módulo tiene una responsabilidad clara
- **Modularidad**: Componentes independientes y reutilizables
- **Testabilidad**: Código diseñado para ser fácilmente testeable
- **Extensibilidad**: Fácil agregar nuevos criterios y funcionalidades
