"""Check repository Markdown links without reading private/generated files."""
import os
import re
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','node_modules','local','backups','artifacts','dist','__pycache__','.pytest_cache'}

def markdown_files(root=ROOT):
    files=[]
    for directory,folders,names in os.walk(root):
        folders[:]=[name for name in folders if name not in EXCLUDED]
        files.extend(Path(directory)/name for name in names if name.endswith('.md'))
    return sorted(files)

def check(root=ROOT):
    errors=[];files=markdown_files(root)
    for path in files:
        text=path.read_text(encoding='utf8')
        # Commands/examples inside fenced code aren't Markdown link targets.
        prose=re.sub(r'^```.*?^```[^\n]*', '', text, flags=re.M|re.S)
        for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)',prose):
            href=href.strip().split(' "',1)[0].strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',href) or href.startswith('#'):continue
            target=unquote(href.split('#',1)[0])
            if not target:continue
            if not (path.parent/target).exists():errors.append(f'{path.relative_to(root)}: missing link {href}')
        if '\ufffd' in text:errors.append(f'{path.relative_to(root)}: invalid replacement character')
    return files,errors

if __name__=='__main__':
    files,errors=check()
    for error in errors:print(error)
    if errors:raise SystemExit(1)
    print(f'Markdown audit: {len(files)} UTF-8 documents; local links resolve; private/generated files excluded.')
