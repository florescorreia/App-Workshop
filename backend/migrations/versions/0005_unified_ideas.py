"""Unify all visible ideas; retain legacy flags/events without rewriting records."""
from alembic import op
import sqlalchemy as sa

revision='0005'
down_revision='0004'

def upgrade():
    constraints={c['name'] for c in sa.inspect(op.get_bind()).get_check_constraints('idea')}
    if 'removed_only_test' in constraints:
        op.drop_constraint('removed_only_test','idea',type_='check')

def downgrade():
    raise RuntimeError('Restoring the old removal restriction is unsupported; verify an isolated backup instead.')
