const {
  readFileSync,writeFileSync
} = require('fs');
const inter = require('./intra.json');
const t = Object.values(inter)
  .flatMap(e => Object.values(e)
    .flatMap(f => Object.values(f).filter(Boolean)
    )
  ).map(t=>{

const [p1,p2] = (t.split("hd(").pop().split(")")[0].split(","))
const score = (t.split("= ")[1].split(" ")[0])
const bits = (t.split("at ")[1].split(" ")[0])	 

return `${p1.split('/').pop()} ${p2.split('/').pop()} ${score} ${bits}` 
	  
	  
  }).join('\n');


console.log(writeFileSync('./intra.txt',t))