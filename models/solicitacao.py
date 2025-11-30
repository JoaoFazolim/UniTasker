from extensions import db
from datetime import datetime



class Solicitacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    #Status: 'pendente', 'aceita', 'recusada', 'concluida'
    status = db.Column(db.String(20), default='pendente', nullable=False)
    
    #Oferta e descrição
    valor_ofertado = db.Column(db.Float, nullable=False)
    descricao_pedido = db.Column(db.Text, nullable=False)
    
    #Quando foi criada e quando foi respondida
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_resposta = db.Column(db.DateTime, nullable=True)
    
    #Referência ao serviço solicitado
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    servico = db.relationship('Servico', backref='solicitacoes')

    #Dados do cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    cliente = db.relationship('Usuario', foreign_keys=[cliente_id], backref='minhas_solicitacoes')

    #Dados do prestador
    prestador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    prestador = db.relationship('Usuario', foreign_keys=[prestador_id], backref='solicitacoes_recebidas')

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'valor_ofertado': self.valor_ofertado,
            'descricao_pedido': self.descricao_pedido,
            'data_solicitacao': self.data_solicitacao.isoformat(),
            'servico': {
                'id': self.servico.id,
                'titulo': self.servico.titulo
            },
            'cliente': {
                'id': self.cliente.id,
                'nome': self.cliente.nome,
                'imagem': self.cliente.imagem
            },
            'prestador': self.prestador.nome
        }