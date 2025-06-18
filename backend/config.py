import os
from dotenv import load_dotenv
load_dotenv()

SI_OUTPUT_VALIDATORS_ACCESS_KEY = os.getenv("SI_OUTPUT_VALIDATORS_ACCESS_KEY")
SI_OUTPUT_VALIDATORS_SECRET_KEY = os.getenv("SI_OUTPUT_VALIDATORS_SECRET_KEY")
FUNNEL_URL = os.getenv("FUNNEL_URL")
MONGO_URI = os.getenv("MONGO_URI")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8081))