"""Initial migration - Create users and expenses tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-20

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    
    # Create expense category enum
    expense_category = sa.Enum(
        'FOOD', 'TRANSPORT', 'UTILITIES', 'ENTERTAINMENT', 
        'HEALTH', 'SHOPPING', 'OTHER',
        name='expensecategory'
    )
    expense_category.create(op.get_bind())
    
    # Create expense table
    op.create_table(
        'expense',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('merchant', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('category', expense_category, nullable=False),
        sa.Column('is_subscription', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('receipt_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expense_user_id'), 'expense', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_expense_user_id'), table_name='expense')
    op.drop_table('expense')
    op.execute('DROP TYPE expensecategory')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
