CREATE TABLE IF NOT EXISTS schema_versions(version integer PRIMARY KEY, installed_at timestamptz NOT NULL DEFAULT now());
INSERT INTO schema_versions(version) VALUES(1) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS records (
 id uuid NOT NULL, version integer NOT NULL, tenant text NOT NULL,
 kind text NOT NULL, status text NOT NULL DEFAULT 'draft', body jsonb NOT NULL,
 actor text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(id,version)
);
CREATE TABLE IF NOT EXISTS requests (
 key text PRIMARY KEY, digest text NOT NULL, id uuid NOT NULL, version integer NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
 sequence bigserial PRIMARY KEY, actor text NOT NULL, operation text NOT NULL,
 id uuid, version integer, correlation uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS outbox (
 sequence bigserial PRIMARY KEY, id uuid NOT NULL, version integer NOT NULL,
 state text NOT NULL DEFAULT 'pending', attempts integer NOT NULL DEFAULT 0,
 error text, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(id,version)
);
CREATE TABLE IF NOT EXISTS chunks (
 id bigserial PRIMARY KEY, source_id uuid NOT NULL, source_version integer NOT NULL,
 locator text NOT NULL, text text NOT NULL, hash text NOT NULL,
 extractor text NOT NULL, configuration jsonb NOT NULL, embedding_model text,
 embedding vector, UNIQUE(source_id,source_version,locator,hash),
 FOREIGN KEY(source_id,source_version) REFERENCES records(id,version)
);
CREATE INDEX IF NOT EXISTS chunks_bm25 ON chunks USING bm25(id,text) WITH(key_field='id');
CREATE TABLE IF NOT EXISTS jobs (
 id uuid PRIMARY KEY, source_id uuid NOT NULL, version integer NOT NULL,
 status text NOT NULL DEFAULT 'pending', progress integer NOT NULL DEFAULT 0,
 error text, cancelled boolean NOT NULL DEFAULT false, started_at timestamptz,
 updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(source_id,version)
);
CREATE TABLE IF NOT EXISTS ontology_versions (
 version integer PRIMARY KEY, document jsonb NOT NULL, actor text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
