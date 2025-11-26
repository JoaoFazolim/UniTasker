from models import *
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

def cadastrarUsuario(dados):

    username = dados.get('username')
    nome = dados.get('nome')
    email = dados.get('email') 
    senha = dados.get('senha') 

    
    if not username or not email or not senha:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Preencha todos os campos obrigatórios!'}

   
    usuario_existente = Usuario.query.filter(
        (Usuario.username == username) | (Usuario.email == email)
    ).first()

    if usuario_existente:
        return {'status': 'CONFLITO', 'mensagem': 'Nome de usuário ou E-mail já cadastrados.'}

    try:
        
        hashSenha = generate_password_hash(senha).decode('utf-8')

        
        novoUsuario = Usuario(
            username=username,
            nome=nome,
            email=email,
            hashSenha=hashSenha, 
        )

        
        db.session.add(novoUsuario)
        db.session.commit()

        
        return {
            'status': 'SUCESSO', 
            'mensagem': 'Cadastro realizado com sucesso!',
            'data': {
                'id': novoUsuario.id,
                'username': novoUsuario.username,
                'email': novoUsuario.email
            }
        }

    except Exception as e:
        db.session.rollback() 
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro interno: {str(e)}'}
    

def fazerLogin(dados):
    
    login = dados.get('login')
    senha = dados.get('senha')

    #Validação básica dos dados do form
    if not login or not senha:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Preencha usuário e senha.'}

    #Busca por email ou username para depois checar a senha
    usuario = Usuario.query.filter(
        (Usuario.username == login) | (Usuario.username == login)
    ).first()

    # Verificando se o usuário e senha batem
    if usuario and check_password_hash(usuario.hashSenha, senha):
        
        #Verifica se a conta foi desativada antes de fazer login
        if not usuario.estaAtivo:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Esta conta foi desativada.'}

        #Retorna o objeto para a biblioteca flask-login salvar a sessão
        return {'status': 'SUCESSO', 'data': usuario} 
    
    else:
        #Usuário ou senha incorretos
        return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Usuário ou senha inválidos.'}
    

def inativarUsuario(dados):
    id_usuario = dados.get('id')
    
    if not id_usuario:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'ID do usuário é obrigatório.'}

    try:
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário não encontrado.'}
        
        if not usuario.estaAtivo:
            return {'status': 'CONFLITO', 'mensagem': 'Esta conta já está inativa.'}

        #Soft delete aqui
        usuario.deletadoEm = datetime.utcnow()
        
        db.session.commit()
        
        return {'status': 'SUCESSO', 'mensagem': 'Conta inativada com sucesso.'}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao inativar: {str(e)}'}


def reativarUsuario(dados):
    id_usuario = dados.get('id')

    if not id_usuario:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'ID do usuário é obrigatório.'}

    try:
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário não encontrado.'}
        
        if usuario.estaAtivo:
            return {'status': 'CONFLITO', 'mensagem': 'Esta conta já está ativa.'}

        #Restaura
        usuario.deletadoEm = None
        
        db.session.commit()
        
        return {'status': 'SUCESSO', 'mensagem': 'Conta reativada com sucesso!'}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao reativar: {str(e)}'}