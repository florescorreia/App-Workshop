import os
from alembic import context
from sqlalchemy import create_engine
from app.db import Base
from app import models

with create_engine(os.environ.get('DATABASE_ADMIN_URL', os.environ['DATABASE_URL'])).connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
