from flask import Blueprint, render_template, request, redirect,url_for, flash
from utils import handleResponse
from flask_login import login_user, logout_user, login_required, current_user
from services import *


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
         
            return handleResponse(resposta, 'login')
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

@usuario_bp.route('/usuario/<username>', methods=['GET'])
def perfil_publico(username):

    resposta = obterUsuario(username)
    
    return handleResponse(resposta, 'perfil')

@usuario_bp.route('/perfil/foto', methods=['POST'])
@login_required
def upload_foto():
    # Verifica se o cliente quer receber JSON (provavelmente o postman)
    wants_json = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'
    if 'foto_perfil' not in request.files:
        if wants_json:
             return handleResponse({'status': 'ERRO', 'mensagem': 'Nenhum arquivo enviado.'}, 'perfil')
        
        flash('Nenhum arquivo selecionado.', 'erro')
        return redirect(url_for('usuario.perfil_publico', username=current_user.username))
    
    arquivo = request.files['foto_perfil']
    resposta = atualizarImagemPerfil(current_user.id, arquivo)
    
    if wants_json:
        return handleResponse(resposta, 'perfil')

    if resposta['status'] == 'SUCESSO':
        flash('Foto de perfil atualizada com sucesso!', 'sucesso')
    else:
        flash(resposta.get('mensagem', 'Erro ao atualizar foto.'), 'erro')
    
    return redirect(url_for('usuario.perfil_publico', username=current_user.username))


@usuario_bp.route('/logout')
@login_required 
def logout():
    logout_user() #Remove a sessão
    return redirect(url_for('usuario.login'))

@usuario_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    
 
    if request.method == 'POST':
        #Coleta dados de texto (inclui ids para remover e capa)
        dados_form = request.form.to_dict()

        print(dados_form)
        
        #Coleta arquivos separadamente
        arquivo_perfil = request.files.get('foto_perfil')
        lista_portfolio = request.files.getlist('foto_portfolio')
        
        #Chama o Service que processa tudo (Texto, Avatar e Portfólio)
        resposta = atualizarPerfil(current_user.id, dados_form, arquivo_perfil, lista_portfolio)
        
        if resposta['status'] == 'SUCESSO':
            flash('Perfil atualizado com sucesso!', 'sucesso')
            return redirect(url_for('usuario.perfil_publico', username=current_user.username))
        else:
            flash(resposta.get('mensagem'), 'erro')
            #Se der erro, recarrega a página de edição
            return redirect(url_for('usuario.editar_perfil')) 

    dados_usuario = current_user.to_dict()
    return render_template('perfil.html', dados=dados_usuario, modo="editar_perfil")