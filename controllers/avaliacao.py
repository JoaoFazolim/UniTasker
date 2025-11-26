from models import *
from datetime import datetime

def criarAvaliacao(dados, usuario_logado):
 
    servico_id = dados.get('servico_id')
    nota = dados.get('nota')
    comentario = dados.get('comentario')

    #Validação básica
    if not servico_id or nota is None:
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
            nota=nota,
            comentario=comentario,
            data_avaliacao=datetime.utcnow(),
            usuario_avaliador_id=usuario_logado.id, # Quem avaliou
            usuario_avaliado_id=servico.usuario_id, # O dono do serviço (prestador)
            servico_id=servico.id
        )

        db.session.add(nova_avaliacao)
        
        #Atualização da nota geral do perfil
        prestador = Usuario.query.get(servico.usuario_id)
        #Recalcula a nota geral com a nova avaliação
        avaliacoes_prestador = Avaliacao.query.filter_by(usuario_avaliado_id=prestador.id).all()
        
        
        total_notas = sum([a.nota for a in avaliacoes_prestador]) + nota
        qtd_notas = len(avaliacoes_prestador) + 1
        
        prestador.notaGeral = total_notas / qtd_notas

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