const {
  spawn,exec
} = require('child_process')
const {
  readdirSync,readFileSync
} = require('fs')

function run(command) {
  return new Promise((resolve,reject)=>{
    return exec(command, function(err, stdout, stderr){
      if (err) reject(err);
      if (stderr) reject(err);
      else resolve(true)
    });
    const proc = spawn(command);
    //proc.stdout.on('data', function(data) { console.log("stdout: " + data); });
    //proc.stderr.on('data', function(data) { console.log("stderr: " + data); });
    proc.on('exit', function(code) {
      if (typeof code === "number" && code>0) {
        return reject(new Error(command));
      }
      return resolve(true);
    });
  })
}
const getNewCommands = () => {
return JSON.parse(readFileSync('./cachenewcommands').toString());
const commands = JSON.parse(readFileSync('./commands.json').toString());
console.log(`START NEWCOMMAND PROCES`)
const alreadyDone = new Set(readdirSync('./comparisonintercache'));
const newCommands = commands.map(e=>{
  const [_,__,file1,file2]=e.split(' ');
  const key = `${file1.split('/').slice(1).join()}_${file2.split('/').slice(1).join()}.txt`;
  if (alreadyDone.has(key)) return false;
  /*if (existsSync(`./comparisonintercache/${file1.split('/').slice(1).join()}_${file2.split('/').slice(1).join()}.txt`)) {
    throw new Error('what!')
  };*/
  return String.raw`C:\Users\monua\Desktop\bio_mat\biometricsfriday\images\USITv3.0.0\bin\hd.exe -i ${file1} ${file2} -o ./comparisonintercache1/${file1.split('/').slice(1).join()}_${file2.split('/').slice(1).join()}.txt`
}).filter(Boolean);
console.log(`END NEWCOMMAND PROCES`)
return newCommands;

};
const newCommands = getNewCommands().map(e=>e.split('comparisonintercache').join('comparisonintercache1'));
const chunks = require('lodash').chunk(newCommands,parseInt(newCommands.length/30));
async function main(){
  console.log(`INP :${newCommands.length}`)
  const handleChunk = async (chunk,index) =>{
    for (let i = 0; i < chunk.length; i++) {
      console.log(`DONING INDEX:(${index+1}),${i+1}/${chunk.length}`)
      await run(chunk[i]);
      console.log(`DONE INDEX:(${index+1}),${i+1}/${chunk.length}`)
    }
  }

  return Promise.all(chunks.map(handleChunk));

}
main().then(()=>  console.log(`DONE ALL`)).catch(console.error)
setInterval(console.clear,10*1000)
