"""New Migration

Revision ID: e5f1f28fa60e
Revises: 
Create Date: 2024-06-27 15:28:25.554887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e5f1f28fa60e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('doctors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('specialization', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_doctors_name'), 'doctors', ['name'], unique=False)
    op.create_index(op.f('ix_doctors_phone_number'), 'doctors', ['phone_number'], unique=True)
    op.create_table('patients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('disease', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_disease'), 'patients', ['disease'], unique=False)
    op.create_index(op.f('ix_patients_email'), 'patients', ['email'], unique=True)
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    op.create_index(op.f('ix_patients_name'), 'patients', ['name'], unique=False)
    op.create_index(op.f('ix_patients_phone_number'), 'patients', ['phone_number'], unique=True)
    op.drop_table('posts')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('published', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='posts_pkey'),
    sa.UniqueConstraint('title', name='posts_title_key')
    )
    op.drop_index(op.f('ix_patients_phone_number'), table_name='patients')
    op.drop_index(op.f('ix_patients_name'), table_name='patients')
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_index(op.f('ix_patients_email'), table_name='patients')
    op.drop_index(op.f('ix_patients_disease'), table_name='patients')
    op.drop_table('patients')
    op.drop_index(op.f('ix_doctors_phone_number'), table_name='doctors')
    op.drop_index(op.f('ix_doctors_name'), table_name='doctors')
    op.drop_table('doctors')
    # ### end Alembic commands ###
