const a = require('assert'); const { fmt } = require('../src/currency');
a.strictEqual(fmt(0), '$0.00'); a.strictEqual(fmt(5), '$0.05'); console.log('invariants ok');
