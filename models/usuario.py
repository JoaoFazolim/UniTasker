from models import db
from datetime import datetime
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True , nullable=False)
    hashSenha = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable = False, default='user')
    nome = db.Column(db.String(60), nullable=False)
    descricaoMD = db.Column(db.Text, nullable=False,default='')
    imagem = db.Column(db.String(30), nullable=True, default='default.png')
    notaGeral = db.Column(db.Float,nullable = False, default=0.0)
    criadoEm = db.Column(db.DateTime, default=datetime.utcnow)
    deletadoEm = db.Column(db.DateTime, nullable=True)

    @property
    def estaAtivo(self):
        #Propriedade pra verificar se o usuário está ativo
        return self.deletadoEm is None

    def to_dict(self):
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
            'ativo': self.estaAtivo
        }