const fs=require('fs');exports.load=()=>fs.readFileSync('tests/fixtures/patients.csv','utf8').split('\n').slice(1);
