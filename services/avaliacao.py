from models import *
from extensions import db
from datetime import datetime
from sqlalchemy.sql import func

def criarAvaliacao(dados, usuario_logado):
 
    servico_id = dados.get('servico_id')
    nota = dados.get('nota')
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')

    #Validação básica
    if not servico_id or nota is None or not titulo or not descricao:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Serviço e nota são obrigatórios.'}

    try:
        nota = float(nota)
        if nota < 0 or nota > 5:
            return {'status': 'FORM_INVALIDO', 'mensagem': 'A nota deve ser entre 0 e 5.'}

        servico = Servico.query.get(servico_id)
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}

        #Não deixa avaliar o próprio serviço 💀
        if servico.usuario_id == usuario_logado.id:
            return {'status': 'CONFLITO', 'mensagem': 'Você não pode avaliar seu próprio serviço.'}

        #Verifica se já avaliou o serviço antes
        avaliacao_existente = Avaliacao.query.filter_by(
            servico_id=servico.id, 
            usuario_avaliador_id=usuario_logado.id
        ).first()

        if avaliacao_existente:
            return {'status': 'CONFLITO', 'mensagem': 'Você já avaliou este serviço.'}

        #Cria nova avaliação
        nova_avaliacao = Avaliacao(
            titulo=titulo,
            nota=nota,
            descricao=descricao,
            data_avaliacao=datetime.utcnow(),
            usuario_avaliador_id=usuario_logado.id, # Quem avaliou
            usuario_avaliado_id=servico.usuario_id, # O dono do serviço (prestador)
            servico_id=servico.id
        )

        db.session.add(nova_avaliacao)
        
        #Atualiza para garantir q a nova avaliação vai contar mas sem fechar a transação ainda
        db.session.flush()

        #Atualização da nota geral do perfil
        prestador = Usuario.query.get(servico.usuario_id)
        
        # Calculamos a média direto no banco de dados
        nova_media = db.session.query(func.avg(Avaliacao.nota))\
            .filter(Avaliacao.usuario_avaliado_id == prestador.id)\
            .scalar()
        
        #Atualiza a nota do prestador (arredondando se quiser)
        prestador.notaGeral = float(nova_media) if nova_media else 0.0

        db.session.commit()

        return {
            'status': 'SUCESSO',
            'mensagem': 'Avaliação registrada com sucesso!',
            'data': nova_avaliacao.to_dict()
        }

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao avaliar: {str(e)}'}


def listarAvaliacoesServico(id_servico):
    try:
        avaliacoes = Avaliacao.query.filter_by(servico_id=id_servico).order_by(Avaliacao.data_avaliacao.desc()).all()
        
        return {
            'status': 'SUCESSO',
            'data': [a.to_dict() for a in avaliacoes]
        }
    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}


def listarAvaliacoesUsuario(id_usuario):
    try:
        #Busca avaliações onde o usuário foi o prestador
        avaliacoes = Avaliacao.query.filter_by(usuario_avaliado_id=id_usuario).order_by(Avaliacao.data_avaliacao.desc()).all()
        
        return {
            'status': 'SUCESSO',
            'data': [a.to_dict() for a in avaliacoes]
        }
    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}