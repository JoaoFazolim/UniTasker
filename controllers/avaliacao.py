from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services import *
from utils import handleResponse

avaliacao_bp = Blueprint('avaliacao', __name__)

@avaliacao_bp.route('/avaliacao/criar', methods=['POST'])
@login_required
def criar():
  
    dados = request.form.to_dict()
    
    resposta = criarAvaliacao(dados, current_user)
    
    servico_id = dados.get('servico_id')
    
    if resposta['status'] == 'SUCESSO':
        flash('Avaliação enviada com sucesso! Obrigado pelo feedback.', 'sucesso')
    else:
        flash(resposta.get('mensagem'), 'erro')
        
    #Volta para a página de detalhes do serviço
    if servico_id:
        return redirect(url_for('servico.detalhes', id_servico=servico_id))
    
    #Fallback
    return redirect(url_for('home.home'))