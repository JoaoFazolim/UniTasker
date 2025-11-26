from models import db
from datetime import datetime

class Mensagem(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

    conversa_id = db.Column(db.Integer, db.ForeignKey('conversa.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    remetente = db.relationship('Usuario', foreign_keys=[remetente_id])