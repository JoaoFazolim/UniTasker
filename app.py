from flask import Flask
from flask_login import LoginManager, current_user
from config import Config
import os
from routes import usuario_bp, home_bp

#Instanciando o app e definindo pasta de templates
app = Flask(__name__, template_folder=os.path.join('templates'))
#Aplicando as configurações do config.py
app.config.from_object(Config)


loginManager = LoginManager()
loginManager.init_app(app)

#importando tudo no models e incluindo o db no app
from models import *
db.init_app(app)

with app.app_context():
    db.create_all()


#Função para carregar o usuário da sessão
@loginManager.user_loader
def load_user(userId):
    return Usuario.query.get(int(userId))


#Injeta variáveis no contexto de renderização dos templates
#Tudo que estiver dentro do dicionário será acessivel no template
#É chamado toda vez que um template é renderizado
@app.context_processor
def inject_user():
    return { 'usuarioAtual' : current_user } 


#Aplicando os bps de rotas dos controllers
app.register_blueprint(home_bp)
app.register_blueprint(usuario_bp)



#Inicia a aplicação flask caso o arquivo esteja sendo executado diretamente
if __name__  == '__main__':
    app.run(debug=True)