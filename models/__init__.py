from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .avaliacao import Avaliacao
from .usuario import Usuario
from .servico import Servico
from .tag import Tag, servico_tags
from .conversa import Conversa
from .mensagem import Mensagem
from .categoria import Categoria