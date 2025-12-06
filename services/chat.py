from models import *
from extensions import db
from sqlalchemy import or_

def enviarMensagem(dados, usuario_remetente):

    destinatario_id = dados.get('destinatario_id')
    conteudo = dados.get('conteudo')

    #Validação básica
    if not destinatario_id or not conteudo:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Destinatário e conteúdo são obrigatórios.'}

    try:
        #Verifica se o destinatário existe
        destinatario = Usuario.query.get(destinatario_id)
        if not destinatario:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Usuário destinatário não encontrado.'}

        #Verifica se o remetente é o mesmo do destinatário
        if usuario_remetente.id == int(destinatario_id):
            return {'status': 'CONFLITO', 'mensagem': 'Você não pode enviar mensagem para si mesmo, arrume um amigo'}

        #Verifica se a conversa entre os dois usuários ja existe
        conversa = Conversa.query.filter(
            or_(
                (Conversa.usuario1_id == usuario_remetente.id) & (Conversa.usuario2_id == destinatario_id),
                (Conversa.usuario1_id == destinatario_id) & (Conversa.usuario2_id == usuario_remetente.id)
            )
        ).first()

        #Se não existir, cria a conversa
        if not conversa:
            conversa = Conversa(
                usuario1_id=usuario_remetente.id,
                usuario2_id=destinatario_id
            )
            db.session.add(conversa)
            db.session.commit() 

        #Cria a mensagem
        nova_mensagem = Mensagem(
            conteudo=conteudo,
            conversa_id=conversa.id,
            remetente_id=usuario_remetente.id
        )

        db.session.add(nova_mensagem)
        db.session.commit()

        return {
            'status': 'CRIADO',
            'mensagem': 'Mensagem enviada!',
            'data': {
                'id': nova_mensagem.id,
                'conteudo': nova_mensagem.conteudo,
                'data_envio': nova_mensagem.data_envio.isoformat(),
                'conversa_id': conversa.id
            }
        }

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao enviar mensagem: {str(e)}'}


def listarConversas(usuario_logado):
    
    try:
        #Busca conversas que o usuário participa
        conversas = Conversa.query.filter(
            or_(
                Conversa.usuario1_id == usuario_logado.id,
                Conversa.usuario2_id == usuario_logado.id
            )
        ).all()

        lista_conversas = []
        for conv in conversas:
            #Pega o outro usuário da conversa
            outro_usuario = conv.usuario2 if conv.usuario1_id == usuario_logado.id else conv.usuario1
            
            #Ultima mensagem para preview
            ultima_msg = Mensagem.query.filter_by(conversa_id=conv.id).order_by(Mensagem.data_envio.desc()).first()

            lista_conversas.append({
                'id': conv.id,
                'usuario_com_quem_falo': {
                    'id': outro_usuario.id,
                    'nome': outro_usuario.nome,
                    'imagem': outro_usuario.imagem
                },
                'ultima_mensagem': ultima_msg.conteudo if ultima_msg else "Sem mensagens",
                'data_ultima_mensagem': ultima_msg.data_envio.isoformat() if ultima_msg else None
            })

        #Ordena pela mais recente as conversas
        lista_conversas.sort(key=lambda x: x['data_ultima_mensagem'] or '', reverse=True)

        return {'status': 'SUCESSO', 'data': lista_conversas}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}


def obterMensagens(id_conversa, usuario_logado):

    try:
        conversa = Conversa.query.get(id_conversa)
        
        if not conversa:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Conversa não encontrada.'}

        #Verifica se o usuário faz parte da conversa
        if usuario_logado.id not in [conversa.usuario1_id, conversa.usuario2_id]:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Você não tem permissão para ver essa conversa.'}

        #Busca todas as mensagens ordenadas por data
        mensagens = Mensagem.query.filter_by(conversa_id=id_conversa).order_by(Mensagem.data_envio.asc()).all()

        historico = []
        for msg in mensagens:
            historico.append({
                'id': msg.id,
                'conteudo': msg.conteudo,
                'data_envio': msg.data_envio.isoformat(),
                'remetente_id': msg.remetente_id,
                'sou_remetente': msg.remetente_id == usuario_logado.id 
            })

        return {'status': 'SUCESSO', 'data': historico}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}