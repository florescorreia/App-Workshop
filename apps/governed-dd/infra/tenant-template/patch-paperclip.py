"""Minimal pinned Codex adapter change: never serialize server secrets into SSH runs."""
from pathlib import Path
p=Path('/app/packages/adapters/codex-local/src/server/execute.ts')
text=p.read_text()
old='Object.entries({ ...process.env, ...env }).filter('
new='Object.entries({ ...Object.fromEntries(Object.entries(process.env).filter(([key]) => ["PATH", "LANG", "LC_ALL", "TMPDIR"].includes(key))), ...env }).filter('
if text.count(old)!=1:raise RuntimeError('Pinned adapter changed; review credential filtering before build')
p.write_text(text.replace(old,new))
