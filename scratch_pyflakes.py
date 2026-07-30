import subprocess
import os

try:
    output = subprocess.check_output(
        ["python", "-m", "pyflakes", "backend/app"], 
        stderr=subprocess.STDOUT, 
        text=True, 
        cwd="d:/projects/major project/Agilegraph"
    )
    print(output)
except subprocess.CalledProcessError as e:
    print(e.output)
