"""added maxplayers for season

Revision ID: 2d292a4b6321
Revises: efe89ece4199
Create Date: 2022-03-17 11:43:07.192119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d292a4b6321'
down_revision = 'efe89ece4199'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('season', sa.Column('max_players', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('season', 'max_players')
    # ### end Alembic commands ###
