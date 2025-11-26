from models import db
from datetime import datetime

class Avaliacao(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False) 
    nota = db.Column(db.Float, nullable=False)
    
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)


    usuario_avaliador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario_avaliado_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)

    avaliador = db.relationship('Usuario', foreign_keys=[usuario_avaliador_id], backref='avaliacoes_feitas')
    avaliado = db.relationship('Usuario', foreign_keys=[usuario_avaliado_id], backref='avaliacoes_recebidas')
    servico = db.relationship('Servico', backref='avaliacoes')

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'nota': self.nota,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'avaliador': self.avaliador.nome if self.avaliador else None,
            'servico_titulo': self.servico.titulo if self.servico else None
        }