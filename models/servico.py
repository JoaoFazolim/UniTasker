from extensions import db
from models.tag import servico_tags
from datetime import datetime

class ServicoImagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caminho = db.Column(db.String(150), nullable=False) 
    is_cover = db.Column(db.Boolean, default=False, nullable=False)

    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'caminho': self.caminho, 'is_cover':self.is_cover}


class Servico(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricaoMD = db.Column(db.Text, nullable=False)

    #Range de preço para o serviço
    valor_minimo = db.Column(db.Float, nullable=False) 
    #O valor máximo é opcional e só usado caso tenha um range e não um valor fixo
    valor_maximo = db.Column(db.Float, nullable=True)

    #Registra a forma de pagamento escolhida
    forma_pagamento = db.Column(db.String(20), default='pago', nullable=False) 
    
    estado = db.Column(db.String(20), default='ativo', nullable=False)
    dataCriacao = db.Column(db.DateTime, default=datetime.utcnow)

    #Relacionamentos
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='servicos_ofertados')

    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    
    tags = db.relationship('Tag', secondary=servico_tags, lazy='subquery',
                           backref=db.backref('servicos', lazy=True))
    
    #Com esse cascade caso o serviço seja apagado os registros das imagens serão apagados tambem
    imagens_lista = db.relationship('ServicoImagem', backref='servico', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):

        capa_obj = None
        if self.imagens_lista:
            capa_obj = next((img for img in self.imagens_lista if img.is_cover), None)

        capa_dict = {
            'id': capa_obj.id,
            'caminho': capa_obj.caminho,
            'is_cover': capa_obj.is_cover
        } if capa_obj else None

        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricaoMD': self.descricaoMD,
            'valor_minimo': self.valor_minimo,
            'valor_maximo': self.valor_maximo,
            'forma_pagamento': self.forma_pagamento, 
            'imagens': [{'id': img.id, 'caminho': img.caminho, 'is_cover': img.is_cover} for img in self.imagens_lista],
            'imagem_capa': capa_dict,
            'estado': self.estado,
            'dataCriacao': self.dataCriacao.isoformat() if self.dataCriacao else None,
            'categoria': self.categoria.nome if self.categoria else None,
            'categoria_id': self.categoria_id,
            'tags': [tag.nome for tag in self.tags],
            'usuario': {
                'id': self.usuario.id,
                'nome': self.usuario.nome,
                'username':self.usuario.username,
                'imagem': self.usuario.imagem
            } if self.usuario else None
        }