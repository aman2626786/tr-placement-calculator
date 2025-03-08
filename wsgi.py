import sys
import os

# Add your project directory to the sys.path
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/T_R_placement_calculate'
if path not in sys.path:
    sys.path.append(path)

# Set the environment variable
os.environ['FLASK_ENV'] = 'production'

# Import your Flask app
from app import app as application 