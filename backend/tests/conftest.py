import os, uuid
import pytest
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from app.db import get_db
from app.main import app
from app.models import User, Site, Category
from app.auth import hasher

@pytest.fixture(scope='session')
def test_engine():
    """A new isolated database; never delete or clear live domain tables."""
    admin=create_engine(os.environ['DATABASE_ADMIN_URL'],isolation_level='AUTOCOMMIT')
    name='ideaflow_test_'+uuid.uuid4().hex
    with admin.connect() as c:c.execute(text(f'CREATE DATABASE {name}'))
    admin_url=admin.url.set(database=name);app_url=create_engine(os.environ['DATABASE_URL']).url.set(database=name)
    original=os.environ['DATABASE_ADMIN_URL'];os.environ['DATABASE_ADMIN_URL']=admin_url.render_as_string(hide_password=False)
    try:
        command.upgrade(Config('alembic.ini'),'head')
        owner=create_engine(admin_url)
        with owner.begin() as c:
            c.execute(text('GRANT USAGE ON SCHEMA public TO ideaflow_app'))
            c.execute(text('GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO ideaflow_app'))
            c.execute(text('GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO ideaflow_app'))
            c.execute(text('REVOKE UPDATE,DELETE,TRUNCATE ON idea_event FROM ideaflow_app'))
        engine=create_engine(app_url)
        with sessionmaker(engine).begin() as db:
            for role in ('Admin','Manager','Finance','Contributor'):
                db.add(User(name='Test '+role,email=role.lower()+'@test.invalid',role=role,password_hash=hasher.hash('test-only-password-123')))
            for label,unit in [('Tampa','Assembly'),('Atlanta','Distribution'),('Dallas','Assembly')]:db.add(Site(id=label,label=label,business_unit=unit))
            for label in ['Procurement','Freight','Inventory','Energy','Scrap/Quality','Productivity','Working Capital']:db.add(Category(id=label,label=label))
        yield engine
        engine.dispose();owner.dispose()
    finally:
        os.environ['DATABASE_ADMIN_URL']=original
        with admin.connect() as c:c.execute(text(f'DROP DATABASE {name} WITH (FORCE)'))
        admin.dispose()

@pytest.fixture
def db(test_engine):
    with sessionmaker(test_engine,expire_on_commit=False)() as s:
        yield s
        s.rollback()

@pytest.fixture
def clients(test_engine):
    def override():
        with sessionmaker(test_engine,expire_on_commit=False)() as db:
            try:yield db;db.commit()
            except Exception:db.rollback();raise
    app.dependency_overrides[get_db]=override
    result={}
    for role in ('Admin','Manager','Finance','Contributor'):
        c=TestClient(app)
        response=c.post('/api/v1/session/login',json={'email':role.lower()+'@test.invalid','password':'test-only-password-123'})
        assert response.status_code==200
        c.headers['X-CSRF-Token']=response.json()['csrf'];result[role]=c
    yield result
    for c in result.values():c.close()
    app.dependency_overrides.clear()
