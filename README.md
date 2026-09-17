# Automatización, Inventario y Pipeline ETL - SIIA Abisalud

Sistema integral en Python para:
1. **Control y Gestión de Inventario (CRUD Web & CLI):** Consulta el catálogo de claves disponibles, existencias consolidadas, semáforo de lotes, y agrega, edita o elimina registros fácilmente.
2. **Descarga asistida/automática (RPA):** Iniciar sesión con credenciales en el portal SIIA Abisalud (`https://siia.abisalud.com/main.php`) y descargar reportes automáticamente.
3. **Procesamiento de Archivos (ETL):** Ingesta, estandarización y limpieza de archivos en formatos **CSV, Excel (.xlsx, .xls), PDF y JSON**.
4. **Persistencia en Base de Datos:** Almacenamiento estructurado en base de datos SQLite local (o PostgreSQL/MySQL) con trazabilidad y auditoría.

---

## 📁 Estructura de Archivos

```text
abisalud_automation/
├── .env.example              # Plantilla de configuración
├── .env                      # Tus credenciales reales
├── requirements.txt          # Dependencias de Python
├── config.py                 # Módulo de configuración y rutas
├── database.py               # Gestión de base de datos, esquemas SQLAlchemy y CRUD
├── processor.py              # Procesador de archivos CSV, Excel, PDF y JSON
├── downloader.py             # Automatización de navegador con Playwright
├── app.py                    # Servidor Web FastAPI con API REST
├── main.py                   # Orquestador del flujo y CLI
├── iniciar_panel.bat         # Acceso directo de 1-clic para abrir el panel web
├── templates/
│   └── index.html            # Dashboard Web moderno e interactivo (SPA)
├── downloads/                # Carpeta donde se depositan los archivos a procesar
│   └── processed/            # Histórico de archivos ya procesados
└── data/                     # Base de datos SQLite (abisalud.db)
```

---

## 🚀 Inicio Rápido

### Opción A: Abrir el Panel Web Interactivo (Recomendado)
Haz doble clic en `iniciar_panel.bat` o ejecuta:
```bash
python main.py --web
```
Se abrirá automáticamente tu navegador en `http://127.0.0.1:8000` con:
- 📊 **Tarjetas de KPIs:** Claves únicas, total de piezas en stock, valor monetario acumulado y lotes.
- 📋 **Catálogo Consolidado de Claves:** Visualiza el stock acumulado por cada clave única.
- 📦 **Inventario Detallado por Lotes:** Tabla con buscador en tiempo real, filtros y acciones de **Edición** y **Eliminación**.
- ➕ **Formulario de Altas:** Botón para agregar nuevas claves e insumos con autocalculado de importes.
- 📥 **Exportación a Excel:** Botón para descargar el reporte maestro consolidado en 1 clic.
- 📂 **Carga Drag & Drop:** Arrastra archivos Excel/PDF/CSV directamente a la web para procesarlos.

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
