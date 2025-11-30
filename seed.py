from app import app as flask_app
from extensions import db
from models.categoria import Categoria
from models.usuario import Usuario
from models.servico import Servico
from models.tag import Tag
from flask_bcrypt import generate_password_hash 
from datetime import datetime




def seed_database():
    print("🌱 Plantando uns dados 🎲🎲...")
    
    #Categorias
    categorias_lista = [
        "Aulas e Monitoria", "Tecnologia e Programação", "Design e Multimídia",
        "Trabalhos Acadêmicos e ABNT", "Assistência Técnica", "Tradução e Redação",
        "Marketing e Negócios", "Saúde e Estética", "Outros"
    ]
    
    #Dicionário para guardar objetos e usar depois
    cats_objs = {} 
    
    for nome in categorias_lista:
        cat = Categoria.query.filter_by(nome=nome).first()
        if not cat:
            cat = Categoria(nome=nome)
            db.session.add(cat)
            print(f" [+] Categoria criada: {nome}")
        cats_objs[nome] = cat
    
    db.session.commit() 

    #Tags
    tags_lista = ["Python", "Java", "Web", "Design", "Logo", "Matemática", "Inglês"]
    tags_objs = {}
    
    for nome in tags_lista:
        tag = Tag.query.filter_by(nome=nome).first()
        if not tag:
            tag = Tag(nome=nome)
            db.session.add(tag)
        tags_objs[nome] = tag
        
    db.session.commit()

    #Botando uns usuários
    alice = Usuario.query.filter_by(email="alice@unitasker.com").first()
    if not alice:
        alice = Usuario(
            username="alice_dev",
            email="alice@unitasker.com",
            nome="Alice Developer",
            hashSenha=generate_password_hash("123456"), # Senha padrão
            role="user",
            descricaoMD="Sou desenvolvedora **Fullstack** e adoro ensinar.",
            cargo="Engenharia de Software",
            localizacao="Campus Sorocaba"
        )
        #Adiciona habilidade
        alice.habilidades.append(tags_objs["Python"])
        alice.habilidades.append(tags_objs["Web"])
        
        db.session.add(alice)
        print(" [+] Usuário Alice criado.")


    bob = Usuario.query.filter_by(email="bob@unitasker.com").first()
    if not bob:
        bob = Usuario(
            username="bob_student",
            email="bob@unitasker.com",
            nome="Bob Estudante",
            hashSenha=generate_password_hash("123456"),
            role="user",
            descricaoMD="Estudante de Design precisando de ajuda em programação.",
            cargo="Design Gráfico",
            localizacao="Campus Itu"
        )
        bob.habilidades.append(tags_objs["Design"])
        db.session.add(bob)
        print(" [+] Usuário Bob criado.")

    adm = Usuario.query.filter_by(email="admin@unitasker.com").first()
    if not adm:
        adm = Usuario(
            username="bob_admin",
            email="admin@unitasker.com",
            nome="Bob Admin",
            hashSenha=generate_password_hash("senhapoderosa123"),
            role="admin",
            descricaoMD="**Vo apaga sua conta**",
            cargo="Desempregado",
            localizacao="Campus Itu"
        )
        adm.habilidades.append(tags_objs["Python"])
        db.session.add(adm)
        print(" [+] Usuário Bob criado.")

    db.session.commit()

    #Alguns serviços
    servico1 = Servico.query.filter_by(titulo="Aulas Particulares de Python").first()
    if not servico1:
        servico1 = Servico(
            titulo="Aulas Particulares de Python",
            descricaoMD="Ensino lógica de programação e Python do zero. **Metodologia prática**.",
            valor_minimo=50.0,
            valor_maximo=80.0,
            forma_pagamento="pago",
            estado="ativo",
            usuario_id=alice.id,
            categoria_id=cats_objs["Tecnologia e Programação"].id
        )
        servico1.tags.append(tags_objs["Python"])
        db.session.add(servico1)
        print(" [+] Serviço Python criado.")


    servico2 = Servico.query.filter_by(titulo="Formatação de TCC").first()
    if not servico2:
        servico2 = Servico(
            titulo="Formatação de TCC",
            descricaoMD="Deixo seu trabalho nas normas da ABNT.",
            valor_minimo=0.0,
            valor_maximo=None,
            forma_pagamento="a_combinar",
            estado="ativo",
            usuario_id=alice.id,
            categoria_id=cats_objs["Trabalhos Acadêmicos e ABNT"].id
        )
        db.session.add(servico2)
        print(" [+] Serviço ABNT criado.")

    db.session.commit()
    print("✅ Banco de dados populado com sucesso!")


with flask_app.app_context():
    
    db.create_all()
    seed_database()