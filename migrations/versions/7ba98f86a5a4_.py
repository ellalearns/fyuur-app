"""empty message

Revision ID: 7ba98f86a5a4
Revises: f4d19159713d
Create Date: 2022-08-04 10:54:03.146072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ba98f86a5a4'
down_revision = 'f4d19159713d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=500), nullable=False))
    op.add_column('Venue', sa.Column('looking_for_talent', sa.Boolean(), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=False))
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('Venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('Venue', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Venue', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'looking_for_talent')
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
