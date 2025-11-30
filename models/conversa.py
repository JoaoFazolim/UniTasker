from extensions import db

class Conversa(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    
    usuario1_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario2_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    mensagens = db.relationship('Mensagem', backref='conversa_pai', lazy=True)
    
    usuario1 = db.relationship('Usuario', foreign_keys=[usuario1_id])
    usuario2 = db.relationship('Usuario', foreign_keys=[usuario2_id])