import os
from dotenv import load_dotenv

config = load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
