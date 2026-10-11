# Engagement contract

An engagement owns an opaque 24-character hexadecimal ID, membership, PostgreSQL server, graph, artifact bytes and runtime workspaces. The name is display metadata, never an authorization key. A consultant must explicitly switch engagement; combined search/copy is absent.

Version references have `{id, version}` and evidence additionally carries a locator. Sources preserve original filename/URL, hash, size, retrieval metadata and access limitations. Unknown provenance stays unknown. Registry updates require an idempotency key and optional exact prior version. Human acceptance is an immutable review record over exact deliverable versions.

Initial ontology is `schemas/ontology/v1.yaml`. Agents persist proposals; human owners approve before typed relation ingestion. Approved versions are canonical in PostgreSQL and replayed into the dedicated tenant ontology Git volume. Endpoint types and required properties are validated before writes. Explorer filters use approved relation names. Actual analytical code and commits reside on runtime volumes; independent reviewer work has separate workspace/home.
