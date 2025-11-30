from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


#Aqui vão ficar todas as dependências que precisam ser usadas no resto da aplicação

#Banco de dados
db = SQLAlchemy()

#Gerenciador de login do flask
login_manager = LoginManager()