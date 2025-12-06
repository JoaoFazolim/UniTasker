from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services import *
from utils import handleResponse


servico_bp = Blueprint('servico', __name__)

@servico_bp.route('/servico/criar', methods=['GET', 'POST'])
@login_required
def criar():
    #Se for POST, processa o formulário
    if request.method == 'POST':
        #Pega os dados de texto e campos normais
        dados = request.form.to_dict()
        
        #Pega os arquivos de upload (getlist é importante para múltiplos arquivos)
        lista_arquivos = request.files.getlist('fotos') 
        
        resposta = criarServico(dados, lista_arquivos, current_user)
        
        if resposta['status'] == 'SUCESSO':
            flash('Serviço criado com sucesso!', 'sucesso')
            return redirect(url_for('usuario.perfil_publico', username=current_user.username))
        else:
            return handleResponse(resposta, 'perfil')

    # Se for get renderiza o template correspondente passando o modo correto
    # Passamos modo='criar_servico'
    return render_template('perfil.html', dados=current_user.to_dict(), modo='criar_servico')

@servico_bp.route('/servico/editar/<int:id_servico>', methods=['GET', 'POST'])
@login_required
def editar(id_servico):
    #Busca o serviço para preencher o form
    resposta_servico = obterServico(id_servico)
    
    if resposta_servico['status'] != 'SUCESSO':
        flash('Serviço não encontrado.', 'erro')
        return redirect(url_for('usuario.perfil_publico', username=current_user.username))
    
    servico = resposta_servico['data']

    #Verifica se o usuário é dono
    if servico['usuario']['id'] != current_user.id:
        flash('Você não pode editar este serviço.', 'erro')
        return redirect(url_for('usuario.perfil_publico', username=current_user.username))

    #Se for um POST salva o serviço
    if request.method == 'POST':
        dados = request.form.to_dict()
        lista_arquivos = request.files.getlist('fotos')
        resposta = editarServico(id_servico, dados,lista_arquivos, current_user)
        
        if resposta['status'] == 'SUCESSO':
            flash('Serviço atualizado!', 'sucesso')
            return redirect(url_for('usuario.perfil_publico', username=current_user.username))
        else:
            flash(resposta['mensagem'], 'erro')

    #Se for GET, mostra o form preenchido
    return render_template('perfil.html', 
                           dados=current_user.to_dict(), 
                           modo='editar_servico', 
                           servico_editar=servico)

@servico_bp.route('/servico/<int:id_servico>', methods=['GET'])
def detalhes(id_servico):
    
    res_servico = obterServico(id_servico)
    
    if res_servico['status'] != 'SUCESSO':
        return handleResponse(res_servico, 'detalhesServico')
    
    servico_dados = res_servico['data']
    
    #Busca avaliações do servico
    res_avaliacoes = listarAvaliacoesServico(id_servico)
    lista_avaliacoes = res_avaliacoes['data'] if res_avaliacoes['status'] == 'SUCESSO' else []

    #Verifica se o usuário pode avaliar
    solicitacao_ativa = None
    pode_avaliar = False
    
    if current_user.is_authenticated:
        

        solicitacao_ativa = verificarStatusSolicitacao(id_servico, current_user)
 

        solicitacao_concluida = buscarSolicitacaoConcluida(id_servico, current_user)
   

        

        if solicitacao_concluida:
            
            pode_avaliar = verificarPodeAvaliar(id_servico, current_user)
         
    

    return render_template('detalhesServico.html', 
                            dados=servico_dados, 
                            lista_avaliacoes=lista_avaliacoes,
                            pode_avaliar=pode_avaliar,
                            solicitacao_ativa=solicitacao_ativa)

@servico_bp.route('/servicos', methods=['GET'])
def listar():
    #Usa os filtros passados na url que será montada com js no front
    filtros = request.args.to_dict()
    
    resposta = listarServicos(filtros)
    
    #Renderiza o template de listagem
    return handleResponse(resposta, 'listarServicos')