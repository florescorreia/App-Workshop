CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
CREATE TABLE IF NOT EXISTS app_user (
 id UUID PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK (role IN ('Admin','User'))
);
CREATE TABLE IF NOT EXISTS app_session (
 token_hash TEXT PRIMARY KEY, user_id UUID NOT NULL REFERENCES app_user(id),
 csrf TEXT NOT NULL, expires_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS note (
 id UUID PRIMARY KEY, body TEXT NOT NULL CHECK (length(body) BETWEEN 1 AND 2000),
 actor_id UUID NOT NULL REFERENCES app_user(id), record_version INTEGER NOT NULL DEFAULT 1,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS note_event (
 id UUID PRIMARY KEY, note_id UUID NOT NULL REFERENCES note(id),
 actor_id UUID NOT NULL REFERENCES app_user(id), activity TEXT NOT NULL,
 occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(), changes JSONB NOT NULL
);
CREATE OR REPLACE FUNCTION protect_note_event() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'Note events are append-only'; END $$;
DROP TRIGGER IF EXISTS note_event_immutable ON note_event;
CREATE TRIGGER note_event_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON note_event
FOR EACH STATEMENT EXECUTE FUNCTION protect_note_event();
INSERT INTO schema_version(version) VALUES(1) ON CONFLICT DO NOTHING;
