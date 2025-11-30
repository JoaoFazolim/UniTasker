from models import  *
from extensions import db
from datetime import datetime

def criarSolicitacao(dados, usuario_cliente):
    
    servico_id = dados.get('servico_id')
    valor_oferta = dados.get('valor_oferta')
    descricao = dados.get('descricao')
    
    #Validação
    if not servico_id or not valor_oferta or not descricao:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Preencha todos os campos da proposta.'}

    try:
        servico = Servico.query.get(servico_id)
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}

        #Não pode contratar seu próprio serviço
        if servico.usuario_id == usuario_cliente.id:
            return {'status': 'CONFLITO', 'mensagem': 'Você não pode contratar seu próprio serviço.'}

        #Cria a solicitação
        nova_solicitacao = Solicitacao(
            valor_ofertado=float(valor_oferta),
            descricao_pedido=descricao,
            servico_id=servico.id,
            cliente_id=usuario_cliente.id,
            prestador_id=servico.usuario_id
        )

        db.session.add(nova_solicitacao)
        db.session.commit()

        return {'status': 'SUCESSO', 'mensagem': 'Proposta enviada!', 'data': nova_solicitacao.to_dict()}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}


def responderSolicitacao(id_solicitacao, acao, usuario_logado):

    try:
        solicitacao = Solicitacao.query.get(id_solicitacao)
        if not solicitacao:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Solicitação não encontrada.'}

        #Só o prestador pode aceitar/recusar
        if solicitacao.prestador_id != usuario_logado.id:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Apenas o prestador pode responder.'}

        if solicitacao.status != 'pendente':
            return {'status': 'CONFLITO', 'mensagem': 'Esta solicitação já foi respondida.'}

        if acao == 'aceitar':
            solicitacao.status = 'aceita'
            solicitacao.data_resposta = datetime.utcnow()
            msg = "Proposta aceita!"
        elif acao == 'recusar':
            solicitacao.status = 'recusada'
            solicitacao.data_resposta = datetime.utcnow()
            msg = "Proposta recusada."
        else:
            return {'status': 'FORM_INVALIDO', 'mensagem': 'Ação inválida.'}

        db.session.commit()
        return {'status': 'SUCESSO', 'mensagem': msg}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}


def listarMinhasSolicitacoes(usuario_logado, tipo='enviadas'):

    try:
        if tipo == 'enviadas':
            lista = Solicitacao.query.filter_by(cliente_id=usuario_logado.id).order_by(Solicitacao.data_solicitacao.desc()).all()
        else:
            lista = Solicitacao.query.filter_by(prestador_id=usuario_logado.id).order_by(Solicitacao.data_solicitacao.desc()).all()

        return {'status': 'SUCESSO', 'data': [s.to_dict() for s in lista]}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}