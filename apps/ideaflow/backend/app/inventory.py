import importlib.metadata, json
def main():
    rows=[]
    for dist in sorted(importlib.metadata.distributions(),key=lambda d:d.metadata['Name'].lower()):
        rows.append({'name':dist.metadata['Name'],'version':dist.version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License') or '; '.join(c for c in dist.metadata.get_all('Classifier',[]) if 'License' in c)})
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
