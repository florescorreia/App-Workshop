"""Read-only persisted embedding and scoped-secret check; no provider requests."""
import json, os
from pathlib import Path
from domain import Domain

d = Domain()
keys = json.loads(Path(os.environ['PROVIDER_KEYS_FILE']).read_text())
assert set(keys) == {os.environ['EMBEDDING_API_KEY_ENV']}
assert all(isinstance(v, str) and v for v in keys.values())
assert os.environ['EMBEDDING_MODEL'] == 'text-embedding-3-large'
assert os.environ['EMBEDDING_DIMENSIONS'] == '3072'
with d.connect() as db:
    rows = db.execute('SELECT embedding_model, vector_dims(embedding) AS dims, count(*) AS n FROM chunks WHERE embedding IS NOT NULL GROUP BY 1,2').fetchall()
    assert rows and all(r['dims'] == 3072 and r['embedding_model'] == d.embedding_space() for r in rows)
    sources = db.execute("SELECT * FROM records WHERE kind='Source'").fetchall()
    import hashlib
    assert all(hashlib.sha256(d.storage.get(s['body']['hash'])).hexdigest() == s['body']['hash'] for s in sources)
print('Restored tenant: all source hashes, scoped provider secret, model/space and', sum(r['n'] for r in rows), '3072-dimensional vectors passed; no model/network call.')
