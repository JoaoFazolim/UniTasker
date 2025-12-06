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

        dicionario = usuario.to_dict()
        print(dicionario['portfolio'])
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
    
def processar_imagens_portfolio(usuario, lista_novos_arquivos=None, ids_remover_str=None, id_capa_selecionada=None):
    print("=-=-=-=-=--=-=-=- DADOS AQUI =-=-=-=-=-=-=-=-==-")
    print(lista_novos_arquivos)
    print("=-=-=-=-=--=-=-=- ARQUIVO PERFIL AQUI =-=-=-=-=-=-=-=-==-")
    print(ids_remover_str)
    print("=-=-=-=-=--=-=-=- ARQUIVOS PORTFOLIO AQUI =-=-=-=-=-=-=-=-==-")
    print(id_capa_selecionada)

    try:
        #Imagens para remover
        if ids_remover_str:
            ids_para_remover = [int(id) for id in str(ids_remover_str).split(',') if id.strip().isdigit()]
            
            for img_id in ids_para_remover:
                imagem = UsuarioPortfolio.query.get(img_id)
                if imagem and imagem.usuario_id == usuario.id:
                    # Remove do disco
                    caminho_base = current_app.config['UPLOAD_FOLDER']
                    # imagem.caminho já é 'portfolio/nome.jpg'
                    caminho_arquivo = os.path.join(caminho_base, imagem.caminho)
                    
                    if os.path.exists(caminho_arquivo):
                        try: os.remove(caminho_arquivo)
                        except: pass
                    
                    db.session.delete(imagem)
            
            db.session.flush()

        #Adicionar arquivos
        if lista_novos_arquivos:
            imagens_salvas = 0
            LIMITE = 4
            qtd_atual = len(usuario.portfolio)
            
            #Garante pasta portfolio
            pasta_portfolio = os.path.join(current_app.config['UPLOAD_FOLDER'], 'portfolio')
            if not os.path.exists(pasta_portfolio): os.makedirs(pasta_portfolio)

            for arquivo in lista_novos_arquivos:
                if (qtd_atual + imagens_salvas) >= LIMITE: break

                if arquivo and arquivo.filename != '' and validarArquivo(arquivo.filename):
                    ext = arquivo.filename.rsplit('.', 1)[1].lower()
                    novo_nome = f"port_{usuario.id}_{uuid.uuid4().hex[:8]}.{ext}"
                    
                
                    salvarArquivo(arquivo, novo_nome)
                    
                    #Define a capa se for a primeira imagem
                    eh_capa = (qtd_atual == 0 and imagens_salvas == 0 and not id_capa_selecionada)
                    
                    nova_img = UsuarioPortfolio(caminho=f"{novo_nome}", usuario_id=usuario.id, is_cover=eh_capa)
                    db.session.add(nova_img)
                    imagens_salvas += 1

        #Mudar capa
        if id_capa_selecionada:
            db.session.flush()
            for img in usuario.portfolio:
                img.is_cover = (str(img.id) == str(id_capa_selecionada))

        return True, "Portfólio atualizado."

    except Exception as e:
        return False, f"Erro no portfólio: {str(e)}"


def atualizarPerfil(id_usuario, dados, arquivo_perfil=None, lista_arquivos_portfolio=None):
   
    try:
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário não encontrado.'}

        #Mudança do avatar
        if arquivo_perfil and arquivo_perfil.filename != '':
            #Chama a função de alterar
            resp_avatar = atualizarImagemPerfil(id_usuario, arquivo_perfil)
            #Se der erro no avatar, aborta e avisa
            if resp_avatar['status'] != 'SUCESSO':
                return resp_avatar 

        #Mudança de textos
        if 'editName' in dados: usuario.nome = dados['editName'] or usuario.nome
        if 'editJob' in dados: usuario.cargo = dados['editJob']
        if 'editLocation' in dados: usuario.localizacao = dados['editLocation']
        if 'descricaoMD' in dados: usuario.descricaoMD = dados['descricaoMD']

        #Mudança de habilidades
        if 'habilidades' in dados:
            entrada = dados['habilidades']
            lista_nomes = []
            if isinstance(entrada, str):
                lista_nomes = [s.strip().title() for s in entrada.split(',') if s.strip()]
            elif isinstance(entrada, list):
                lista_nomes = [s.strip().title() for s in entrada if s.strip()]

            #Atualiza lista se mudou
            if set(lista_nomes) != set([t.nome for t in usuario.habilidades]):
                usuario.habilidades = []
                for nome in lista_nomes:
                    tag = Tag.query.filter_by(nome=nome).first()
                    if not tag: tag = Tag(nome=nome)
                    usuario.habilidades.append(tag)

        #Tratar portfolio
        ids_remover = dados.get('remover_portfolio_id')
        id_capa = dados.get('imagem_capa_id')
        
        if lista_arquivos_portfolio or ids_remover or id_capa:
            sucesso, msg_port = processar_imagens_portfolio(usuario, lista_arquivos_portfolio, ids_remover, id_capa)
            if not sucesso:
                db.session.rollback()
                return {'status': 'ERRO_GENERICO', 'mensagem': msg_port}

        #Commita tudo
        db.session.commit()
        
        return {
            'status': 'SUCESSO', 
            'mensagem': 'Perfil atualizado com sucesso!', 
            'data': usuario.to_dict()
        }

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao atualizar perfil: {str(e)}'}
