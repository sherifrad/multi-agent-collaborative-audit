const a=require('assert');const t=require('../src/todos');t.add('x');a.strictEqual(t.list().length,1);console.log('ok');
