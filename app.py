from flask import Flask, request, jsonify, flash, redirect
from flask_login import LoginManager, current_user
from config import Config
import os
from controllers import usuario_bp, home_bp, dashboard_bp, servico_bp, solicitacao_bp, avaliacao_bp, chat_bp
from extensions import db, login_manager, migrate, socketio

#Instanciando o app e definindo pasta de templates
app = Flask(__name__, template_folder=os.path.join('templates'))
#Aplicando as configurações do config.py
app.config.from_object(Config)



login_manager.init_app(app)

migrate.init_app(app, db)

socketio.init_app(app)

#importando tudo no models e incluindo o db no app
from models import *
db.init_app(app)



#Função para carregar o usuário da sessão
@login_manager.user_loader
def load_user(userId):
    return Usuario.query.get(int(userId))


#Injeta variáveis no contexto de renderização dos templates
#Tudo que estiver dentro do dicionário será acessivel no template
#É chamado toda vez que um template é renderizado
@app.context_processor
def inject_user():
    return { 'usuarioAtual' : current_user } 



#Tratamento de erros de arquivo acima do limite
@app.errorhandler(413)
def request_entity_too_large(error):
    #Verifica se a requisição foi feita pelo postman
    if request.is_json or request.accept_mimetypes.accept_json:
        return jsonify({
            'status': 'ERRO', 
            'mensagem': 'O arquivo enviado é muito grande. O limite máximo é 4MB.'
        }), 413
    
    #Caso vier do navegador da um flash na mensagem
    flash('O arquivo enviado é muito grande. O limite máximo é 4MB.', 'erro')
    
    #E redireciona para a página que ele estava
    return redirect(request.url)


#Aplicando os bps de rotas dos controllers
app.register_blueprint(home_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(servico_bp)
app.register_blueprint(solicitacao_bp)
app.register_blueprint(avaliacao_bp)
app.register_blueprint(chat_bp)





#Inicia a aplicação flask caso o arquivo esteja sendo executado diretamente
if __name__  == '__main__':
    app.run(debug=True,host='0.0.0.0')