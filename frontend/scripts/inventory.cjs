const fs=require('fs');
const lock=JSON.parse(fs.readFileSync('package-lock.json'));
console.log(JSON.stringify(Object.entries(lock.packages).filter(([path])=>path).map(([path,p])=>({name:path.split('node_modules/').at(-1),version:p.version,license:p.license||'See upstream LICENSE',dev:!!p.dev})),null,2));
