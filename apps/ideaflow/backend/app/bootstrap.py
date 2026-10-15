import os
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text, select
from psycopg import sql
from argon2 import PasswordHasher
from .models import User
from .db import SessionLocal

def bootstrap():
    command.upgrade(Config('alembic.ini'), 'head')
    admin_engine = create_engine(os.environ['DATABASE_ADMIN_URL'])
    with admin_engine.begin() as conn:
        raw = conn.connection.driver_connection
        with raw.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname='ideaflow_app'")
            if not cur.fetchone():
                cur.execute(sql.SQL('CREATE ROLE ideaflow_app LOGIN PASSWORD {}').format(sql.Literal(os.environ['APP_DB_PASSWORD'])))
            cur.execute('GRANT USAGE ON SCHEMA public TO ideaflow_app')
            cur.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ideaflow_app')
            cur.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ideaflow_app')
            cur.execute('REVOKE UPDATE, DELETE, TRUNCATE ON idea_event FROM ideaflow_app')
            cur.execute('REVOKE UPDATE, DELETE, TRUNCATE ON account_event FROM ideaflow_app')
            cur.execute('REVOKE UPDATE, DELETE, TRUNCATE ON vave_program_event FROM ideaflow_app')
            cur.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
    with SessionLocal.begin() as db:
        if not db.scalar(select(User).where(User.email == os.environ['ADMIN_EMAIL'].lower())):
            db.add(User(name='Local Administrator', email=os.environ['ADMIN_EMAIL'].lower(), role='Admin', password_hash=PasswordHasher().hash(os.environ['ADMIN_PASSWORD'])))

if __name__ == '__main__': bootstrap()
