from models import *
from sqlalchemy import or_


def criarServico(dados, usuarioLogado):
   
    titulo = dados.get('titulo')
    descricaoMD = dados.get('descricaoMD')
    valor = dados.get('valor')
    categoria_id = dados.get('categoria_id')
    tags = dados.get('tags', []) 
    
    #Validação inicial
    if not titulo or not descricaoMD or valor is None or not categoria_id:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Preencha todos os campos obrigatórios.'}

    try:
        #Verifica se a categoria existe
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Categoria inválida.'}

        #Cria o objeto do Serviço
        novoServico = Servico(
            titulo=titulo,
            descricaoMD=descricaoMD,
            valor=float(valor),
            usuario_id=usuarioLogado.id, 
            categoria_id=categoria.id
        )

        #Processamento de tags
        for nomeTag in tags:
            #Padroniza as tags
            nomeTag = nomeTag.strip()
            
            #Busca as tags e cria uma nova caso não exista
            tag = Tag.query.filter_by(nome=nomeTag).first()
            if not tag:
                tag = Tag(nome=nomeTag)
            
            # Adiciona a tag ao serviço
            novoServico.tags.append(tag)

        db.session.add(novoServico)
        db.session.commit()

        return {
            'status': 'SUCESSO',
            'mensagem': 'Serviço criado com sucesso!',
            'data': novoServico.to_dict()
        }

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao criar serviço: {str(e)}'}



def listarServicos(filtros=None):

    try:
        #Começa buscando apenas serviços ativos
        query = Servico.query.filter_by(estado='ativo')

        if filtros:
            if filtros.get('categoria_id'):
                query = query.filter_by(categoria_id=filtros['categoria_id'])

            if filtros.get('busca'):
                termo = f"%{filtros['busca']}%"
                
                #O or_ faz ele buscar o texto no titulo e na descricão
                query = query.filter(
                    or_(
                        Servico.titulo.ilike(termo),
                        Servico.descricaoMD.ilike(termo)
                        )
                )

        #Ordena por mais recentes
        query = query.order_by(Servico.dataCriacao.desc())
        
        servicos = query.all()
        
        #Converte lista de objetos pra uma lista de dicionários
        lista_servicos = [s.to_dict() for s in servicos]

        return {'status': 'SUCESSO', 'data': lista_servicos}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao listar serviços: {str(e)}'}



def obterServico(id_servico):
    try:
        servico = Servico.query.get(id_servico)
        
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}
            
        return {'status': 'SUCESSO', 'data': servico.to_dict()}

    except Exception as e:
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}


def editarServico(id_servico, dados, usuario_logado):
    try:
        servico = Servico.query.get(id_servico)
        
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}
            
        #Verifica se quem está tentando editar é o dono do anuncio
        if servico.usuario_id != usuario_logado.id:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Você não tem permissão para editar este serviço.'}

        #Atualiza campos enviados
        if 'titulo' in dados: 
            servico.titulo = dados['titulo']
        if 'descricaoMD' in dados: 
            servico.descricaoMD = dados['descricaoMD']
        if 'valor' in dados: 
            servico.valor = float(dados['valor'])
        
        #Atualizar estado
        if 'estado' in dados: servico.estado = dados['estado'] 

        if 'tags' in dados:
                tags_lista = dados['tags']
                
                #Limpa as tags primeiro
                servico.tags = []
                
                # 2. Adiciona as novas
                for nome_tag in tags_lista:
                    nome_tag = nome_tag.strip()
                    tag = Tag.query.filter_by(nome=nome_tag).first()
                    if not tag:
                        tag = Tag(nome=nome_tag)
                    servico.tags.append(tag)


        db.session.commit()
        
        return {'status': 'SUCESSO', 'mensagem': 'Serviço atualizado.', 'data': servico.to_dict()}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}



def excluirServico(id_servico, usuario_logado):
    try:
        servico = Servico.query.get(id_servico)
        
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}
            
        if servico.usuario_id != usuario_logado.id:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Sem permissão.'}

        #Soft delete de serviços
        servico.estado = 'excluido' 
        
        db.session.commit()
        return {'status': 'SUCESSO', 'mensagem': 'Serviço removido com sucesso.'}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': str(e)}