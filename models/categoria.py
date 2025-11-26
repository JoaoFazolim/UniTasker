from models import db

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

    servicos = db.relationship('Servico', backref='categoria', lazy=True)

