"""Shared workspace, user-defined classifications; preserves existing history."""
from alembic import op
import sqlalchemy as sa
import unicodedata

revision = '0002'
down_revision = '0001'

def upgrade():
    connection = op.get_bind()
    # 0001 creates current metadata on a fresh install. Upgrade old installations too.
    inspector = sa.inspect(connection)
    for constraint in inspector.get_check_constraints('app_user'):
        if 'role' in constraint['sqltext']:
            op.drop_constraint(constraint['name'], 'app_user', type_='check')
    op.execute("UPDATE app_user SET role='User' WHERE role<>'Admin'")
    op.create_check_constraint('user_role', 'app_user', "role IN ('User','Admin')")
    for table in ('site', 'category'):
        columns = {c['name'] for c in sa.inspect(connection).get_columns(table)}
        if 'label_key' not in columns:
            op.add_column(table, sa.Column('label_key', sa.String(120), nullable=True))
            op.add_column(table, sa.Column('record_version', sa.Integer(), nullable=False, server_default='1'))
            op.add_column(table, sa.Column('merged_into', sa.String(80), nullable=True))
            rows = connection.execute(sa.text(f'SELECT id,label FROM {table}')).all()
            for row in rows:
                key = ' '.join(unicodedata.normalize('NFKC', row.label).casefold().split())
                connection.execute(sa.text(f'UPDATE {table} SET label_key=:key WHERE id=:id'), {'key': key, 'id': row.id})
            op.alter_column(table, 'label_key', nullable=False)
            op.create_unique_constraint(table+'_label_key_key', table, ['label_key'])
    op.alter_column('idea', 'site_id', nullable=True)
    op.alter_column('idea', 'category_id', nullable=True)

def downgrade():
    raise RuntimeError('Restore a backup in an isolated database; destructive downgrade is unsupported.')
