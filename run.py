import os
import subprocess
import sys

# Active le venv (optionnel si déjà activé)
# os.system(".venv\\Scripts\\activate")  # Windows

# Lance le serveur
subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"])
