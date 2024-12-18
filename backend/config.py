# backend/config.py
from pathlib import Path

import os
# Get the project root directory (where ontology folder is)
PROJECT_ROOT = Path(__file__).parent.parent

# Database configuration
DATABASE_URL = f"sqlite:///{PROJECT_ROOT}/backend/student_progress.db"

# Path to the ontology file
ONTOLOGY_PATH = PROJECT_ROOT / "ontology" / "energy-storage.owx"

# Quiz settings
PASS_THRESHOLD = 0.8  # 70% correct answers needed to pass
MAX_QUIZ_ATTEMPTS = 99  # Maximum number of attempts per topic


# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY" , "0000000000")

# QA Database settings
QA_DATABASE_PATH = str(PROJECT_ROOT / "backend" / "qa_shots.db")