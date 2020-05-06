import os

from dotenv import load_dotenv


project_folder = os.path.expanduser('~/temperature-difference')
load_dotenv(os.path.join(project_folder, '.env'))

from app import app