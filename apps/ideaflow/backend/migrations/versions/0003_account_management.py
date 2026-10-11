"""Retire historical accounts without removing attribution; audit account actions."""
from alembic import op
import sqlalchemy as sa
from app.models import AccountEvent
revision='0003'
down_revision='0002'

def upgrade():
    if 'deleted_at' not in {c['name'] for c in sa.inspect(op.get_bind()).get_columns('app_user')}:
        op.add_column('app_user',sa.Column('deleted_at',sa.DateTime(timezone=True),nullable=True))
    AccountEvent.__table__.create(op.get_bind(),checkfirst=True)
    op.execute('CREATE TRIGGER immutable_account_events BEFORE UPDATE OR DELETE ON account_event FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation()')

def downgrade():
    raise RuntimeError('Destructive downgrade is unsupported; restore an isolated backup.')
