from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("URI do banco faltando! Verifique o .env")

    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("Chave secreta faltando! Verifique o .env")
    
    #Caminho base do projeto
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    #Pasta onde as imagens de perfil serão salvas
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'uploads')
    
    #Tamanho máximo do arquivo em bytes (ex: 4MB)
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024 
    
    #Extensões permitidas
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

