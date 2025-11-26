from flask import Blueprint, render_template, request, redirect,url_for
from utils import handleResponse
from flask_login import login_user, logout_user, login_required, current_user
from controllers import *


usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/cadastro', methods = ['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            dadosUsuario = {
                                'username': request.form.get('username'),
                                'nome': request.form.get('nome'),
                                'email': request.form.get('email'),
                                'senha': request.form.get('senha'),
                            }
            resposta = cadastrarUsuario(dadosUsuario)
         
            return handleResponse(resposta, 'cadastro')
        except Exception as e:
            return handleResponse({'status': 'ERRO_GENERICO', 'mensagem': str(e)}, 'cadastro')
    else:
        return render_template('cadastro.html', mensagem="Cadastra ai 🔫💀🤬")


@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    #Verifica se ja esta logado e retorna pra home
    if current_user.is_authenticated:
        return redirect(url_for('home.home')) 

    if request.method == 'POST':
        #Extrai os dados do form
        dados = request.form

        dadosLogin = {
            'login': dados.get('login'),
            'senha': dados.get('senha')
        }
        
        #Chama o controlador de login
        resposta = fazerLogin(dadosLogin)

        if resposta['status'] == 'SUCESSO':
            usuario = resposta['data']
            
            #Cria a sessão passando o objeto do usuário como argumento
            login_user(usuario)

            resposta['data'] = usuario.to_dict() 
            
            querJson = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'
            
            if querJson:
                #Retorna a resposta corretamente caso seja feita a requisição pelo postman
                return handleResponse(resposta, 'login')
            else:
                #Se for no navegador mesmo faz um redirect
                return redirect(url_for('home.home'))
            
        
        else:
            #Se der algum erro retorna para o login
            return handleResponse(resposta, 'login')

    #Formulário caso seja um get
    return render_template('login.html')


@usuario_bp.route('/logout')
@login_required #Só pode acessar se estiver logado
def logout():
    logout_user() #Remove a sessão
    return redirect(url_for('usuario.login'))