from models import  *
from extensions import db
from datetime import datetime

def criarSolicitacao(dados, usuario_cliente):
    
    servico_id = dados.get('servico_id')
    valor_oferta = dados.get('valor_ofertado')
    descricao = dados.get('descricao_pedido')
    
    #Validação
    if not servico_id or not valor_oferta or not descricao:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Preencha todos os campos da proposta.'}

    try:
        #Validação de Valor
        try:
            valor_float = float(valor_oferta)
            if valor_float < 0:
                return {'status': 'FORM_INVALIDO', 'mensagem': 'O valor da oferta não pode ser negativo.'}
        except ValueError:
            return {'status': 'FORM_INVALIDO', 'mensagem': 'Valor monetário inválido.'}
        servico = Servico.query.get(servico_id)
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}
        
        if servico.estado != 'ativo':
            return {'status': 'CONFLITO', 'mensagem': 'Este serviço não está disponível para novas propostas.'}


        #Não pode contratar seu próprio serviço
        if int(servico.usuario_id) == int(usuario_cliente.id):
            return {'status': 'CONFLITO', 'mensagem': 'Você não pode contratar seu próprio serviço.'}
        
        #Verifica se já existe uma solicitação pendente deste usuário para este serviço
        solicitacao_existente = Solicitacao.query.filter_by(
            servico_id=servico.id,
            cliente_id=usuario_cliente.id,
            status='pendente'
        ).first()

        if solicitacao_existente:
            return {'status': 'CONFLITO', 'mensagem': 'Você já possui uma proposta pendente para este serviço. Aguarde a resposta.'}

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

        #O usuário tem que fazer parte do negócio
        if usuario_logado.id not in [solicitacao.prestador_id, solicitacao.cliente_id]:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Sem permissão.'}

    
        if acao in ['aceitar', 'recusar']:
            if usuario_logado.id != solicitacao.prestador_id:
                return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Apenas o prestador pode aceitar ou recusar propostas iniciais.'}
            
            if solicitacao.status != 'pendente':
                return {'status': 'CONFLITO', 'mensagem': 'Esta solicitação já foi processada.'}
            
            solicitacao.status = 'aceita' if acao == 'aceitar' else 'recusada'
            solicitacao.data_resposta = datetime.utcnow()
            
            db.session.commit()
            return {'status': 'SUCESSO', 'mensagem': f"Proposta {solicitacao.status} com sucesso."}

        #Ação de concluir pode ser realizada pelo prestador ou quem contratou
        elif acao == 'concluir':
            
            if solicitacao.status != 'aceita':
                return {'status': 'CONFLITO', 'mensagem': 'Apenas serviços em andamento podem ser concluídos.'}
            
            solicitacao.status = 'concluida'
            solicitacao.data_conclusao = datetime.utcnow()
            
            db.session.commit()
            return {'status': 'SUCESSO', 'mensagem': "Serviço marcado como concluído! Avaliação liberada."}

        #Ação de cancelar uma solicitação pendente
        elif acao == 'cancelar':
            if usuario_logado.id != solicitacao.cliente_id:
                return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Apenas o cliente pode cancelar a proposta.'}
            
            if solicitacao.status != 'pendente':
                return {'status': 'CONFLITO', 'mensagem': 'Não é possível cancelar uma proposta que já foi respondida.'}
            
            solicitacao.status = 'cancelada'
            
            db.session.commit()
            return {'status': 'SUCESSO', 'mensagem': "Proposta cancelada."}

        else:
            return {'status': 'FORM_INVALIDO', 'mensagem': 'Ação inválida.'}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}

def verificarStatusSolicitacao(id_servico, usuario_cliente):

    if not usuario_cliente.is_authenticated:
        return None

    #Verifica se existe uma solicitação PENDENTE ou ACEITA
    solicitacao_ativa = Solicitacao.query.filter(
        Solicitacao.servico_id == id_servico,
        Solicitacao.cliente_id == usuario_cliente.id,
        Solicitacao.status.in_(['pendente', 'aceita'])
    ).first()

    return solicitacao_ativa

def buscarSolicitacaoConcluida(id_servico, usuario_cliente):

    if not usuario_cliente.is_authenticated:
        return None
        
    solicitacao_concluida = Solicitacao.query.filter_by(
        servico_id=id_servico,
        cliente_id=usuario_cliente.id,
        status='concluida'
    ).first()
    
    return solicitacao_concluida


def listarMinhasSolicitacoes(usuario_logado, tipo='enviadas'):

    try:
        if tipo == 'enviadas':
            lista = Solicitacao.query.filter_by(cliente_id=usuario_logado.id).order_by(Solicitacao.data_solicitacao.desc()).all()
        else:
            lista = Solicitacao.query.filter_by(prestador_id=usuario_logado.id).order_by(Solicitacao.data_solicitacao.desc()).all()

        return {'status': 'SUCESSO', 'data': [s.to_dict() for s in lista]}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}