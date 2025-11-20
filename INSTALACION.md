# 🚀 Instrucciones de Instalación

## ⚠️ IMPORTANTE: Acceder al Código

El código completo del Job Scraper está en la rama de desarrollo:
**`claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6`**

### Opción 1: Clonar la Rama Directamente (Recomendado)

```bash
# Clonar solo la rama con el código
git clone -b claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6 \
  https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs
```

### Opción 2: Clonar y Cambiar de Rama

```bash
# Clonar el repositorio
git clone https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs

# Cambiar a la rama con el código
git checkout claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6
```

### Opción 3: Hacer Merge a tu Rama Principal (Para Propietarios del Repo)

Si eres el propietario del repositorio y quieres hacer merge a main/master:

```bash
# Clonar el repositorio
git clone https://github.com/albertjimrod/compare_jobs.git
cd compare_jobs

# Crear rama main si no existe
git checkout -b main

# Hacer merge de la rama de desarrollo
git merge claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6

# Pushear a main
git push -u origin main
```

## ✅ Verificar que Tienes el Código Completo

Después de clonar, deberías ver esta estructura:

```bash
tree -L 2
```

Resultado esperado:
```
.
├── config
│   └── config.yaml           ← Debe estar presente
├── data
│   ├── README.md
│   ├── processed/
│   ├── raw/
│   ├── reports/
│   └── visualizations/
├── docs
│   ├── architecture.md
│   └── extending_scrapers.md
├── scripts
│   ├── quick_start.py        ← Debe estar presente
│   ├── setup.sh
│   └── verify_installation.py
├── src
│   ├── __init__.py
│   ├── main.py               ← Debe estar presente
│   ├── models/
│   ├── scrapers/             ← Debe tener varios archivos
│   ├── services/             ← Debe tener varios archivos
│   └── utils/
├── tests
├── .env.example              ← Debe estar presente
├── environment.yml           ← Debe estar presente
├── requirements.txt          ← Debe estar presente
├── QUICKSTART.md
└── README.md

Total archivos Python: ~18
Total archivos en proyecto: ~37
```

### Verificar Instalación

```bash
# Ejecutar script de verificación
python scripts/verify_installation.py
```

Deberías ver:
```
✅ Todos los archivos presentes (13/13)
✅ Todos los directorios presentes (14/14)
```

## 🔧 Si Solo Ves Archivos Vacíos

Si después de clonar solo ves archivos como:
```
.
├── docs
├── src
│   └── __init__.py
└── tests
```

**Significa que no estás en la rama correcta.** Ejecuta:

```bash
# Ver en qué rama estás
git branch

# Listar ramas disponibles
git branch -a

# Cambiar a la rama con el código
git checkout claude/job-scraper-data-science-01AoTTB6fVS9wcV3WMuFkxa6

# Verificar que ahora tienes el código
ls -la src/
```

## 📦 Después de Tener el Código

Sigue las instrucciones de [QUICKSTART.md](QUICKSTART.md):

1. **Verificar instalación:**
   ```bash
   python scripts/verify_installation.py
   ```

2. **Instalar dependencias:**
   ```bash
   # Con Conda (recomendado)
   conda env create -f environment.yml
   conda activate job-scraper-env

   # O con pip
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Ejecutar:**
   ```bash
   python scripts/quick_start.py
   ```

## 🆘 Problemas Comunes

### "No such file 'requirements.txt'"
→ No estás en la rama correcta. Ver sección "Si Solo Ves Archivos Vacíos" arriba.

### "No module named 'src'"
→ No estás en la rama correcta o no has instalado dependencias.

### "fatal: A branch named 'main' already exists"
→ Ya tienes una rama main. Usa `git checkout main` y luego haz merge.

---

**Nota para el propietario del repositorio:**

Esta estructura de ramas es resultado del sistema de desarrollo con Claude. Para facilitar el acceso a futuros usuarios, se recomienda hacer merge de la rama de desarrollo a `main` o `master` y establecerla como rama por defecto en GitHub:

1. GitHub → Settings → Branches → Default branch
2. Cambiar a `main` o la rama que desees como principal

De esta forma, al clonar el repositorio, los usuarios obtendrán automáticamente todo el código.
