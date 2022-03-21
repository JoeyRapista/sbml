"""remaned max

Revision ID: f5e4c1ed6431
Revises: 2d292a4b6321
Create Date: 2022-03-17 11:46:46.336744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5e4c1ed6431'
down_revision = '2d292a4b6321'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('season', sa.Column('max_teams', sa.Integer(), nullable=True))
    op.drop_column('season', 'max_players')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('season', sa.Column('max_players', sa.INTEGER(), nullable=True))
    op.drop_column('season', 'max_teams')
    # ### end Alembic commands ###