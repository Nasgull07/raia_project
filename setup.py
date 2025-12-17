import subprocess
import os
import sys

# Ruta base del entorno virtual
venv_path = os.path.join('.venv', 'Scripts')

# Verifica si el entorno virtual existe
if not os.path.exists(venv_path):
    raise FileNotFoundError("El entorno virtual no existe. Por favor, crea el entorno virtual en '.venv'." 
                            "Intenta ejecutar setup.py despues de crear el entorno virtual ejecutando el siguiente comando en la terminal:"
                            "python -m venv .venv")
# Rutas a los ejecutables dentro del entorno virtual
pip_executable = os.path.join(venv_path, 'pip.exe')
python_executable = os.path.join(venv_path, 'python.exe')

# Instala dependencias en FastAPI
subprocess.run([pip_executable, 'install', '-r', 'FastAPI/requirements.txt'], shell=True)

# Instala dependencias en UI
subprocess.run([pip_executable, 'install', '-r', 'UI/requirements.txt'], shell=True)

# Ejecuta la aplicación Streamlit
subprocess.run([python_executable, '-m', 'streamlit', 'run', 'UI/app.py'], shell=True)