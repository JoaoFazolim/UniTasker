"""add_default_and_fix_nulls

Revision ID: 2c80e803077a
Revises: a7229aa69c33
Create Date: 2025-12-03 19:18:33.607672

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '2c80e803077a'
down_revision = 'a7229aa69c33'
branch_labels = None
depends_on = None


def upgrade():
 
    op.alter_column('usuario', 'imagem',
               existing_type=sa.VARCHAR(100),
               server_default='user.jpg',
               existing_nullable=True) 
               

    op.alter_column('usuario', 'cargo',
               existing_type=sa.VARCHAR(50),
               server_default='',
               existing_nullable=True)
               

    op.alter_column('usuario', 'localizacao',
               existing_type=sa.VARCHAR(30),
               server_default='',
               existing_nullable=True)
               

    op.execute(
        text("UPDATE usuario SET cargo = '', localizacao = '' WHERE cargo IS NULL OR localizacao IS NULL")
    )
    

    op.execute(
        text("UPDATE usuario SET imagem = 'user.jpg' WHERE imagem IS NULL")
    )

def downgrade():
    op.alter_column('usuario', 'imagem', server_default=None, existing_nullable=True)
    op.alter_column('usuario', 'cargo', server_default=None, existing_nullable=True)
    op.alter_column('usuario', 'localizacao', server_default=None, existing_nullable=True)
