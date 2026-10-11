import os, uuid
from pathlib import Path
import psycopg
from argon2 import PasswordHasher

def bootstrap():
    with psycopg.connect(os.environ['DATABASE_URL']) as db:
        db.execute((Path(__file__).parent/'migrations'/'001.sql').read_text())
        if not db.execute('SELECT 1 FROM app_user WHERE email=%s',(os.environ['ADMIN_EMAIL'].lower(),)).fetchone():
            db.execute('INSERT INTO app_user(id,email,password_hash,role) VALUES(%s,%s,%s,%s)',(uuid.uuid4(),os.environ['ADMIN_EMAIL'].lower(),PasswordHasher().hash(os.environ['ADMIN_PASSWORD']),'Admin'))

if __name__=='__main__':bootstrap()
