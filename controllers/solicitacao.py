from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services import *
from utils import handleResponse

solicitacao_bp = Blueprint('solicitacao', __name__)

@solicitacao_bp.route('/solicitacao/criar', methods=['POST'])
@login_required
def criar():

    dados = request.form.to_dict()

    resposta = criarSolicitacao(dados, current_user)
    
    #Verifica se o cliente pediu JSON explicitamente (postman)
    wants_json = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'

    if wants_json:
  
        return handleResponse(resposta, 'detalhes_servico')


    servico_id = dados.get('servico_id')

    if resposta['status'] == 'SUCESSO':
        flash('Proposta enviada com sucesso!', 'sucesso')
        
        if servico_id:
            return redirect(url_for('servico.detalhes', id_servico=servico_id))
        
        return redirect(url_for('usuario.perfil_publico', username=current_user.username))
    
    else:
        flash(resposta.get('mensagem'), 'erro')
        
        if servico_id:
            return redirect(url_for('servico.detalhes', id_servico=servico_id))
            
        return redirect(url_for('home.home'))
    
@solicitacao_bp.route('/solicitacao/<int:id_solicitacao>/<acao>', methods=['POST'])
@login_required
def responder(id_solicitacao, acao):

    resposta = responderSolicitacao(id_solicitacao, acao, current_user)

    #Verificação postman
    wants_json = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'
    
    if wants_json or request.is_json:

        return handleResponse(resposta, 'perfil')

    if resposta['status'] == 'SUCESSO':
        flash(resposta.get('mensagem'), 'sucesso')
    else:
        flash(resposta.get('mensagem'), 'erro')

    #Volta para o perfil
    return redirect(url_for('usuario.perfil_publico', username=current_user.username))



#Util para testes no postman
@solicitacao_bp.route('/solicitacoes/listar', methods=['GET'])
@login_required
def listar():
    tipo = request.args.get('tipo', 'enviadas')
    resposta = listarMinhasSolicitacoes(current_user, tipo)
    return handleResponse(resposta, 'listar_solicitacoes')