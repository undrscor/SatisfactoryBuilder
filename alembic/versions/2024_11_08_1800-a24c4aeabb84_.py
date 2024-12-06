"""empty message

Revision ID: a24c4aeabb84
Revises: 
Create Date: 2024-11-08 18:00:31.720704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a24c4aeabb84'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('buildings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_buildings')),
    sa.UniqueConstraint('name', name=op.f('uq_buildings_name'))
    )
    op.create_table('materials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_materials')),
    sa.UniqueConstraint('name', name=op.f('uq_materials_name'))
    )
    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_players')),
    sa.UniqueConstraint('name', name=op.f('uq_players_name'))
    )
    op.create_table('recipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('energy', sa.Integer(), nullable=True),
    sa.Column('building_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipes')),
    sa.UniqueConstraint('name', name=op.f('uq_recipes_name'))
    )
    op.create_table('building_materials',
    sa.Column('building_id', sa.Integer(), nullable=False),
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], name=op.f('fk_building_materials_building_id_buildings')),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], name=op.f('fk_building_materials_material_id_materials')),
    sa.PrimaryKeyConstraint('building_id', 'material_id', name='m2m_building_materials')
    )
    op.create_table('inventory_materials',
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.Column('inventory_id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['inventory_id'], ['players.id'], name=op.f('fk_inventory_materials_inventory_id_players')),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], name=op.f('fk_inventory_materials_material_id_materials')),
    sa.PrimaryKeyConstraint('material_id', 'inventory_id', name='m2m_inventory_materials')
    )
    op.create_table('recipe_inputs',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], name=op.f('fk_recipe_inputs_material_id_materials')),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_inputs_recipe_id_recipes')),
    sa.PrimaryKeyConstraint('recipe_id', 'material_id', name='m2m_recipe_inputs')
    )
    op.create_table('recipe_outputs',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], name=op.f('fk_recipe_outputs_material_id_materials')),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name=op.f('fk_recipe_outputs_recipe_id_recipes')),
    sa.PrimaryKeyConstraint('recipe_id', 'material_id', name='m2m_recipe_outputs')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe_outputs')
    op.drop_table('recipe_inputs')
    op.drop_table('inventory_materials')
    op.drop_table('building_materials')
    op.drop_table('recipes')
    op.drop_table('players')
    op.drop_table('materials')
    op.drop_table('buildings')
    # ### end Alembic commands ###