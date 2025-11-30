from models import *
from extensions import db
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
import os
import uuid
from utils import validarArquivo, salvarArquivo
from flask import current_app


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
    
def obterUsuario(username):
    try:

        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário não encontrado.'}
        
        #Verifica se o usuário está ativo
        if not usuario.estaAtivo:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Este usuário não está mais ativo.'}

        #Retorna os dados convertidos para dicionário
        return {'status': 'SUCESSO', 'data': usuario.to_dict()}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}
    
def atualizarImagemPerfil(id_usuario, arquivo):

    #Recebe o id de usuário e arquivo
    if not arquivo or arquivo.filename == '':
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Nenhum arquivo enviado.'}

    #Validação usando o helper
    if not validarArquivo(arquivo.filename):
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Tipo de arquivo não permitido (use PNG, JPG, GIF).'}

    try:
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário não encontrado.'}

        #Checa a extensão do arquivo e ve se é permitido
        extensao = arquivo.filename.rsplit('.', 1)[1].lower()
        #Gerar um nome
        novo_nome = f"user_{id_usuario}_{uuid.uuid4().hex[:8]}.{extensao}"
        
        #Verifica se o usuário ja possui uma imagem de perfil
        caminho_pasta = current_app.config['UPLOAD_FOLDER']
        imagem_antiga = usuario.imagem
        
        #Se ele tiver apagamos do servidor para economizar espaço
        if imagem_antiga:
            nome_arquivo_antigo = os.path.basename(imagem_antiga)
            caminho_antigo = os.path.join(caminho_pasta, nome_arquivo_antigo)
            
            if os.path.exists(caminho_antigo):
                try:
                    os.remove(caminho_antigo)
                except Exception as e:
                    print(f"Erro ao apagar imagem antiga: {e}")

        #Após essa validação salvamos a nova imagem
        salvarArquivo(arquivo, novo_nome)

        #Atualizamos o banco de dados
        usuario.imagem = novo_nome 
        
        db.session.commit()

        return {'status': 'SUCESSO', 'mensagem': 'Imagem de perfil atualizada!', 'data': usuario.to_dict()}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao salvar imagem: {str(e)}'}
    
def atualizarPerfil(id_usuario, dados):

    try:
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário não encontrado.'}

        if 'nome' in dados:
            usuario.nome = dados['nome']
            
        if 'cargo' in dados:
            usuario.cargo = dados['cargo']
            
        if 'localizacao' in dados:
            usuario.localizacao = dados['localizacao']
            
        if 'descricaoMD' in dados:
            usuario.descricaoMD = dados['descricaoMD']

        if 'habilidades' in dados:
            entrada = dados['habilidades']
            
            #Se vier de um form HTML (string), separa por vírgula
            if isinstance(entrada, str):
                lista_nomes = [s.strip() for s in entrada.split(',') if s.strip()]
            else:
                lista_nomes = entrada # Já é lista (JSON)

            #Limpa as habilidades atuais para substituir pelas novas
            usuario.habilidades = []

            for nome in lista_nomes:
                nome_limpo = nome.strip().title()
                if not nome_limpo: continue
                
                # Busca ou cria a Tag
                tag = Tag.query.filter_by(nome=nome_limpo).first()
                if not tag:
                    tag = Tag(nome=nome_limpo)
                
                # Adiciona à lista (evita duplicatas)
                if tag not in usuario.habilidades:
                    usuario.habilidades.append(tag)

        
        db.session.commit()
        
        return {
            'status': 'SUCESSO', 
            'mensagem': 'Perfil atualizado com sucesso!', 
            'data': usuario.to_dict()
        }

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao atualizar perfil: {str(e)}'}