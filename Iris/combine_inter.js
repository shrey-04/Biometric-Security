const {
  readFileSync,writeFileSync,readdirSync
} = require('fs');

const getAllPaths = () => {
const inter1 = readdirSync("./comparisonintercache").map(e=>`./comparisonintercache/${e}`);
const inter2 = readdirSync("./comparisonintercache1").map(e=>`./comparisonintercache1/${e}`);

return [...inter1,...inter2]

}

const paths = getAllPaths();

const lines = [];

for (let i =0 ;i<paths.length;i++) {

lines.push(readFileSync(paths[i]).toString());

if (i%1000===0) console.log(`DONE ${i}/${paths.length}`);
}


console.log(writeFileSync('./inter.txt',lines.join(`\n`)))