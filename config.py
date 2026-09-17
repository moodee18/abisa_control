import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables del archivo .env si existe
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(BASE_DIR / ".env.example")

# Configuración del Portal
SIIA_URL = os.getenv("SIIA_URL", "https://siia.abisalud.com/main.php")
SIIA_USERNAME = os.getenv("SIIA_USERNAME", "")
SIIA_PASSWORD = os.getenv("SIIA_PASSWORD", "")

# Configuración de Playwright
HEADLESS = os.getenv("HEADLESS", "False").lower() in ("true", "1", "yes")
SLOW_MO = int(os.getenv("SLOW_MO", "300"))

# Base de Datos
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'abisalud.db'}")

# Carpetas de trabajo
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
PROCESSED_DIR = BASE_DIR / os.getenv("PROCESSED_DIR", "downloads/processed")
DATA_DIR = BASE_DIR / "data"

# Asegurar directorios
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configuración Servidor Web UI
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

