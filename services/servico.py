from models import *
from extensions import db
from sqlalchemy import or_
import uuid
import os
from utils import validarArquivo, salvarArquivo
from flask import current_app


def criarServico(dados, lista_arquivos, usuario_logado):
    titulo = dados.get('titulo')
    descricaoMD = dados.get('descricaoMD')
    valor_minimo = dados.get('valor_minimo')
    valor_maximo = dados.get('valor_maximo')
    forma_pagamento = dados.get('forma_pagamento')
    tags_input = dados.get('tags', [])
    
    if forma_pagamento not in ["pago", "a_combinar", "voluntario"]:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Forma de pagamento inválida.'}
    
    if not titulo or not descricaoMD or not forma_pagamento or not dados.get('categoria_id'):
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Preencha os campos obrigatórios.'}
    
    if forma_pagamento == 'pago' and not valor_minimo:
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Valor mínimo obrigatório.'}

    try:
        categoria = Categoria.query.get(dados.get('categoria_id'))
        if not categoria:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Categoria inválida.'}

        valor_min = float(valor_minimo) if valor_minimo and str(valor_minimo).strip() != '' else 0.0
        valor_max = float(valor_maximo) if valor_maximo and str(valor_maximo).strip() != '' else None
        
        if forma_pagamento != 'pago':
            valor_min = 0.0
            valor_max = None

        if valor_min > 0 and valor_max and valor_max < valor_min:
            return {'status': 'FORM_INVALIDO', 'mensagem': 'O valor máximo não pode ser menor que o mínimo.'}

        novoServico = Servico(
            titulo=titulo,
            descricaoMD=descricaoMD,
            valor_minimo=valor_min,
            valor_maximo=valor_max,
            forma_pagamento=forma_pagamento,
            usuario_id=usuario_logado.id, 
            categoria_id=categoria.id
        )
        db.session.add(novoServico)
        
        #Tags
        lista_tags = tags_input if isinstance(tags_input, list) else [s.strip() for s in tags_input.split(',') if s.strip()]
        for nomeTag in lista_tags:
            nomeTag = nomeTag.strip().title()
            tag = Tag.query.filter_by(nome=nomeTag).first()
            if not tag: tag = Tag(nome=nomeTag)
            novoServico.tags.append(tag)
        
       
        db.session.flush()
        
        ids_remover = dados.get('imagens_remover', '')
        id_capa = dados.get('imagem_capa_id')

        sucesso, msg_img = processar_imagens_servico(novoServico, lista_arquivos, ids_remover, id_capa)
        if not sucesso:
            raise Exception(msg_img)

        db.session.commit()
        return {'status': 'SUCESSO', 'mensagem': 'Serviço criado!', 'data': novoServico.to_dict()}

    except ValueError:
        db.session.rollback()
        return {'status': 'FORM_INVALIDO', 'mensagem': 'Valores inválidos.'}
    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao criar: {str(e)}'}


def listarServicos(filtros=None):
    try:
        #Começa buscando apenas serviços ativos
        query = Servico.query.filter_by(estado='ativo')

        if filtros:
            #Filtro por Categoria (verifica a chave 'categoria')
            if filtros.get('categoria'):
                query = query.filter_by(categoria_id=filtros['categoria'])

            #Filtro por Texto (busca)
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

def processar_imagens_servico(servico, lista_novos_arquivos=None, ids_remover=[], id_capa_selecionada=None):

    try:
        #Remover imagens marcadas
        if ids_remover:
            
            for img_id in ids_remover:
                imagem = ServicoImagem.query.get(img_id)
                
                #Só apaga se a imagem pertencer ao serviço
                if imagem and imagem.servico_id == servico.id:
                    # Remove do disco
                    caminho_pasta = current_app.config['UPLOAD_FOLDER']
                    caminho_arquivo = os.path.join(caminho_pasta, imagem.caminho)
                    if os.path.exists(caminho_arquivo):
                        try: os.remove(caminho_arquivo)
                        except: pass
                    
                    #Remove do banco
                    db.session.delete(imagem)
            
            #Persiste as remoções e atualiza o objeto servico
            db.session.commit() 
            db.session.refresh(servico)

        #Adicionar novas imagens
        if lista_novos_arquivos:
            imagens_salvas = 0
            LIMITE_IMAGENS = 4
            #Reconta quantas sobraram após a remoção
            qtd_atual = len(servico.imagens_lista) 
            
            for arquivo in lista_novos_arquivos:
                if (qtd_atual + imagens_salvas) >= LIMITE_IMAGENS:
                    break

                if arquivo and arquivo.filename != '' and validarArquivo(arquivo.filename):
                    extensao = arquivo.filename.rsplit('.', 1)[1].lower()
                    nome_novo = f"servico_{servico.id}_{uuid.uuid4().hex[:8]}.{extensao}"
                    
                    salvarArquivo(arquivo, nome_novo) 
                    
                    #Define como capa se for a primeira imagem e não houver outras
                    is_cover = False
                    if qtd_atual == 0 and imagens_salvas == 0 and not id_capa_selecionada:
                        is_cover = True

                    nova_img = ServicoImagem(caminho=nome_novo, servico_id=servico.id, is_cover=is_cover)
                    db.session.add(nova_img)
                    imagens_salvas += 1
        

        if id_capa_selecionada:

            print("Aqui essa porra")
            print(id_capa_selecionada)
            print(servico.imagens_lista)
            
            for img in servico.imagens_lista:
               
                if str(img.id) == str(id_capa_selecionada):
                    img.is_cover = True
                else:
                    img.is_cover = False
                print(img.to_dict())
            db.session.commit()

        return True, "Imagens processadas."

    except Exception as e:
        return False, f"Erro interno ao processar imagens: {str(e)}"

def editarServico(id_servico, dados,lista_arquivos, usuario_logado):
    try:
        servico = Servico.query.get(id_servico)
        
        if not servico:
            return {'status': 'NAO_ENCONTRADO', 'mensagem': 'Serviço não encontrado.'}
            

        if servico.usuario_id != usuario_logado.id:
            return {'status': 'NAO_AUTORIZADO', 'mensagem': 'Você não tem permissão para editar este serviço.'}


        novo_titulo = dados.get('titulo')
        if novo_titulo and novo_titulo != servico.titulo:
            servico.titulo = novo_titulo

        nova_descricao = dados.get('descricaoMD')
        if nova_descricao and nova_descricao != servico.descricaoMD:
            servico.descricaoMD = nova_descricao


        try:
            novo_min = float(dados['valor_minimo'])
            novo_max = float(dados['valor_maximo']) if dados['valor_maximo'] else None

            if novo_max is not None and novo_max < novo_min:
                return {'status': 'FORM_INVALIDO', 'mensagem': 'O valor máximo não pode ser menor que o mínimo.'}

            if novo_min != servico.valor_minimo:
                servico.valor_minimo = novo_min
            
            if novo_max != servico.valor_maximo:
                servico.valor_maximo = novo_max
                
        except ValueError:
            return {'status': 'FORM_INVALIDO', 'mensagem': 'Valores inválidos.'}


        nova_forma = dados.get('forma_pagamento')
        if nova_forma and nova_forma != servico.forma_pagamento:
            if nova_forma not in ['pago', 'voluntario', 'a_combinar']:
                return {'status': 'FORM_INVALIDO', 'mensagem': 'Forma de pagamento inválida.'}
            servico.forma_pagamento = nova_forma

        nova_categoria_id = dados.get('categoria_id')
        if nova_categoria_id and int(nova_categoria_id) != servico.categoria_id:
            #Verifica se existe antes de trocar
            if Categoria.query.get(nova_categoria_id):
                servico.categoria_id = int(nova_categoria_id)


        novo_estado = dados.get('estado')
        if novo_estado and novo_estado != servico.estado:
            if novo_estado in ['ativo', 'pausado']:
                servico.estado = novo_estado

        if 'tags' in dados:
            tags_input = dados['tags'] # Pode vir como string "Python, Java" ou lista
            
            # Normaliza para lista
            if isinstance(tags_input, str):
                lista_nomes_novos = [t.strip().title() for t in tags_input.split(',') if t.strip()]
            else:
                lista_nomes_novos = [t.strip().title() for t in tags_input if t.strip()]

            #Pega nomes das tags atuais para comparar
            tags_atuais = [t.nome for t in servico.tags]
            
            #Só mexe no banco se as listas forem diferentes
            if set(lista_nomes_novos) != set(tags_atuais):
                servico.tags = [] 
                for nome in lista_nomes_novos:
                    tag = Tag.query.filter_by(nome=nome).first()
                    if not tag:
                        tag = Tag(nome=nome)
                    servico.tags.append(tag)

        ids_remover = dados.get('imagens_remover', '')

        ids_remover_lista = [int(id) for id in ids_remover.split(',') if id.strip().isdigit()]
        

        id_capa = dados.get('imagem_capa_id') 

        sucesso, msg_img = processar_imagens_servico(servico, lista_arquivos, ids_remover_lista, id_capa)
        print(sucesso, msg_img)
        db.session.commit()
        
        return {'status': 'SUCESSO', 'mensagem': 'Serviço atualizado com sucesso.', 'data': servico.to_dict()}

    except Exception as e:
        db.session.rollback()
        return {'status': 'ERRO_GENERICO', 'mensagem': f'Erro ao editar: {str(e)}'}



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