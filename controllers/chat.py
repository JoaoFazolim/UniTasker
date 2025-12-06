from flask import Blueprint, jsonify, request
from flask_socketio import join_room, emit, leave_room
from extensions import socketio 
from services import *
from models import Conversa 
from flask_login import current_user, login_required 
from utils import handleResponse


chat_bp = Blueprint('chat', __name__, url_prefix='/chat')



@chat_bp.route('/conversas', methods=['GET'])
@login_required 
def get_conversas():

    usuario = current_user 
    
    resultado = listarConversas(usuario)
    
    if resultado['status'] == 'SUCESSO':
        return jsonify(resultado['data']), 200
    else:
        return jsonify(resultado), 500 

@chat_bp.route('/conversas/<int:conversa_id>/mensagens', methods=['GET'])
@login_required
def get_mensagens(conversa_id):

    usuario = current_user 
    
    resultado = obterMensagens(conversa_id, usuario)
    
    if resultado['status'] == 'SUCESSO':
        return jsonify(resultado['data']), 200
    elif resultado['status'] in ['NAO_AUTORIZADO', 'NAO_ENCONTRADO']:
        return jsonify(resultado), 403 
    else:
        return jsonify(resultado), 500



@socketio.on('join')
def on_join(data):
    #Verifica a autenticação manualmente
    if not current_user.is_authenticated:
        emit('error', {'mensagem': 'Autenticação SocketIO falhou (Usuário não logado).'}, room=request.sid)
        return
        
    usuario = current_user 
    conversa_id = data.get('conversa_id')
    room = str(conversa_id) 

    conversa = Conversa.query.get(conversa_id)
    if not conversa or usuario.id not in [conversa.usuario1_id, conversa.usuario2_id]:
        emit('error', {'mensagem': 'Sem permissão para entrar na sala.'}, room=request.sid)
        return
        
    join_room(room)
    emit('status', {'msg': f'Entrou na sala {conversa_id}'}, room=request.sid)


@socketio.on('send_message')
def handle_send_message(data):
    #Verifica a autenticação manualmente
    if not current_user.is_authenticated:
        emit('error', {'mensagem': 'Autenticação SocketIO falhou (Usuário não logado).'}, room=request.sid)
        return
        
    usuario_remetente = current_user 
    conversa_id = data.get('conversa_id')
    conteudo = data.get('conteudo')

    #Encontra a conversa e determina o destinatário
    conversa = Conversa.query.get(conversa_id)
    if not conversa:
        emit('error', {'mensagem': 'Conversa não encontrada. Impossível enviar.'}, room=request.sid)
        return

    destinatario_id = conversa.usuario2_id if conversa.usuario1_id == usuario_remetente.id else conversa.usuario1_id
    
    dados_para_service = {
        'destinatario_id': destinatario_id,
        'conteudo': conteudo
    }
    
    #Salva no DB através da sua service
    resultado = enviarMensagem(dados_para_service, usuario_remetente)

    if resultado['status'] == 'SUCESSO' or resultado['status'] == 'CRIADO':
        room = str(conversa_id)
        
        #Prepara o payload para o frontend
        payload = {
            'id': resultado['data']['id'],
            'conteudo': resultado['data']['conteudo'],
            'data_envio': resultado['data']['data_envio'], 
            'conversa_id': conversa_id,
            'remetente_id': usuario_remetente.id,
            'remetente_nome': usuario_remetente.nome if hasattr(usuario_remetente, 'nome') else 'Eu' 
        }
        
        #Emite o evento para todos na sala (tempo real)
        emit('receive_message', payload, room=room) 
    else:
        emit('error', resultado, room=request.sid)



@chat_bp.route('/iniciar-conversa', methods=['POST'])
@login_required
def iniciar_conversa():
    usuario_remetente = current_user 
    dados = request.json

    resultado = enviarMensagem(dados, usuario_remetente)

    return handleResponse(resultado, nomeTemplate='chat/placeholder')