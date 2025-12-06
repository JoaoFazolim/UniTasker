from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

#Aqui vão ficar todas as dependências que precisam ser usadas no resto da aplicação

#Banco de dados
db = SQLAlchemy()

#Socketio para chats
socketio = SocketIO()

#Gerenciador de login do flask
login_manager = LoginManager()

migrate = Migrate()