"""added ForeinKey

Revision ID: 60791bcee23c
Revises: 8f788fab87c5
Create Date: 2023-12-31 19:49:28.357494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60791bcee23c'
down_revision = '8f788fab87c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('poster_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_posts_poster_id_users'), 'users', ['poster_id'], ['id'])
        batch_op.drop_column('author')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_users_email'), ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_users_email'), type_='unique')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=120), nullable=True))
        batch_op.drop_constraint(batch_op.f('fk_posts_poster_id_users'), type_='foreignkey')
        batch_op.drop_column('poster_id')

    # ### end Alembic commands ###
