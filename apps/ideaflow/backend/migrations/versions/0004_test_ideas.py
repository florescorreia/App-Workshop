"""Exclude test work from business cohorts; retain removed ideas and attribution."""
from alembic import op
import sqlalchemy as sa
revision='0004'
down_revision='0003'

def upgrade():
    columns={c['name'] for c in sa.inspect(op.get_bind()).get_columns('idea')}
    if 'is_test' not in columns:
        op.add_column('idea',sa.Column('is_test',sa.Boolean(),nullable=False,server_default=sa.text('false')))
        op.add_column('idea',sa.Column('removed_at',sa.DateTime(timezone=True),nullable=True))
        op.add_column('idea',sa.Column('removed_by',sa.String(36),sa.ForeignKey('app_user.id'),nullable=True))
        op.add_column('idea',sa.Column('removal_reason',sa.Text(),nullable=True))
        op.create_check_constraint('removed_only_test','idea','removed_at IS NULL OR is_test')
        op.create_check_constraint('removal_metadata','idea','(removed_at IS NULL AND removed_by IS NULL AND removal_reason IS NULL) OR (removed_at IS NOT NULL AND removed_by IS NOT NULL AND removal_reason IS NOT NULL AND length(trim(removal_reason)) > 0)')

def downgrade():
    raise RuntimeError('Destructive downgrade is unsupported; restore an isolated backup.')
