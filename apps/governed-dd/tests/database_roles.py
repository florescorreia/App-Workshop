from domain import Domain
import psycopg
d=Domain()
with d.connect() as db:
 assert not db.execute("SELECT has_table_privilege(current_user,'records','UPDATE') AS allowed").fetchone()['allowed']
 assert not db.execute("SELECT has_table_privilege(current_user,'records','DELETE') AS allowed").fetchone()['allowed']
 assert not db.execute("SELECT has_schema_privilege(current_user,'public','CREATE') AS allowed").fetchone()['allowed']
 assert db.execute("SELECT has_table_privilege(current_user,'audit','INSERT') AS allowed").fetchone()['allowed']
try:
 with d.connect() as db:db.execute('UPDATE records SET status=status WHERE false')
except psycopg.errors.InsufficientPrivilege:pass
else:raise AssertionError('Canonical update permitted')
print('Database least privilege and canonical immutability permissions passed.')
