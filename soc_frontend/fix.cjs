const fs = require('fs');
let c = fs.readFileSync('src/components/AeroShards.tsx', 'utf8');
c = c.replace(/\\`/g, '`').replace(/\\\$\{/g, '${');
fs.writeFileSync('src/components/AeroShards.tsx', c);
