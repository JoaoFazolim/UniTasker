from dotenv import load_dotenv
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:admin@localhost:5432/unitasker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    load_dotenv()
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("Chave secreta faltando! Verifique o .env")

