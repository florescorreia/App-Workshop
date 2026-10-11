CREATE TABLE IF NOT EXISTS tenants(id text PRIMARY KEY, name text NOT NULL, active boolean NOT NULL DEFAULT false);
CREATE TABLE IF NOT EXISTS memberships(subject text NOT NULL, tenant text NOT NULL REFERENCES tenants(id), role text NOT NULL CHECK(role IN ('owner','analyst','reviewer','viewer')), PRIMARY KEY(subject,tenant));
CREATE TABLE IF NOT EXISTS sessions(id text PRIMARY KEY, subject text NOT NULL, csrf text NOT NULL, expires_at timestamptz NOT NULL, id_token text NOT NULL);
CREATE TABLE IF NOT EXISTS login_states(id text PRIMARY KEY, verifier text NOT NULL, nonce text NOT NULL, expires_at timestamptz NOT NULL);
CREATE TABLE IF NOT EXISTS control_audit(sequence bigserial PRIMARY KEY, subject text NOT NULL, operation text NOT NULL, tenant text, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS component_tickets(id text PRIMARY KEY, session_id text NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, tenant text NOT NULL REFERENCES tenants(id), component text NOT NULL, expires_at timestamptz NOT NULL);
