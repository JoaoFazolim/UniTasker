from models import db
from models.tag import servico_tags
from datetime import datetime

class Servico(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricaoMD = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Float, nullable=False)

    imagens = db.Column(db.Text, nullable=True) 
    
    estado = db.Column(db.String(20), default='ativo', nullable=False)
    
    dataCriacao = db.Column(db.DateTime, default=datetime.utcnow)

    #Relacionamentos
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='servicos_ofertados')

    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    
    tags = db.relationship('Tag', secondary=servico_tags, lazy='subquery',
                           backref=db.backref('servicos', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'valor': self.valor,
            'categoria': self.categoria.nome,
            'tags': [tag.nome for tag in self.tags],
            'usuario': self.usuario.nome
        }