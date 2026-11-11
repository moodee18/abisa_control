# Automatización, Inventario y Pipeline ETL - SIIA Abisalud

Sistema integral en Python para:
1. **Control y Gestión de Inventario (CRUD Web & CLI):** Consulta el catálogo de claves disponibles, existencias consolidadas, semáforo de lotes, matriz CLUES, control por movimientos y gestión de usuarios/permisos.
2. **Automatización Robótica de Inventarios (SIIA RPA):** Módulo desatendido para generar Altas de Inventario (`opc=78`) con descarga de PDFs oficiales y Seguimiento Masivo (`opc=82`) desde Excel de conteo físico con paginación autónoma, guardado y evidencias fotográficas pre-cierre.
3. **Descarga asistida/automática (RPA):** Iniciar sesión con credenciales en el portal SIIA Abisalud (`https://siia.abisalud.com/main.php`) y descargar reportes automáticamente.
4. **Procesamiento de Archivos (ETL):** Ingesta, estandarización y limpieza de archivos en formatos **CSV, Excel (.xlsx, .xls), PDF y JSON**.
5. **Persistencia en Base de Datos:** Almacenamiento estructurado en base de datos SQLite local (`data/abisalud.db`) con trazabilidad y auditoría.

---

## 📁 Estructura del Proyecto

```text
abisalud_automation/
├── .env.example              # Plantilla de configuración
├── .env                      # Tus credenciales locales
├── requirements.txt          # Dependencias de Python
├── config.py                 # Módulo de configuración y rutas
├── database.py               # Gestión de base de datos, esquemas SQLAlchemy, roles y CRUD
├── processor.py              # Procesador de archivos CSV, Excel, PDF y JSON
├── downloader.py             # Automatización de descargas con Playwright
├── siia_inventario_rpa.py    # Motor RPA para Altas Masivas y Seguimiento de Inventario
├── app.py                    # Servidor Web FastAPI con API REST
├── main.py                   # Orquestador del flujo y CLI
├── instalar_dependencias.bat # Instalador de 1-clic para equipos nuevos
├── iniciar_panel.bat         # Lanzador de 1-clic para abrir el panel web
├── templates/
│   ├── index.html            # Dashboard Web moderno e interactivo (SPA)
│   └── login.html            # Pantalla de inicio de sesión con roles y permisos
├── data/
│   ├── abisalud.db           # Base de datos SQLite del sistema
│   └── plantillas/           # Plantillas oficiales en Excel para RPA
│       ├── Plantilla_Alta_Almacenes.xlsx
│       └── Plantilla_Seguimiento_Inventario.xlsx
└── downloads/                # Carpeta de trabajo para reportes y evidencias en ZIP
```

---

## 💻 Instalación en Otra Computadora (Paso a Paso)

### 1. Clonar el repositorio
```bash
git clone https://github.com/moodee18/abisa_control.git
cd abisa_control
```

### 2. Instalar dependencias (Método Rápido)
Haz doble clic en:
```text
instalar_dependencias.bat
```
*O si prefieres hacerlo por consola:*
```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\playwright install chromium
```

### 3. Iniciar el Sistema
Haz doble clic en:
```text
iniciar_panel.bat
```
*O por consola:*
```bash
python main.py --web
```
Se abrirá automáticamente el navegador en `http://localhost:8000`.

---

## 🤖 Módulo "Automatización SIIA" (Nuevo)

Accede desde el botón **Automatización SIIA** en la barra superior:

1. **Sub-pestaña 1: Alta de Inventario Masiva (`opc=78`)**
   - Sube un Excel con la lista de almacenes (puedes descargar la plantilla con el botón correspondiente).
   - Selecciona la localidad (**CS ALMACEN 2022**).
   - Genera automáticamente los cortes de inventario y descarga todos los PDFs oficiales en un archivo `.zip` comprimido.

2. **Sub-pestaña 2: Seguimiento de Inventario Masivo (`opc=82`)**
   - Sube el Excel detallado con las 7 columnas de conteo físico (Código de Barras, Clave Cliente, Descripción, Lote, Almacén, Cantidad, Caducidad).
   - El robot recorre hoja por hoja automáticamente, llena las cantidades, da clic en Guardar y avanza por todas las páginas del almacén.
   - Marca la casilla **Finalizado**, toma la **captura de pantalla de evidencia fotográfica pre-cierre** y consolida el ajuste.
   - Descarga todas las fotos de comprobación en un archivo `.zip` listo para auditoría.

---

## 🛠️ Comandos por Consola (CLI)

| Objetivo | Comando |
| :--- | :--- |
| **Abrir Panel Web Interactivo** | `python main.py --web` |
| **Ver Catálogo y Stock en Consola** | `python main.py --inventory` |
| **Agregar Insumo por Consola** | `python main.py --add` |
| **Descarga asistida en SIIA (RPA)** | `python main.py --download` |
| **Procesar archivos en `downloads/` a la BD** | `python main.py --process` |
| **Flujo completo (Descargar + Procesar)** | `python main.py --all` |
| **Ver estadísticas y auditoría** | `python main.py --summary` |
| **Exportar la BD a Excel maestro** | `python main.py --export` |
