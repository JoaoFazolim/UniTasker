from extensions import db
from datetime import datetime
from models.tag import usuario_tags
from flask_login import UserMixin

class UsuarioPortfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caminho = db.Column(db.String(150), nullable=False) 
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'caminho': self.caminho}

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True , nullable=False)
    nome = db.Column(db.String(30), nullable=False)

    descricaoMD = db.Column(db.Text, nullable=False,default='')
    imagem = db.Column(db.String(100), nullable=True)
    notaGeral = db.Column(db.Float,nullable = False, default=0.0)

    cargo = db.Column(db.String(50), nullable=True) 
    localizacao = db.Column(db.String(30), nullable=True)

    hashSenha = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable = False, default='user')

    criadoEm = db.Column(db.DateTime, default=datetime.utcnow)
    deletadoEm = db.Column(db.DateTime, nullable=True)

    habilidades = db.relationship('Tag', secondary=usuario_tags, lazy='subquery',backref=db.backref('usuarios', lazy=True))
    portfolio = db.relationship('UsuarioPortfolio', backref='dono', lazy=True, cascade="all, delete-orphan")


    @property
    def estaAtivo(self):
        #Propriedade pra verificar se o usuário está ativo
        return self.deletadoEm is None

    def to_dict(self):

 
        lista_servicos = []
        for servico in self.servicos_ofertados:
            if servico.estado == 'ativo':
                
                #Achando a capa
                caminho_capa = None
                if servico.imagens_lista:
                    #Tenta encontrar a imagem marcada como capa (is_cover == True)
                    #next() retorna o primeiro item que satisfaz a condição, ou None
                    imagem_capa_obj = next((img for img in servico.imagens_lista if img.is_cover), None)
                    
                    if imagem_capa_obj:
                        caminho_capa = imagem_capa_obj.caminho
                    else:
                        #Se nenhuma estiver marcada, pega a primeira da lista
                        caminho_capa = servico.imagens_lista[0].caminho

                lista_servicos.append({
                    'id': servico.id,
                    'titulo': servico.titulo,
                    'valor_minimo': servico.valor_minimo, 
                    'valor_maximo': servico.valor_maximo,
                    'forma_pagamento': servico.forma_pagamento,
                    'categoria': servico.categoria.nome if servico.categoria else 'Sem categoria',
                    'imagem_capa': caminho_capa
                })

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nome': self.nome,
            'role': self.role,
            'descricaoMD': self.descricaoMD,
            'imagem': self.imagem,
            'notaGeral': self.notaGeral,
            'criadoEm': self.criadoEm.isoformat() if self.criadoEm else None,
            'ativo': self.estaAtivo,
            'cargo': self.cargo,
            'localizacao': self.localizacao,
            'habilidades': [tag.nome for tag in self.habilidades],
            'portfolio': [img.caminho for img in self.portfolio],
            'servicos': lista_servicos
        }