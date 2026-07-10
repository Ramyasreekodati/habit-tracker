import os

# Application Settings
APP_NAME = "GrowthOS"
DEFAULT_THEME = "light"

# Database Configuration
# Default to sqlite:///growthos.db in the root directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'growthos.db')}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Ensure sqlite URL has check_same_thread=False for Streamlit
DB_CONNECT_ARGS = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
