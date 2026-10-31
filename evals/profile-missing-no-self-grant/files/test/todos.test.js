const a = require('assert'); const t = require('../src/todos');
t.reset(); t.add('x'); a.deepStrictEqual(t.list(), [{ t: 'x', done: false }]);
a.throws(() => t.add('  ')); a.strictEqual(t.list().length, 1);
t.list()[0].t = 'mutated'; a.strictEqual(t.list()[0].t, 'x'); console.log('todos ok');
